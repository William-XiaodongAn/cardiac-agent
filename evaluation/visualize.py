"""
visualize.py — Figure generation for the Web-PDE-LLM paper.

Produces all figures described in EXPERIMENTS.md §5.
Figures are saved to results/figures/ as PDF (vector) + PNG (300 Dpi).

Usage:
    python visualize.py --results-dir results/
    python visualize.py --fig 2   # generate only Fig 2
"""

import argparse
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path
from typing import Optional

FIGURES_DIR = Path("results/figures")
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

METHOD_LABELS = ["LLM-direct", "CodePDE", "Web-PDE-LLM (ours)"]
METHOD_COLORS = ["#4878D0", "#EE854A", "#6ACC65"]
METHOD_LINESTYLES = ["--", "-.", "-"]


def _save(fig, name: str):
    for ext in ("pdf", "png"):
        path = FIGURES_DIR / f"{name}.{ext}"
        fig.savefig(path, bbox_inches="tight", dpi=300)
    print(f"  Saved: {FIGURES_DIR / name}.[pdf,png]")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Fig 2 — Error maps (u field, all methods, T=931.25)
# ---------------------------------------------------------------------------

def fig2_error_maps(snapshots: dict, gt_u: np.ndarray, timestamp: float = 931.25):
    """
    3-column subplot: predicted u field + absolute error map for each method.

    snapshots: {"LLM-direct": {931.25: {"u": ...}}, "CodePDE": ..., ...}
    """
    methods = list(snapshots.keys())
    n_methods = len(methods)

    fig, axes = plt.subplots(
        2, n_methods + 1,
        figsize=(4 * (n_methods + 1), 8),
        constrained_layout=True,
    )
    fig.suptitle(f"Transmembrane Voltage u  (T = {timestamp})", fontsize=13)

    # Ground truth column
    im = axes[0, 0].imshow(gt_u, cmap="RdBu_r", vmin=0, vmax=1, origin="lower")
    axes[0, 0].set_title("Ground Truth", fontsize=10)
    axes[0, 0].axis("off")
    axes[1, 0].axis("off")
    plt.colorbar(im, ax=axes[0, 0], fraction=0.046, pad=0.04)

    for col, method in enumerate(methods, start=1):
        pred_u = snapshots[method].get(timestamp, {}).get("u")
        if pred_u is None:
            axes[0, col].axis("off")
            axes[1, col].axis("off")
            continue

        axes[0, col].imshow(pred_u, cmap="RdBu_r", vmin=0, vmax=1, origin="lower")
        axes[0, col].set_title(method, fontsize=10)
        axes[0, col].axis("off")

        err = np.abs(pred_u - gt_u)
        im_err = axes[1, col].imshow(err, cmap="hot", vmin=0, vmax=0.2, origin="lower")
        axes[1, col].set_title(f"Abs. error (max={err.max():.3f})", fontsize=9)
        axes[1, col].axis("off")
        plt.colorbar(im_err, ax=axes[1, col], fraction=0.046, pad=0.04)

    _save(fig, "fig2_error_maps")


# ---------------------------------------------------------------------------
# Fig 3 — L2 error over time
# ---------------------------------------------------------------------------

def fig3_l2_over_time(accuracy_results: dict):
    """
    accuracy_results: {method: {T: {"l2_u": float, ...}}}
    """
    fig, axes = plt.subplots(1, 3, figsize=(14, 4), constrained_layout=True)
    fig.suptitle("Relative L2 Error over Time", fontsize=13)

    for ax, var in zip(axes, ["u", "v", "w"]):
        for method, color, ls in zip(METHOD_LABELS, METHOD_COLORS, METHOD_LINESTYLES):
            if method not in accuracy_results:
                continue
            times = sorted(accuracy_results[method].keys())
            errors = [accuracy_results[method][t].get(f"l2_{var}", np.nan) for t in times]
            ax.plot(times, errors, label=method, color=color, linestyle=ls, linewidth=2)
        ax.set_xlabel("Simulation time (t)")
        ax.set_ylabel(f"Relative L2 error  (var={var})")
        ax.set_title(f"State variable  {var}")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)

    _save(fig, "fig3_l2_over_time")


# ---------------------------------------------------------------------------
# Fig 4 — Action potential time series (centre pixel)
# ---------------------------------------------------------------------------

