"""
baselines/llm_direct.py — LLM-direct baseline.

Single-shot: the LLM generates a Python NumPy solver in one call with no
iterative debugging. Represents the simplest possible LLM code-generation
approach.

Also contains FentonKarmaSolver and AlievPanfilovSolver as canonical
reference implementations (bug-free rate = 1.0 upper bound).
"""

from __future__ import annotations
import time
import tracemalloc
from typing import Optional
import numpy as np


class FentonKarmaSolver:
    """Canonical Fenton-Karma 3V reference solver (NumPy, Neumann BCs)."""

    DEFAULTS = dict(
        D=0.001, C_m=1.0,
        tau_pv=7.99, tau_v1=9.8, tau_v2=312.5,
        tau_pw=870.0, tau_mw=41.0, tau_0=12.5,
        tau_r=33.83, tau_si=29.0, K=10.0,
        V_csi=0.861, V_c=0.13, V_v=0.04, tau_d=0.5714,
        dt=0.025, dx=0.0390625,
    )

    def __init__(self, **kwargs):
        self.p = {**self.DEFAULTS, **kwargs}

    def _lap(self, f: np.ndarray) -> np.ndarray:
        pad = np.pad(f, 1, mode="edge")
        return (pad[2:, 1:-1] + pad[:-2, 1:-1] +
                pad[1:-1, 2:] + pad[1:-1, :-2] - 4 * f) / self.p["dx"] ** 2

    def step(self, u, v, w):
        p = self.p
        H = (u >= p["V_c"]).astype(float)
        Hv = (u >= p["V_v"]).astype(float)
        I_fi = -v * H * (u - p["V_c"]) * (1 - u) / p["tau_d"]
        I_so = u * (1 - H) / p["tau_0"] + H / p["tau_r"]
        I_si = -w * (1 + np.tanh(p["K"] * (u - p["V_csi"]))) / (2 * p["tau_si"])
        tau_mv = np.where(Hv < 1, p["tau_v1"], p["tau_v2"])
        du = p["D"] * self._lap(u) - (I_fi + I_so + I_si) / p["C_m"]
        dv = (1 - v) * (1 - H) / tau_mv - v * H / p["tau_pv"]
        dw = (1 - w) * (1 - H) / p["tau_mw"] - w * H / p["tau_pw"]
        return (np.clip(u + p["dt"] * du, 0, 1),
                np.clip(v + p["dt"] * dv, 0, 1),
                np.clip(w + p["dt"] * dw, 0, 1))

    def run(self, ic, t_end, sample_times):
        u, v, w = ic["u"].copy(), ic["v"].copy(), ic["w"].copy()
        t, sample_set = 0.0, set(sample_times)
        n_steps = int(round(t_end / self.p["dt"]))
        snaps = {}
        tracemalloc.start()
        t0 = time.perf_counter()
        for _ in range(n_steps):
            u, v, w = self.step(u, v, w)
            t = round(t + self.p["dt"], 6)
            if t in sample_set:
                snaps[t] = {"u": u.copy(), "v": v.copy(), "w": w.copy()}
        wall = time.perf_counter() - t0
        _, peak = tracemalloc.get_traced_memory(); tracemalloc.stop()
        return snaps, {"wall_time_s": wall, "peak_mem_mb": peak/1e6, "bug_free": True}


