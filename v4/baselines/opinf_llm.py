"""
baselines/opinf_llm.py — Operator Inference + LLM (OpInf-LLM) baseline.

Reference: "OpInf-LLM: Parametric PDE Solving with LLMs via Operator Inference"
           arxiv.org/abs/2602.01493

Two-phase approach
------------------
Phase 1 — Offline (fit):
  1. Collect snapshot trajectories at training parameter values.
  2. Compute a shared POD basis Φ ∈ ℝ^(n × r) via truncated SVD.
  3. Project each trajectory to the reduced space: r̂ = Φᵀ u.
  4. Estimate time derivatives via 2nd-order finite differences.
  5. Solve the least-squares system to learn operators A, H, c:
         dr/dt ≈ A r + H (r ⊗ r) + c
  6. (Optional LLM step) ask an LLM which terms to include, then re-fit.

Phase 2 — Online (predict):
  1. If predicting at a new parameter value, extrapolate operators via
     polynomial regression on the training parameter values.
  2. Project the initial condition onto the reduced basis.
  3. Integrate the reduced ODE with scipy RK45.
  4. Reconstruct the full field: u ≈ Φ r.

Usage
-----
    from baselines.opinf_llm import OpInfLLMBaseline
    from data.base import get_data_source

    src = get_data_source("pdebench_2d_rd")
    model = OpInfLLMBaseline(r=20, use_quadratic=True)

    # Fit on 4 training trajectories
    trajectories, meta = src.load_training_trajectories(sample_indices=[0,1,2,3])
    model.fit(trajectories, metadata=meta)

    # Predict on sample 4
    ic   = src.load_ic(sample_idx=4)
    gt   = src.load_snapshots(sample_idx=4)
    pred = model.predict(ic, t_eval=sorted(gt.keys()))
"""

from __future__ import annotations

import json
import logging
import time
import tracemalloc
import warnings
from typing import Optional

import numpy as np
from scipy.integrate import solve_ivp
from scipy.linalg import lstsq

from data.base import DatasetMetadata

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helper: Kronecker (quadratic) feature
# ---------------------------------------------------------------------------