def fig4_action_potential(traces: dict, dt: float = 0.025, gt_trace: Optional[np.ndarray] = None):
    """
    traces: {method: np.ndarray of shape (T_steps,)}
    """
    fig, ax = plt.subplots(figsize=(10, 4), constrained_layout=True)
    fig.suptitle("Action Potential — Centre Pixel (256, 256)", fontsize=13)

    if gt_trace is not None:
        t_gt = np.arange(len(gt_trace)) * dt
        ax.plot(t_gt, gt_trace, color="black", linewidth=2.5, label="Ground Truth", zorder=5)

    for method, color, ls in zip(METHOD_LABELS, METHOD_COLORS, METHOD_LINESTYLES):
        if method not in traces:
            continue
        trace = traces[method]
        t = np.arange(len(trace)) * dt
        ax.plot(t, trace, color=color, linestyle=ls, linewidth=1.5, label=method)

    ax.axhline(0.13, color="gray", linestyle=":", linewidth=1, label="V_c = 0.13")
    ax.set_xlabel("Time (simulation units)")
    ax.set_ylabel("u (transmembrane potential)")
    ax.legend(fontsize=9)
    ax.set_ylim(-0.05, 1.1)
    ax.grid(True, alpha=0.3)

    _save(fig, "fig4_action_potential")


# ---------------------------------------------------------------------------
# Fig 5 — Performance speedup bar chart
# ---------------------------------------------------------------------------

def fig5_performance(perf_results: dict):
    """
    perf_results: {method: {"wall_time_s": float, "fps": float|None, "peak_mem_mb": float}}
    """
    methods = list(perf_results.keys())
    times = [perf_results[m]["wall_time_s"] for m in methods]
    fps   = [perf_results[m].get("fps") or 0 for m in methods]
    mems  = [perf_results[m]["peak_mem_mb"] for m in methods]

    fig, axes = plt.subplots(1, 3, figsize=(14, 4), constrained_layout=True)
    fig.suptitle("Computational Performance", fontsize=13)

    x = np.arange(len(methods))
    colors = [METHOD_COLORS[METHOD_LABELS.index(m)] if m in METHOD_LABELS else "#888" for m in methods]

    axes[0].bar(x, times, color=colors)
    axes[0].set_xticks(x); axes[0].set_xticklabels(methods, rotation=15, ha="right", fontsize=9)
    axes[0].set_ylabel("Wall-clock time (s)  — lower is better")
    axes[0].set_title("Simulation time (T=100)")
    axes[0].grid(axis="y", alpha=0.3)

    axes[1].bar(x, fps, color=colors)
    axes[1].set_xticks(x); axes[1].set_xticklabels(methods, rotation=15, ha="right", fontsize=9)
    axes[1].set_ylabel("Frames per second  — higher is better")
    axes[1].set_title("Interactive frame rate")
    axes[1].grid(axis="y", alpha=0.3)
    # Mark Python baselines as N/A
    for i, m in enumerate(methods):
        if perf_results[m].get("fps") is None:
            axes[1].text(i, 1, "N/A", ha="center", fontsize=9, color="gray")

    axes[2].bar(x, mems, color=colors)
    axes[2].set_xticks(x); axes[2].set_xticklabels(methods, rotation=15, ha="right", fontsize=9)
    axes[2].set_ylabel("Peak memory (MB)  — lower is better")
    axes[2].set_title("Memory usage")
    axes[2].grid(axis="y", alpha=0.3)

    _save(fig, "fig5_performance")


# ---------------------------------------------------------------------------
# Fig 6 — Robustness / code-generation success bars
# ---------------------------------------------------------------------------

def fig6_robustness(robustness_results: dict):
    """
    robustness_results: {method: {"first_gen_success_rate": float,
                                  "validation_pass_rate": float,
                                  "mean_debug_iterations": float}}
    """
    methods = list(robustness_results.keys())
    x = np.arange(len(methods))
    w = 0.25
    colors = [METHOD_COLORS[METHOD_LABELS.index(m)] if m in METHOD_LABELS else "#888" for m in methods]

    first_gen = [robustness_results[m]["first_gen_success_rate"] for m in methods]
    val_pass  = [robustness_results[m]["validation_pass_rate"] for m in methods]
    iterations= [robustness_results[m]["mean_debug_iterations"] for m in methods]

    fig, axes = plt.subplots(1, 2, figsize=(12, 4), constrained_layout=True)
    fig.suptitle("Code Generation Robustness (N=10 trials)", fontsize=13)

    axes[0].bar(x - w/2, first_gen, w, label="1st-gen success", color="#4878D0", alpha=0.85)
    axes[0].bar(x + w/2, val_pass,  w, label="Validation pass", color="#6ACC65", alpha=0.85)
    axes[0].set_xticks(x); axes[0].set_xticklabels(methods, rotation=15, ha="right", fontsize=9)
    axes[0].set_ylabel("Rate  (higher is better)")
    axes[0].set_ylim(0, 1.1)
    axes[0].legend(fontsize=9)
    axes[0].grid(axis="y", alpha=0.3)

    axes[1].bar(x, iterations, color=colors, alpha=0.85)
    axes[1].set_xticks(x); axes[1].set_xticklabels(methods, rotation=15, ha="right", fontsize=9)
    axes[1].set_ylabel("Mean debug iterations  (lower is better)")
    axes[1].set_title("Debug Iterations to Convergence")
    axes[1].grid(axis="y", alpha=0.3)

    _save(fig, "fig6_robustness")