class AlievPanfilovSolver:
    """Canonical Aliev-Panfilov 2V reference solver."""

    DEFAULTS = dict(D=0.001, a=0.1, k=8.0, eps_0=0.01, mu1=0.07, mu2=0.3,
                    dt=0.025, dx=0.0390625)

    def __init__(self, **kwargs):
        self.p = {**self.DEFAULTS, **kwargs}

    def _lap(self, f):
        pad = np.pad(f, 1, mode="edge")
        return (pad[2:, 1:-1] + pad[:-2, 1:-1] +
                pad[1:-1, 2:] + pad[1:-1, :-2] - 4 * f) / self.p["dx"] ** 2

    def step(self, u, v):
        p = self.p
        eps = p["eps_0"] + p["mu1"] * v / (p["mu2"] + u + 1e-10)
        du = p["D"] * self._lap(u) - p["k"] * u * (u - p["a"]) * (u - 1) - u * v
        dv = eps * (-v - p["k"] * u * (u - p["a"] - 1))
        return np.clip(u + p["dt"] * du, 0, 1), np.clip(v + p["dt"] * dv, 0, 1)

    def run(self, ic, t_end, sample_times):
        u, v = ic["u"].copy(), ic["v"].copy()
        t, sample_set = 0.0, set(sample_times)
        n_steps = int(round(t_end / self.p["dt"]))
        snaps = {}
        tracemalloc.start()
        t0 = time.perf_counter()
        for _ in range(n_steps):
            u, v = self.step(u, v)
            t = round(t + self.p["dt"], 6)
            if t in sample_set:
                snaps[t] = {"u": u.copy(), "v": v.copy()}
        wall = time.perf_counter() - t0
        _, peak = tracemalloc.get_traced_memory(); tracemalloc.stop()
        return snaps, {"wall_time_s": wall, "peak_mem_mb": peak/1e6, "bug_free": True}


class LLMDirectBaseline:
    """
    LLM-direct: single-shot LLM generation of a Python solver, no debugging.

    The LLM receives the PDE description and coding skeleton and returns code.
    Code is executed in a sandboxed subprocess; success/failure is recorded.
    """

    def __init__(self, model: str = "qwen3:8b"):
        self.model = model
        self._generated_code: Optional[str] = None
        self._bug_free: bool = False

    def generate(self, pde_description: str, skeleton: str = "") -> str:
        """Single-shot code generation. Returns raw GLSL/Python code."""
        from ollama import chat
        prompt = (
            f"Generate a complete Python NumPy solver for:\n{pde_description}\n"
            f"Skeleton:\n{skeleton}\nReturn only raw Python code."
        )
        resp = chat(model=self.model, messages=[{"role": "user", "content": prompt}])
        code = resp.message.content.strip()
        for fence in ("```python", "```"):
            if code.startswith(fence):
                code = code[len(fence):]
        if code.endswith("```"):
            code = code[:-3]
        self._generated_code = code.strip()
        return self._generated_code

    def execute(self, ic: dict, t_end: float, sample_times: list) -> tuple[dict, dict]:
        """
        Execute the generated code in a subprocess.
        Returns (snapshots, perf) where perf includes bug_free flag.
        """
        import subprocess, tempfile, os, pickle
        if not self._generated_code:
            raise RuntimeError("Call generate() first.")

        # Write IC and wrapper to temp files
        with tempfile.TemporaryDirectory() as tmp:
            ic_path  = os.path.join(tmp, "ic.pkl")
            out_path = os.path.join(tmp, "out.pkl")
            with open(ic_path, "wb") as f:
                pickle.dump({"ic": ic, "t_end": t_end, "sample_times": sample_times}, f)

            wrapper = (
                f"import pickle, numpy as np\n"
                f"with open('{ic_path}','rb') as f: args=pickle.load(f)\n"
                f"{self._generated_code}\n"
                f"result = solve(args['ic'], args['t_end'], args['sample_times'])\n"
                f"with open('{out_path}','wb') as f: pickle.dump(result, f)\n"
            )
            code_path = os.path.join(tmp, "solver.py")
            with open(code_path, "w") as f:
                f.write(wrapper)

            t0 = time.perf_counter()
            try:
                subprocess.run(
                    ["python", code_path],
                    timeout=120,
                    check=True,
                    capture_output=True,
                )
                wall = time.perf_counter() - t0
                with open(out_path, "rb") as f:
                    snaps = pickle.load(f)
                self._bug_free = True
                return snaps, {"wall_time_s": wall, "bug_free": True, "peak_mem_mb": 0}
            except Exception as e:
                wall = time.perf_counter() - t0
                self._bug_free = False
                return {}, {"wall_time_s": wall, "bug_free": False, "error": str(e)}
