"""
baselines/codepde.py — CodePDE baseline wrapper.

CodePDE uses an LLM to generate a solver with iterative debugging:
  1. Generate solver code from PDE description.
  2. Execute; if error, feed error message back to LLM for debugging.
  3. Repeat up to max_attempts.

This mirrors the CodePDE paper approach and the existing pipeline in
baselines models/codePDE/codePDE.ipynb.
"""

from __future__ import annotations
import time
import tracemalloc
import subprocess
import tempfile
import os
import pickle
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class CodePDEBaseline:
    """
    CodePDE: LLM generate → execute → debug loop.

    Parameters
    ----------
    gen_model   : LLM model for initial code generation.
    debug_model : LLM model for debugging (can be a smaller coder model).
    max_attempts: Maximum debug iterations before giving up.
    """

    def __init__(
        self,
        gen_model: str = "qwen3:8b",
        debug_model: str = "qwen2.5-coder:3b",
        max_attempts: int = 3,
    ):
        self.gen_model = gen_model
        self.debug_model = debug_model
        self.max_attempts = max_attempts
        self._code: Optional[str] = None
        self._n_debug_iters: int = 0
        self._bug_free: bool = False

    def _llm(self, model: str, prompt: str) -> str:
        from ollama import chat
        resp = chat(model=model, messages=[{"role": "user", "content": prompt}])
        code = resp.message.content.strip()
        for fence in ("```python", "```"):
            if code.startswith(fence):
                code = code[len(fence):]
        if code.endswith("```"):
            code = code[:-3]
        return code.strip()

    def generate(self, pde_description: str) -> str:
        prompt = (
            "Implement a complete, runnable Python NumPy solver for the following PDE.\n"
            "The function signature must be:\n"
            "    def solve(ic: dict, t_end: float, sample_times: list) -> dict:\n"
            "        # ic: {var_name: np.ndarray}, returns {t: {var_name: array}}\n\n"
            f"PDE description:\n{pde_description}\n\n"
            "Return only raw Python code, no markdown."
        )
        self._code = self._llm(self.gen_model, prompt)
        return self._code

    def _try_execute(self, ic, t_end, sample_times) -> tuple[dict, str]:
        """Try running self._code. Returns (result, error_message)."""
        with tempfile.TemporaryDirectory() as tmp:
            ic_path  = os.path.join(tmp, "ic.pkl")
            out_path = os.path.join(tmp, "out.pkl")
            with open(ic_path, "wb") as f:
                pickle.dump({"ic": ic, "t_end": t_end, "sample_times": sample_times}, f)

            wrapper = (
                f"import pickle, numpy as np\n"
                f"with open('{ic_path}','rb') as f: args=pickle.load(f)\n"
                f"{self._code}\n"
                f"result = solve(args['ic'], args['t_end'], args['sample_times'])\n"
                f"with open('{out_path}','wb') as f: pickle.dump(result, f)\n"
            )
            code_path = os.path.join(tmp, "solver.py")
            with open(code_path, "w") as f:
                f.write(wrapper)

            try:
                proc = subprocess.run(
                    ["python", code_path],
                    timeout=120,
                    capture_output=True,
                    text=True,
                )
                if proc.returncode != 0:
                    return {}, proc.stderr or proc.stdout
                with open(out_path, "rb") as f:
                    return pickle.load(f), ""
            except subprocess.TimeoutExpired:
                return {}, "TimeoutError: solver exceeded 120 seconds"
            except Exception as e:
                return {}, str(e)

    def run(
        self,
        ic: dict,
        t_end: float,
        sample_times: list,
        pde_description: str = "",
    ) -> tuple[dict, dict]:
        """
        Generate → execute → debug loop.
        Returns (snapshots, perf_info).
        """
        if not self._code:
            self.generate(pde_description)

        self._n_debug_iters = 0
        tracemalloc.start()
        t0 = time.perf_counter()

        for attempt in range(self.max_attempts):
            snaps, err = self._try_execute(ic, t_end, sample_times)
            if not err:
                self._bug_free = True
                break

            logger.info("  CodePDE attempt %d/%d failed: %s", attempt+1, self.max_attempts, err[:120])
            self._n_debug_iters += 1

            if attempt < self.max_attempts - 1:
                debug_prompt = (
                    f"Fix this Python PDE solver code.\n\nError:\n{err}\n\n"
                    f"Code:\n{self._code}\n\nReturn only corrected raw Python code."
                )
                self._code = self._llm(self.debug_model, debug_prompt)
        else:
            self._bug_free = False
            snaps = {}

        wall = time.perf_counter() - t0
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        return snaps, {
            "wall_time_s": wall,
            "peak_mem_mb": peak / 1e6,
            "bug_free": self._bug_free,
            "debug_iterations": self._n_debug_iters,
        }
