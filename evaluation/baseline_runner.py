"""
baseline_runner.py — Reference Python solvers for LLM-direct and CodePDE baselines.

These are canonical, validated implementations of the FK and AP models used as:
  1. The "LLM-direct" baseline (pure NumPy, no LLM involved at runtime)
  2. Reference solvers for Aliev-Panfilov ground truth (Exp 4)
  3. Pseudo-ground truth for debugging

Usage:
    from baseline_runner import FentonKarmaSolver, AlievPanfilovSolver, load_ground_truth
    solver = FentonKarmaSolver()
    u, v, w = solver.run(ic_u, ic_v, ic_w, t_start=0, t_end=100)
"""

import numpy as np
import tracemalloc
import time
from typing import Tuple, Optional

# ---------------------------------------------------------------------------
# Ground truth data loader
# ---------------------------------------------------------------------------

GT_DATA_DIR = "../baselines models/fk_data/tau_d_0.5714"
GT_SNAPSHOTS = [831.25, 841.25, 851.25, 861.25, 871.25,
                881.25, 891.25, 901.25, 911.25, 921.25, 931.25]


def load_ground_truth(tau_d: float = 0.5714) -> dict:
    """
    Load ground truth data from the fk_data directory.

    Returns:
        {
          "ic":   {"u": (512,512), "v": (512,512), "w": (512,512)},
          "snapshots": {T: {"u": ..., "v": ..., "w": ...}},
          "tau_d": float,
        }
    """
    import os

    data_dir = GT_DATA_DIR
    result = {"tau_d": tau_d, "ic": None, "snapshots": {}}

    # Load initial conditions
    ic_path = os.path.join(data_dir, "IC.csv")
    if os.path.exists(ic_path):
        ic_flat = np.loadtxt(ic_path, delimiter=",")
        # Shape: (512*512, 3+) → (512, 512)
        n = 512
        result["ic"] = {
            "u": ic_flat[:, 0].reshape(n, n),
            "v": ic_flat[:, 1].reshape(n, n),
            "w": ic_flat[:, 2].reshape(n, n),
        }
        print(f"  Loaded IC: {ic_path}")
    else:
        print(f"  [WARN] IC.csv not found at {ic_path}")

    # Load NPZ arrays if available (faster)
    npz_path = os.path.join(data_dir, "UVW_array_data.npz")
    if os.path.exists(npz_path):
        npz = np.load(npz_path)
        U = npz["U"]  # shape (11, 512, 512)
        V = npz["V"]
        W = npz["W"]
        for i, t in enumerate(GT_SNAPSHOTS):
            result["snapshots"][t] = {"u": U[i], "v": V[i], "w": W[i]}
        print(f"  Loaded NPZ snapshots: {npz_path}")
    else:
        # Fall back to individual CSV files
        for t in GT_SNAPSHOTS:
            csv_path = os.path.join(data_dir, f"sim_data_{t}.csv")
            if os.path.exists(csv_path):
                data = np.loadtxt(csv_path, delimiter=",")
                n = 512
                result["snapshots"][t] = {
                    "u": data[:, 0].reshape(n, n),
                    "v": data[:, 1].reshape(n, n),
                    "w": data[:, 2].reshape(n, n),
                }

    return result


# ---------------------------------------------------------------------------
# Fenton-Karma 3V solver (canonical NumPy reference)
# ---------------------------------------------------------------------------

