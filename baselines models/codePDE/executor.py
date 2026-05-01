import os
import re
import pickle
import subprocess
import tempfile


def extract_code(llm_response: str) -> str:
    text = re.sub(r"<think>.*?</think>", "", llm_response, flags=re.DOTALL).strip()
    match = re.search(r"```python\s*(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    match = re.search(r"```\s*(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text


def run_solver(
    code: str,
    u0,
    v0,
    w0,
    t_coordinate,
    tau_d: float,
    timeout: int = 300,
    python_bin: str | None = None,
):
    if python_bin is None:
        python_bin = os.path.join(os.path.dirname(__file__), ".venv", "bin", "python")
        if not os.path.exists(python_bin):
            python_bin = "python3"

    with tempfile.TemporaryDirectory() as tmp:
        input_path = os.path.join(tmp, "input.pkl")
        output_path = os.path.join(tmp, "output.pkl")

        with open(input_path, "wb") as f:
            pickle.dump(
                {
                    "u0": u0,
                    "v0": v0,
                    "w0": w0,
                    "t_coordinate": t_coordinate,
                    "tau_d": tau_d,
                },
                f,
            )

        wrapper = f"""\
import pickle
import numpy as np

with open({input_path!r}, "rb") as _f:
    _args = pickle.load(_f)

{code}

u_pred, v_pred, w_pred = solver(
    _args["u0"], _args["v0"], _args["w0"],
    _args["t_coordinate"], _args["tau_d"],
)

# Convert to numpy if torch tensors
if hasattr(u_pred, "cpu"):
    u_pred = u_pred.cpu().detach().numpy()
    v_pred = v_pred.cpu().detach().numpy()
    w_pred = w_pred.cpu().detach().numpy()

with open({output_path!r}, "wb") as _f:
    pickle.dump({{"u": u_pred, "v": v_pred, "w": w_pred}}, _f)
"""

        script_path = os.path.join(tmp, "run_solver.py")
        with open(script_path, "w") as f:
            f.write(wrapper)

        try:
            proc = subprocess.run(
                [python_bin, script_path],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=tmp,
            )
        except subprocess.TimeoutExpired:
            return None, "", f"TimeoutError: solver exceeded {timeout}s"

        stdout = proc.stdout or ""
        stderr = proc.stderr or ""

        if proc.returncode != 0:
            return None, stdout, stderr

        try:
            with open(output_path, "rb") as f:
                result = pickle.load(f)
            return result, stdout, ""
        except Exception as e:
            return None, stdout, f"Failed to load solver output: {e}"