# ---------------------------------------------------------------------------
# Fig 7 — Aliev-Panfilov spiral wave snapshots
# ---------------------------------------------------------------------------

def fig7_ap_spirals(snapshots: dict, times: list = None):
    """
    snapshots: {method: {T: {"u": np.ndarray, ...}}}
    Plots u field at multiple times for Web-PDE-LLM and AP reference solver.
    """
    if times is None:
        times = [25.0, 50.0, 75.0, 100.0]
    methods = list(snapshots.keys())
    n_rows = len(methods)
    n_cols = len(times)

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(3 * n_cols, 3 * n_rows),
                             constrained_layout=True)
    if n_rows == 1:
        axes = axes[np.newaxis, :]

    fig.suptitle("Aliev-Panfilov 2V — Spiral Wave Evolution  (u field)", fontsize=13)

    for row, method in enumerate(methods):
        for col, t in enumerate(times):
            ax = axes[row, col]
            snapshot = snapshots[method].get(t, {}).get("u")
            if snapshot is not None:
                ax.imshow(snapshot, cmap="RdBu_r", vmin=0, vmax=1, origin="lower")
            else:
                ax.text(0.5, 0.5, "N/A", ha="center", va="center", transform=ax.transAxes)
            ax.axis("off")
            if row == 0:
                ax.set_title(f"T={t}", fontsize=10)
            if col == 0:
                ax.set_ylabel(method, fontsize=9)

    _save(fig, "fig7_ap_spirals")


# ---------------------------------------------------------------------------
# Fig 8 — Spiral tip trajectories
# ---------------------------------------------------------------------------

def fig8_spiral_tips(tip_trajectories: dict, gt_tips: Optional[np.ndarray] = None):
    """
    tip_trajectories: {method: {T: np.ndarray (N, 2)}}
    Plots detected tip positions over time for each method.
    """
    fig, axes = plt.subplots(1, len(tip_trajectories), figsize=(5 * len(tip_trajectories), 5),
                             constrained_layout=True)
    if len(tip_trajectories) == 1:
        axes = [axes]

    fig.suptitle("Spiral Wave Tip Trajectories  (FK, T=831–931)", fontsize=13)

    for ax, (method, traj) in zip(axes, tip_trajectories.items()):
        times = sorted(traj.keys())
        cmap = plt.cm.viridis
        for i, t in enumerate(times):
            tips = traj[t]
            if len(tips) == 0:
                continue
            c = cmap(i / max(len(times) - 1, 1))
            ax.scatter(tips[:, 1], tips[:, 0], s=15, color=c, alpha=0.8)
        ax.set_xlim(0, 512); ax.set_ylim(0, 512)
        ax.set_title(method, fontsize=10)
        ax.set_xlabel("x (pixels)"); ax.set_ylabel("y (pixels)")
        ax.grid(True, alpha=0.2)

        sm = plt.cm.ScalarMappable(cmap=cmap,
                                   norm=plt.Normalize(min(times), max(times)))
        plt.colorbar(sm, ax=ax, label="Time")

    _save(fig, "fig8_spiral_tips")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--results-dir", default="results")
    p.add_argument("--fig", type=int, default=None, help="Generate only figure N")
    args = p.parse_args()

    results_dir = Path(args.results_dir)
    print(f"Loading results from: {results_dir}")

    # Load pre-computed results JSONs and generate the figures
    # (This is called automatically by eval_pipeline.py after running all experiments)
    print("Run eval_pipeline.py --all to generate all results, then re-run this script for figures.")