class FentonKarmaSolver:
    """
    Canonical Fenton-Karma 3V solver.
    Spatial: 4-point finite differences, Neumann BCs via edge-padding.
    Temporal: Forward Euler with fixed dt.

    This is the "LLM-direct baseline": what you get from a well-written
    Python implementation of the same equations.
    """

    # Default parameters (tau_d = 0.5714 matches the ground truth dataset)
    DEFAULTS = dict(
        D=0.001, C_m=1.0,
        tau_pv=7.99, tau_v1=9.8, tau_v2=312.5,
        tau_pw=870.0, tau_mw=41.0,
        tau_0=12.5, tau_r=33.83, tau_si=29.0,
        K=10.0, V_csi=0.861, V_c=0.13, V_v=0.04,
        tau_d=0.5714,
        dt=0.025, dx=0.0390625,
    )

    def __init__(self, **kwargs):
        self.p = {**self.DEFAULTS, **kwargs}

    def _heaviside(self, x: np.ndarray) -> np.ndarray:
        return (x >= 0).astype(float)

    def _laplacian_neumann(self, field: np.ndarray) -> np.ndarray:
        """4-point Laplacian with Neumann (no-flux) BCs via padding."""
        padded = np.pad(field, pad_width=1, mode="edge")
        lap = (
            padded[2:, 1:-1] + padded[:-2, 1:-1] +
            padded[1:-1, 2:] + padded[1:-1, :-2] -
            4.0 * field
        ) / self.p["dx"] ** 2
        return lap

    def _derivatives(self, u, v, w):
        p = self.p

        lap = self._laplacian_neumann(u)
        H   = self._heaviside(u - p["V_c"])
        Hv  = self._heaviside(u - p["V_v"])

        I_fi = -v * H * (u - p["V_c"]) * (1.0 - u) / p["tau_d"]
        I_so = u * (1.0 - H) / p["tau_0"] + H / p["tau_r"]
        I_si = -w * (1.0 + np.tanh(p["K"] * (u - p["V_csi"]))) / (2.0 * p["tau_si"])

        dudt = p["D"] * lap - (I_fi + I_so + I_si) / p["C_m"]

        # tau_mv is piecewise: tau_v1 when u < V_c and u < V_v, tau_v2 otherwise
        tau_mv = np.where(Hv < 1, p["tau_v1"], p["tau_v2"])
        dvdt = (1.0 - v) * (1.0 - H) / tau_mv - v * H / p["tau_pv"]
        dwdt = (1.0 - w) * (1.0 - H) / p["tau_mw"] - w * H / p["tau_pw"]

        return dudt, dvdt, dwdt

    def step(self, u, v, w):
        """Advance one time step via forward Euler."""
        p = self.p
        dudt, dvdt, dwdt = self._derivatives(u, v, w)
        u_new = np.clip(u + p["dt"] * dudt, 0.0, 1.0)
        v_new = np.clip(v + p["dt"] * dvdt, 0.0, 1.0)
        w_new = np.clip(w + p["dt"] * dwdt, 0.0, 1.0)
        return u_new, v_new, w_new

    def run(
        self,
        ic_u: np.ndarray,
        ic_v: np.ndarray,
        ic_w: np.ndarray,
        t_start: float = 0.0,
        t_end: float = 100.0,
        sample_times: Optional[list] = None,
    ) -> Tuple[dict, dict]:
        """
        Run the FK solver from t_start to t_end.

        Args:
            ic_u, ic_v, ic_w: (512, 512) initial conditions
            t_start: start time (use > 0 to continue from a checkpoint)
            t_end: end time
            sample_times: list of times at which to record snapshots

        Returns:
            snapshots: {T: {"u": ..., "v": ..., "w": ...}}
            perf: {"wall_time_s": float, "peak_mem_mb": float, "n_steps": int}
        """
        p = self.p
        u, v, w = ic_u.copy(), ic_v.copy(), ic_w.copy()
        t = t_start
        n_steps = int(round((t_end - t_start) / p["dt"]))
        sample_set = set(sample_times) if sample_times else set()

        snapshots = {}
        tracemalloc.start()
        t0_wall = time.perf_counter()

        for _ in range(n_steps):
            u, v, w = self.step(u, v, w)
            t = round(t + p["dt"], 6)
            if t in sample_set or abs(t - round(t)) < 1e-9 and round(t) in sample_set:
                snapshots[t] = {"u": u.copy(), "v": v.copy(), "w": w.copy()}

        wall_time = time.perf_counter() - t0_wall
        _, peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        perf = {
            "wall_time_s": round(wall_time, 3),
            "peak_mem_mb": round(peak_mem / 1e6, 2),
            "n_steps": n_steps,
        }
        return snapshots, perf


# ---------------------------------------------------------------------------
# Aliev-Panfilov 2V solver (reference for Experiment 4)
# ---------------------------------------------------------------------------

class AlievPanfilovSolver:
    """
    Canonical Aliev-Panfilov 2V solver.
    Used as pseudo-ground truth for Experiment 4.
    """

    DEFAULTS = dict(
        D=0.001, a=0.1, k=8.0,
        eps_0=0.01, mu1=0.07, mu2=0.3,
        dt=0.025, dx=0.0390625,
    )

    def __init__(self, **kwargs):
        self.p = {**self.DEFAULTS, **kwargs}

    def _laplacian_neumann(self, field: np.ndarray) -> np.ndarray:
        padded = np.pad(field, pad_width=1, mode="edge")
        return (
            padded[2:, 1:-1] + padded[:-2, 1:-1] +
            padded[1:-1, 2:] + padded[1:-1, :-2] -
            4.0 * field
        ) / self.p["dx"] ** 2

    def step(self, u, v):
        p = self.p
        lap = self._laplacian_neumann(u)
        eps = p["eps_0"] + p["mu1"] * v / (p["mu2"] + u + 1e-10)
        dudt = p["D"] * lap - p["k"] * u * (u - p["a"]) * (u - 1.0) - u * v
        dvdt = eps * (-v - p["k"] * u * (u - p["a"] - 1.0))
        u_new = np.clip(u + p["dt"] * dudt, 0.0, 1.0)
        v_new = np.clip(v + p["dt"] * dvdt, 0.0, 1.0)
        return u_new, v_new

    def run(
        self,
        ic_u: np.ndarray,
        ic_v: np.ndarray,
        t_end: float = 100.0,
        sample_times: Optional[list] = None,
    ) -> Tuple[dict, dict]:
        p = self.p
        u, v = ic_u.copy(), ic_v.copy()
        n_steps = int(round(t_end / p["dt"]))
        sample_set = set(sample_times or [])

        snapshots = {}
        tracemalloc.start()
        t0_wall = time.perf_counter()

        t = 0.0
        for _ in range(n_steps):
            u, v = self.step(u, v)
            t = round(t + p["dt"], 6)
            if t in sample_set:
                snapshots[t] = {"u": u.copy(), "v": v.copy()}

        wall_time = time.perf_counter() - t0_wall
        _, peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        return snapshots, {
            "wall_time_s": round(wall_time, 3),
            "peak_mem_mb": round(peak_mem / 1e6, 2),
            "n_steps": n_steps,
        }

    def default_ic(self, n: int = 512, seed: int = 42) -> Tuple[np.ndarray, np.ndarray]:
        """Default initial condition: stimulated top-left quadrant."""
        rng = np.random.default_rng(seed)
        u = np.zeros((n, n))
        v = rng.uniform(0.0, 0.5, (n, n))
        u[:n // 4, :n // 4] = 1.0   # stimulus patch
        return u, v
