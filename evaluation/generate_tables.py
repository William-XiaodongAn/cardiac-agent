"""
generate_tables.py — Convert results CSVs into paper-ready LaTeX tables.

Usage:
    python generate_tables.py --results-dir results/
"""

import argparse
import csv
import json
from pathlib import Path

RESULTS_DIR = Path("results")
TABLES_DIR  = Path("results/tables")
TABLES_DIR.mkdir(parents=True, exist_ok=True)


def _fmt(val, decimals=4):
    if val is None or val != val:  # None or NaN
        return "—"
    return f"{float(val):.{decimals}f}"


# ---------------------------------------------------------------------------
# Table 1 — Numerical accuracy (Experiment 1)
# ---------------------------------------------------------------------------

def table1_accuracy(csv_path: str):
    """
    Input CSV columns: method, snapshot_t, l2_u, l2_v, l2_w, rmse_u, ssim_u
    Outputs mean ± std across all snapshots per method.
    """
    import csv as _csv
    import numpy as np
    from collections import defaultdict

    data = defaultdict(list)
    with open(csv_path) as f:
        reader = _csv.DictReader(f)
        for row in reader:
            m = row["method"]
            data[m].append(row)

    methods = list(data.keys())

    lines = []
    lines.append(r"\begin{table}[ht]")
    lines.append(r"\centering")
    lines.append(r"\caption{Numerical accuracy on FK ground truth (tau\_d=0.5714). "
                 r"Relative L2 error and SSIM averaged over 11 snapshots (T=831.25–931.25).}")
    lines.append(r"\label{tab:accuracy}")
    lines.append(r"\begin{tabular}{lccccc}")
    lines.append(r"\toprule")
    lines.append(r"Method & L2-$u\downarrow$ & L2-$v\downarrow$ & L2-$w\downarrow$ & SSIM-$u\uparrow$ & RMSE-$u\downarrow$ \\")
    lines.append(r"\midrule")

    for method in methods:
        rows = data[method]
        l2_u  = np.mean([float(r["l2_u"])  for r in rows])
        l2_v  = np.mean([float(r["l2_v"])  for r in rows])
        l2_w  = np.mean([float(r["l2_w"])  for r in rows])
        ssim_u= np.mean([float(r["ssim_u"]) for r in rows])
        rmse_u= np.mean([float(r["rmse_u"]) for r in rows])
        std_l2= np.std( [float(r["l2_u"])  for r in rows])

        row_str = (
            f"{method} & {_fmt(l2_u)}$\\pm${_fmt(std_l2)} & "
            f"{_fmt(l2_v)} & {_fmt(l2_w)} & {_fmt(ssim_u)} & "
            f"{_fmt(rmse_u)} \\\\"
        )
        lines.append(row_str)

    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(r"\end{table}")

    out = TABLES_DIR / "table1_accuracy.tex"
    out.write_text("\n".join(lines))
    print(f"  Written: {out}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Table 2 — Performance (Experiment 2)
# ---------------------------------------------------------------------------

def table2_performance(csv_path: str):
    import csv as _csv

    with open(csv_path) as f:
        rows = list(_csv.DictReader(f))

    lines = []
    lines.append(r"\begin{table}[ht]")
    lines.append(r"\centering")
    lines.append(r"\caption{Computational performance for T=100 simulation. "
                 r"FPS measured over 60s live browser session (WebGL only).}")
    lines.append(r"\label{tab:performance}")
    lines.append(r"\begin{tabular}{lcccc}")
    lines.append(r"\toprule")
    lines.append(r"Method & Sim time (s)$\downarrow$ & FPS$\uparrow$ & Mem (MB)$\downarrow$ & GPU \\")
    lines.append(r"\midrule")

    for row in rows:
        fps = row.get("fps", "N/A")
        fps_str = _fmt(fps, 1) if fps not in ("", "N/A", None) else r"\textit{N/A}"
        gpu = row.get("uses_gpu", "No")
        lines.append(
            f"{row['method']} & {_fmt(row['wall_time_s'], 1)} & {fps_str} & "
            f"{_fmt(row['peak_mem_mb'], 1)} & {gpu} \\\\"
        )

    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(r"\end{table}")

    out = TABLES_DIR / "table2_performance.tex"
    out.write_text("\n".join(lines))
    print(f"  Written: {out}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Table 3 — Robustness (Experiment 3)
# ---------------------------------------------------------------------------

def table3_robustness(csv_path: str):
    import csv as _csv

    with open(csv_path) as f:
        rows = list(_csv.DictReader(f))

    lines = []
    lines.append(r"\begin{table}[ht]")
    lines.append(r"\centering")
    lines.append(r"\caption{Code generation robustness over N=10 independent trials.}")
    lines.append(r"\label{tab:robustness}")
    lines.append(r"\begin{tabular}{lccc}")
    lines.append(r"\toprule")
    lines.append(r"Method & 1st-gen success$\uparrow$ & Validation pass$\uparrow$ & Mean iterations$\downarrow$ \\")
    lines.append(r"\midrule")

    for row in rows:
        lines.append(
            f"{row['method']} & {_fmt(float(row['first_gen_success_rate']), 2)} & "
            f"{_fmt(float(row['validation_pass_rate']), 2)} & "
            f"{_fmt(float(row['mean_debug_iterations']), 2)} \\\\"
        )

    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(r"\end{table}")

    out = TABLES_DIR / "table3_robustness.tex"
    out.write_text("\n".join(lines))
    print(f"  Written: {out}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Generate LaTeX tables from results CSVs")
    p.add_argument("--results-dir", default="results")
    args = p.parse_args()

    rd = Path(args.results_dir)
    print("Generating LaTeX tables...\n")

    if (rd / "exp1_accuracy.csv").exists():
        table1_accuracy(rd / "exp1_accuracy.csv")

    if (rd / "exp2_performance.csv").exists():
        table2_performance(rd / "exp2_performance.csv")

    if (rd / "exp3_robustness.csv").exists():
        table3_robustness(rd / "exp3_robustness.csv")

    print("\nAll tables written to results/tables/")