def _kron_quadratic(r: np.ndarray) -> np.ndarray:
    """
    Unique quadratic feature vector for a state r of length n_r.
    Uses only the upper-triangle of r ⊗ r to avoid redundancy.
    Length = n_r*(n_r+1)//2.
    """
    n = len(r)
    out = np.empty(n * (n + 1) // 2)
    k = 0
    for i in range(n):
        for j in range(i, n):
            out[k] = r[i] * r[j]
            k += 1
    return out


def _kron_quadratic_batch(R: np.ndarray) -> np.ndarray:
    """Vectorised version for R of shape (T, n_r)."""
    T, n = R.shape
    m = n * (n + 1) // 2
    out = np.empty((T, m))
    k = 0
    for i in range(n):
        for j in range(i, n):
            out[:, k] = R[:, i] * R[:, j]
            k += 1
    return out


# ---------------------------------------------------------------------------
# OpInf-LLM
# ---------------------------------------------------------------------------

class OpInfLLMBaseline:
    """
    Operator Inference + LLM baseline.

    Parameters
    ----------
    r : int
        Reduced dimension (POD modes to retain) per state variable.
    use_quadratic : bool
        Include quadratic (H) operator in addition to linear (A) and constant (c).
    use_llm : bool
        If True, query an LLM to decide which operator terms to include.
        Requires Ollama running with cfg.validation_model.
    llm_model : str
        Ollama model name for the LLM operator selection step.
    regularisation : float
        Tikhonov regularisation strength for the least-squares fit.
    integrate_method : str
        scipy solve_ivp method ('RK45', 'Radau', 'BDF').
    """

    def __init__(
        self,
        r: int = 20,
        use_quadratic: bool = True,
        use_llm: bool = False,
        llm_model: str = "qwen3:8b",
        regularisation: float = 1e-6,
        integrate_method: str = "RK45",
    ):
        self.r = r
        self.use_quadratic = use_quadratic
        self.use_llm = use_llm
        self.llm_model = llm_model
        self.regularisation = regularisation
        self.integrate_method = integrate_method

        # Fitted objects (set after fit())
        self.basis_: Optional[dict[str, np.ndarray]] = None   # {var: Φ (n, r)}
        self.A_: Optional[dict[str, np.ndarray]] = None        # linear operators
        self.H_: Optional[dict[str, np.ndarray]] = None        # quadratic operators
        self.c_: Optional[dict[str, np.ndarray]] = None        # constant bias
        self.var_names_: Optional[list[str]] = None
        self.metadata_: Optional[DatasetMetadata] = None

        # Performance
        self.fit_time_s_: float = 0.0
        self.fit_mem_mb_: float = 0.0
        self.n_train_snaps_: int = 0

    # ------------------------------------------------------------------
    # Phase 1 — Offline: fit
    # ------------------------------------------------------------------

    def fit(
        self,
        trajectories: list[dict[float, dict[str, np.ndarray]]],
        metadata: DatasetMetadata,
        training_params: Optional[list[float]] = None,
    ) -> "OpInfLLMBaseline":
        """
        Fit the OpInf ROM from training trajectories.

        trajectories : list of {t: {var: array}} dicts, one per sample.
        metadata     : DatasetMetadata for the dataset.
        """
        self.metadata_ = metadata
        self.var_names_ = metadata.var_names

        tracemalloc.start()
        t0 = time.perf_counter()

        # Optional LLM step: select operator terms
        if self.use_llm:
            terms = self._llm_select_terms(metadata)
            self.use_quadratic = terms.get("quadratic", self.use_quadratic)
            logger.info("LLM selected terms: %s", terms)

        # Aggregate all snapshots across trajectories
        all_snaps: dict[str, list[np.ndarray]] = {v: [] for v in self.var_names_}
        for traj in trajectories:
            for t in sorted(traj.keys()):
                for var in self.var_names_:
                    all_snaps[var].append(traj[t][var].ravel())

        self.n_train_snaps_ = len(list(all_snaps.values())[0])

        # Compute POD basis per variable
        self.basis_ = {}
        for var in self.var_names_:
            X = np.stack(all_snaps[var], axis=1)  # (n_spatial, n_snaps)
            U, s, _ = np.linalg.svd(X, full_matrices=False)
            energy = np.cumsum(s ** 2) / np.sum(s ** 2)
            r_actual = min(self.r, len(s))
            logger.info(
                "  POD [%s]: r=%d retains %.4f%% energy",
                var, r_actual, energy[r_actual - 1] * 100,
            )
            self.basis_[var] = U[:, :r_actual]

        # Learn operators per variable
        self.A_ = {}
        self.H_ = {}
        self.c_ = {}

        for var in self.var_names_:
            Φ = self.basis_[var]
            r = Φ.shape[1]

            # Build reduced trajectories and time derivatives
            R_list, dRdt_list = [], []
            for traj in trajectories:
                times = sorted(traj.keys())
                R = np.stack([Φ.T @ traj[t][var].ravel() for t in times])  # (T, r)
                # 2nd-order finite differences for time derivatives
                dt_arr = np.diff(times)
                dR = np.gradient(R, np.mean(dt_arr), axis=0)
                R_list.append(R)
                dRdt_list.append(dR)

            R_all    = np.concatenate(R_list,    axis=0)  # (T_total, r)
            dRdt_all = np.concatenate(dRdt_list, axis=0)  # (T_total, r)

            # Build regression matrix [r, r⊗r, 1]
            cols = [R_all]
            if self.use_quadratic:
                cols.append(_kron_quadratic_batch(R_all))
            cols.append(np.ones((len(R_all), 1)))
            D = np.concatenate(cols, axis=1)  # (T_total, n_terms)

            # Tikhonov regularised least squares: min ‖D O - dR/dt‖ + λ‖O‖
            n_terms = D.shape[1]
            I = np.eye(n_terms) * self.regularisation
            O, _, _, _ = lstsq(D.T @ D + I, D.T @ dRdt_all)  # (n_terms, r)

            # Unpack operators
            self.A_[var] = O[:r, :].T                # (r, r)
            idx = r
            if self.use_quadratic:
                n_quad = r * (r + 1) // 2
                self.H_[var] = O[idx: idx + n_quad, :].T  # (r, n_quad)
                idx += n_quad
            else:
                self.H_[var] = None
            self.c_[var] = O[idx:, :].T.squeeze()    # (r,)

        self.fit_time_s_ = time.perf_counter() - t0
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        self.fit_mem_mb_ = peak / 1e6

        logger.info(
            "OpInf fit complete: %.2fs, %.1f MB, %d training snapshots",
            self.fit_time_s_, self.fit_mem_mb_, self.n_train_snaps_,
        )
        return self

    # ------------------------------------------------------------------
    # Phase 2 — Online: predict
    # ------------------------------------------------------------------

    def predict(
        self,
        ic: dict[str, np.ndarray],
        t_eval: list[float],
        rtol: float = 1e-6,
        atol: float = 1e-9,
    ) -> dict[float, dict[str, np.ndarray]]:
        """
        Predict solution at times t_eval from initial condition ic.

        ic     : {var: (H, W) or (N,) array}
        t_eval : list of target times (must be >= 0)

        Returns {t: {var: array of shape spatial_shape}}
        """
        if self.basis_ is None:
            raise RuntimeError("Call fit() before predict().")

        t_span = (min(t_eval), max(t_eval))
        predictions = {t: {} for t in t_eval}

        for var in self.var_names_:
            Φ = self.basis_[var]
            A = self.A_[var]
            H = self.H_[var]
            c = self.c_[var]
            r0 = Φ.T @ ic[var].ravel()

            def rhs(t, r):
                dr = A @ r + c
                if H is not None:
                    dr += H @ _kron_quadratic(r)
                return dr

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                sol = solve_ivp(
                    rhs,
                    t_span,
                    r0,
                    method=self.integrate_method,
                    t_eval=t_eval,
                    rtol=rtol,
                    atol=atol,
                    dense_output=False,
                )

            spatial_shape = ic[var].shape
            for i, t in enumerate(sol.t):
                t_key = round(float(t), 6)
                if t_key in predictions:
                    u_full = Φ @ sol.y[:, i]
                    u_full = np.clip(u_full, 0.0, 1.0)
                    predictions[t_key][var] = u_full.reshape(spatial_shape)

        return predictions

    # ------------------------------------------------------------------
    # LLM operator term selection
    # ------------------------------------------------------------------

    def _llm_select_terms(self, metadata: DatasetMetadata) -> dict:
        """
        Query LLM to decide which operator terms to include in the OpInf ROM.
        Returns {"linear": bool, "quadratic": bool, "constant": bool}.
        """
        prompt = f"""
You are an expert in reduced-order modelling and operator inference.

Given the following PDE metadata, decide which operator terms should be included
in the Operator Inference (OpInf) reduced-order model:
  dr/dt = A*r  [linear]
        + H*(r⊗r)  [quadratic]
        + c  [constant bias]

Dataset: {metadata.name}
Variables: {metadata.var_names}
Model parameters: {json.dumps(metadata.params)}
PDE type: {metadata.n_vars}-variable reaction-diffusion

Respond with ONLY this JSON (no markdown, no explanation):
{{"linear": true, "quadratic": true, "constant": true}}

Set "quadratic" to false only if the PDE is purely linear.
Set "constant" to false only if there is no forcing/bias term.
"""
        try:
            from ollama import chat
            resp = chat(
                model=self.llm_model,
                messages=[{"role": "user", "content": prompt}],
            )
            text = resp.message.content.strip().strip("```json").strip("```").strip()
            return json.loads(text)
        except Exception as e:
            logger.warning("LLM term selection failed (%s) — using defaults.", e)
            return {"linear": True, "quadratic": self.use_quadratic, "constant": True}

    # ------------------------------------------------------------------
    # Parametric operator extrapolation (for unseen parameter values)
    # ------------------------------------------------------------------

    def extrapolate_operators(
        self,
        training_params: list[float],
        target_param: float,
        trained_models: list["OpInfLLMBaseline"],
        poly_degree: int = 2,
    ) -> "OpInfLLMBaseline":
        """
        Given OpInf models trained at each value in training_params,
        fit a polynomial in parameter space and evaluate at target_param.

        Returns a new OpInfLLMBaseline with extrapolated operators.
        This implements the parametric extension from the OpInf-LLM paper.
        """
        new_model = OpInfLLMBaseline(
            r=self.r,
            use_quadratic=self.use_quadratic,
            regularisation=self.regularisation,
            integrate_method=self.integrate_method,
        )
        new_model.basis_ = self.basis_
        new_model.var_names_ = self.var_names_
        new_model.metadata_ = self.metadata_
        new_model.A_ = {}
        new_model.H_ = {}
        new_model.c_ = {}

        xi = np.array(training_params)
        xi_tgt = np.array([target_param])

        for var in self.var_names_:
            A_vals = np.stack([m.A_[var] for m in trained_models])   # (n_params, r, r)
            c_vals = np.stack([m.c_[var] for m in trained_models])   # (n_params, r)

            # Fit polynomial per entry and evaluate at target_param
            A_new = np.zeros_like(A_vals[0])
            c_new = np.zeros_like(c_vals[0])

            for i in range(A_vals.shape[1]):
                for j in range(A_vals.shape[2]):
                    coeffs = np.polyfit(xi, A_vals[:, i, j], deg=poly_degree)
                    A_new[i, j] = np.polyval(coeffs, target_param)

            for i in range(c_vals.shape[1]):
                coeffs = np.polyfit(xi, c_vals[:, i], deg=poly_degree)
                c_new[i] = np.polyval(coeffs, target_param)

            new_model.A_[var] = A_new
            new_model.c_[var] = c_new

            if self.use_quadratic and self.H_[var] is not None:
                H_vals = np.stack([m.H_[var] for m in trained_models])
                H_new = np.zeros_like(H_vals[0])
                for i in range(H_vals.shape[1]):
                    for j in range(H_vals.shape[2]):
                        coeffs = np.polyfit(xi, H_vals[:, i, j], deg=poly_degree)
                        H_new[i, j] = np.polyval(coeffs, target_param)
                new_model.H_[var] = H_new
            else:
                new_model.H_[var] = None

        return new_model
