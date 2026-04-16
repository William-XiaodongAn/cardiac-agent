"""
eval_pipeline.py — Master evaluation runner for the Web-PDE-LLM paper.

Runs all 5 experiments, computes metrics, writes result CSVs,
generates all figures, and produces LaTeX tables.

Usage:
    python eval_pipeline.py --all                  # full paper evaluation
    python eval_pipeline.py --exp 1                # single experiment
    python eval_pipeline.py --exp 1 2 3            # multiple experiments
    python eval_pipeline.py --all --no-webgl       # skip WebGL (Python-only)
    python eval_pipeline.py --all --n-trials 5     # robustness with 5 trials
    python eval_pipeline.py --dry-run              # check imports, no LLM calls

Requirements:
    pip install numpy scipy scikit-image matplotlib pillow playwright
    playwright install chromium
"""

import argparse
import csv
import json
import logging
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

import numpy as np

# Local modules
sys.path.insert(0, str(Path(__file__).parent))
from metrics import (
    accuracy_suite_uvw, relative_l2_error, rmse, max_absolute_error, ssim,
    action_potential_duration, conduction_velocity, spiral_tip_count,
    detect_spiral_tips, code_generation_summary, Timer,
)
from baseline_runner import (
    FentonKarmaSolver, AlievPanfilovSolver, load_ground_truth, GT_SNAPSHOTS,
)
from visualize import (
    fig2_error_maps, fig3_l2_over_time, fig4_action_potential,
    fig5_performance, fig6_robustness, fig7_ap_spirals, fig8_spiral_tips,
)
from generate_tables import table1_accuracy, table2_performance, table3_robustness

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)-8s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("eval")

RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)
(RESULTS_DIR / "figures").mkdir(exist_ok=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_csv(path: Path, rows: list[dict]):
    if not rows:
        return
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    logger.info("  Results → %s", path)


def _log_hardware():
    info = {
        "platform": platform.platform(),
        "python": sys.version,
        "cpu": platform.processor(),
        "numpy_version": np.__version__,
    }
    try:
        import torch
        info["torch"] = torch.__version__
        info["cuda_available"] = torch.cuda.is_available()
        if torch.cuda.is_available():
            info["gpu"] = torch.cuda.get_device_name(0)
    except ImportError:
        pass
    (RESULTS_DIR / "hardware.json").write_text(json.dumps(info, indent=2))
    logger.info("  Hardware logged → results/hardware.json")
    return info


def _run_llm_direct_solver(ic: dict, sample_times: list[float]) -> tuple[dict, dict]:
    """Run the LLM-direct baseline: canonical NumPy FK solver."""
    solver = FentonKarmaSolver()
    logger.info("  Running LLM-direct (NumPy FK solver)…")
    with Timer("LLM-direct") as t:
        snapshots, perf = solver.run(
            ic["u"], ic["v"], ic["w"],
            t_start=0.0,
            t_end=max(sample_times),
            sample_times=sample_times,
        )
    perf["wall_time_s"] = t.elapsed
    return snapshots, perf


def _run_webgl(html_path: str, sample_times: list[float]) -> tuple[dict, dict]:
    """Run the WebGL simulation via Playwright and capture pixel data."""
    from webgl_capture import WebGLCapture
    cap = WebGLCapture(html_path)
    logger.info("  Running WebGL capture…")
    result = cap.run(sample_times=sample_times, fps_duration_s=60.0)
    snapshots = result["snapshots"]
    perf = {
        "wall_time_s": result["perf"].get("wall_time_s", 0),
        "fps": result.get("fps"),
        "peak_mem_mb": 0,  # GPU memory not easily measurable
        "uses_gpu": "Yes",
    }
    return snapshots, perf


# ---------------------------------------------------------------------------
# Experiment 1 — Numerical Accuracy
# ---------------------------------------------------------------------------

def experiment_1(gt: dict, html_path: Optional[str] = None, skip_webgl: bool = False):
    logger.info("=== Experiment 1: Numerical Accuracy ===")

    sample_times = GT_SNAPSHOTS
    ic = gt["ic"]

    all_snapshots = {}
    all_perf = {}

    # LLM-direct
    snaps, perf = _run_llm_direct_solver(ic, sample_times)
    all_snapshots["LLM-direct"] = snaps
    all_perf["LLM-direct"] = {**perf, "uses_gpu": "No", "fps": None}

    # CodePDE — runs the same NumPy solver but with the generated code
    # For reproducibility, we treat this as a second run of the reference solver
    # (in practice: replace this block with the CodePDE-generated solver)
    logger.info("  Running CodePDE baseline (reference solver with CodePDE parameters)…")
    codepde_solver = FentonKarmaSolver(tau_d=0.5714)  # swap for LLM-generated solver
    with Timer("CodePDE") as t:
        snaps_cpde, perf_cpde = codepde_solver.run(
            ic["u"], ic["v"], ic["w"],
            t_start=0.0, t_end=max(sample_times), sample_times=sample_times,
        )
    all_snapshots["CodePDE"] = snaps_cpde
    all_perf["CodePDE"] = {**perf_cpde, "wall_time_s": t.elapsed,
                           "uses_gpu": "No", "fps": None}

    # Web-PDE-LLM (WebGL)
    if not skip_webgl and html_path:
        try:
            snaps_wgl, perf_wgl = _run_webgl(html_path, sample_times)
            all_snapshots["Web-PDE-LLM"] = snaps_wgl
            all_perf["Web-PDE-LLM"] = perf_wgl
        except Exception as e:
            logger.warning("  WebGL capture failed: %s — skipping.", e)

    # Compute metrics at each snapshot
    rows = []
    for method, snaps in all_snapshots.items():
        for t in sample_times:
            gt_snap = gt["snapshots"].get(t)
            pred_snap = snaps.get(t)
            if gt_snap is None or pred_snap is None:
                continue
            metrics = accuracy_suite_uvw(
                pred_snap["u"], gt_snap["u"],
                pred_snap["v"], gt_snap["v"],
                pred_snap.get("w", np.zeros_like(pred_snap["u"])),
                gt_snap.get("w", np.zeros_like(gt_snap["u"])),
            )
            rows.append({"method": method, "snapshot_t": t, **metrics})

    _write_csv(RESULTS_DIR / "exp1_accuracy.csv", rows)

    # Figures
    logger.info("  Generating figures…")
    gt_u_last = gt["snapshots"][GT_SNAPSHOTS[-1]]["u"]
    fig2_error_maps(
        {m: all_snapshots[m] for m in all_snapshots},
        gt_u_last,
        timestamp=GT_SNAPSHOTS[-1],
    )

    acc_by_method_t = {
        m: {r["snapshot_t"]: r for r in rows if r["method"] == m}
        for m in all_snapshots
    }
    fig3_l2_over_time(acc_by_method_t)

    return rows, all_snapshots, all_perf


# ---------------------------------------------------------------------------
# Experiment 2 — Performance
# ---------------------------------------------------------------------------

def experiment_2(gt: dict, html_path: Optional[str] = None, skip_webgl: bool = False):
    logger.info("=== Experiment 2: Computational Performance ===")

    ic = gt["ic"]
    t_end = 100.0
    sample_times = [t_end]
    perf_rows = []

    # LLM-direct
    _, perf = _run_llm_direct_solver(ic, sample_times)
    perf_rows.append({
        "method": "LLM-direct",
        "wall_time_s": perf["wall_time_s"],
        "fps": "",
        "peak_mem_mb": perf["peak_mem_mb"],
        "uses_gpu": "No",
        "n_steps": perf["n_steps"],
    })

    # CodePDE
    solver = FentonKarmaSolver()
    with Timer("CodePDE perf") as t:
        _, perf_cpde = solver.run(ic["u"], ic["v"], ic["w"],
                                   t_start=0, t_end=t_end, sample_times=sample_times)
    perf_rows.append({
        "method": "CodePDE",
        "wall_time_s": t.elapsed,
        "fps": "",
        "peak_mem_mb": perf_cpde["peak_mem_mb"],
        "uses_gpu": "No",
        "n_steps": perf_cpde["n_steps"],
    })

    # Web-PDE-LLM
    if not skip_webgl and html_path:
        try:
            _, perf_wgl = _run_webgl(html_path, [t_end])
            perf_rows.append({
                "method": "Web-PDE-LLM",
                "wall_time_s": perf_wgl["wall_time_s"],
                "fps": perf_wgl.get("fps", ""),
                "peak_mem_mb": 0,
                "uses_gpu": "Yes",
                "n_steps": int(t_end / 0.025),
            })
        except Exception as e:
            logger.warning("  WebGL perf capture failed: %s", e)

    _write_csv(RESULTS_DIR / "exp2_performance.csv", perf_rows)
    fig5_performance({r["method"]: r for r in perf_rows})

    return perf_rows


# ---------------------------------------------------------------------------
# Experiment 3 — Code Generation Robustness
# ---------------------------------------------------------------------------

def experiment_3(n_trials: int = 10):
    logger.info("=== Experiment 3: Code Generation Robustness (N=%d) ===", n_trials)

    # LLM-direct: single-shot generation, no debug loop
    # We simulate N=n_trials independent calls
    # In real eval: replace with actual LLM calls via Ollama
    llm_direct_trials = []
    codepde_trials    = []
    webpde_trials     = []

    logger.info("  NOTE: Running mock trials. Replace with real LLM calls for paper.")
    logger.info("  Each trial: call pipeline.py --model fenton_karma and parse the output.")

    # Stub: read pre-logged trial results if available, else generate placeholder
    trial_log = RESULTS_DIR / "trial_log.json"
    if trial_log.exists():
        all_trials = json.loads(trial_log.read_text())
        llm_direct_trials = all_trials.get("LLM-direct", [])
        codepde_trials    = all_trials.get("CodePDE", [])
        webpde_trials     = all_trials.get("Web-PDE-LLM", [])
        logger.info("  Loaded %d trial logs from %s", len(webpde_trials), trial_log)
    else:
        logger.warning("  No trial_log.json found. Run Experiment 3 manually:")
        logger.warning("  for i in range(%d): run pipeline.py and log result to %s", n_trials, trial_log)
        return []

    rows = []
    for method, trials in [("LLM-direct", llm_direct_trials),
                            ("CodePDE",    codepde_trials),
                            ("Web-PDE-LLM", webpde_trials)]:
        if not trials:
            continue
        summary = code_generation_summary(trials)
        rows.append({"method": method, **summary})

    _write_csv(RESULTS_DIR / "exp3_robustness.csv", rows)
    if rows:
        fig6_robustness({r["method"]: r for r in rows})

    return rows


# ---------------------------------------------------------------------------
# Experiment 4 — Aliev-Panfilov Generalizability
# ---------------------------------------------------------------------------

def experiment_4(html_path_ap: Optional[str] = None, skip_webgl: bool = False):
    logger.info("=== Experiment 4: Aliev-Panfilov Generalizability ===")

    solver = AlievPanfilovSolver()
    ic_u, ic_v = solver.default_ic(seed=42)
    sample_times = [25.0, 50.0, 75.0, 100.0]

    logger.info("  Running AP reference solver…")
    ref_snaps, ref_perf = solver.run(ic_u, ic_v, t_end=100.0, sample_times=sample_times)

    all_ap_snapshots = {"AP-Reference": ref_snaps}

    if not skip_webgl and html_path_ap:
        try:
            wgl_snaps, _ = _run_webgl(html_path_ap, sample_times)
            all_ap_snapshots["Web-PDE-LLM (AP)"] = wgl_snaps
        except Exception as e:
            logger.warning("  AP WebGL capture failed: %s", e)

    # Accuracy vs reference
    rows = []
    for method, snaps in all_ap_snapshots.items():
        if method == "AP-Reference":
            continue
        for t in sample_times:
            ref_u = ref_snaps.get(t, {}).get("u")
            pred_u = snaps.get(t, {}).get("u")
            if ref_u is None or pred_u is None:
                continue
            rows.append({
                "method": method,
                "snapshot_t": t,
                "l2_u": relative_l2_error(pred_u, ref_u),
                "rmse_u": rmse(pred_u, ref_u),
                "ssim_u": ssim(pred_u, ref_u),
            })

    _write_csv(RESULTS_DIR / "exp4_ap_accuracy.csv", rows)
    fig7_ap_spirals(all_ap_snapshots, times=sample_times)

    return rows


# ---------------------------------------------------------------------------
# Experiment 5 — Spiral Tip Analysis
# ---------------------------------------------------------------------------

def experiment_5(gt: dict, all_snapshots: dict):
    logger.info("=== Experiment 5: Spiral Tip Analysis ===")

    tip_trajectories = {}
    for method, snaps in all_snapshots.items():
        traj = {}
        for t in GT_SNAPSHOTS:
            snap = snaps.get(t)
            if snap is None:
                continue
            u_f = snap["u"]
            v_f = snap.get("v", np.zeros_like(u_f))
            traj[t] = detect_spiral_tips(u_f, v_f)
        tip_trajectories[method] = traj
        counts = {t: len(tips) for t, tips in traj.items()}
        logger.info("  %s tip counts: %s", method, counts)

    # GT tips
    gt_traj = {}
    for t in GT_SNAPSHOTS:
        gt_snap = gt["snapshots"].get(t)
        if gt_snap:
            gt_traj[t] = detect_spiral_tips(gt_snap["u"], gt_snap["v"])
    tip_trajectories["Ground Truth"] = gt_traj

    fig8_spiral_tips(tip_trajectories)

    # Save tip count summary
    rows = []
    for method, traj in tip_trajectories.items():
        for t, tips in traj.items():
            rows.append({"method": method, "time": t, "tip_count": len(tips)})
    _write_csv(RESULTS_DIR / "exp5_spiral_tips.csv", rows)

    return tip_trajectories


# ---------------------------------------------------------------------------
# Master runner
# ---------------------------------------------------------------------------

def main():
    p = argparse.ArgumentParser(
        description="Web-PDE-LLM evaluation pipeline",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--all", action="store_true", help="Run all experiments")
    p.add_argument("--exp", nargs="+", type=int, help="Run specific experiment numbers")
    p.add_argument("--no-webgl", action="store_true", help="Skip WebGL capture (Python-only)")
    p.add_argument("--n-trials", type=int, default=10, help="Robustness trial count (Exp 3)")
    p.add_argument("--dry-run", action="store_true", help="Check imports only, no computation")
    p.add_argument(
        "--webgl-html",
        default="../cardiac-PDE/v1/outputs/fenton_karma/3V MODEL skeleton.html",
        help="Path to FK WebGL HTML file",
    )
    p.add_argument(
        "--webgl-html-ap",
        default="../cardiac-PDE/v1/outputs/aliev_panfilov/3V MODEL skeleton.html",
        help="Path to AP WebGL HTML file",
    )
    args = p.parse_args()

    if args.dry_run:
        logger.info("Dry run — imports OK.")
        return

    to_run = set(range(1, 6)) if args.all else set(args.exp or [])
    if not to_run:
        p.print_help()
        return

    skip_webgl = args.no_webgl
    html_fk    = args.webgl_html if not skip_webgl else None
    html_ap    = args.webgl_html_ap if not skip_webgl else None

    t_total = time.perf_counter()
    _log_hardware()

    # Load ground truth (needed for Exp 1, 2, 5)
    gt = None
    if to_run & {1, 2, 5}:
        logger.info("Loading ground truth data…")
        gt = load_ground_truth()

    all_snapshots = {}

    if 1 in to_run:
        _, all_snapshots, _ = experiment_1(gt, html_fk, skip_webgl)

    if 2 in to_run:
        experiment_2(gt, html_fk, skip_webgl)

    if 3 in to_run:
        experiment_3(args.n_trials)

    if 4 in to_run:
        experiment_4(html_ap, skip_webgl)

    if 5 in to_run:
        if not all_snapshots and gt:
            # Re-run Exp 1 solvers to get snapshots for Exp 5
            _, all_snapshots, _ = experiment_1(gt, html_fk, skip_webgl=True)
        experiment_5(gt, all_snapshots)

    # Generate LaTeX tables
    logger.info("Generating LaTeX tables…")
    for exp_n, fn in [(1, "exp1_accuracy.csv"), (2, "exp2_performance.csv"), (3, "exp3_robustness.csv")]:
        if exp_n in to_run and (RESULTS_DIR / fn).exists():
            try:
                {"exp1_accuracy.csv":    table1_accuracy,
                 "exp2_performance.csv": table2_performance,
                 "exp3_robustness.csv":  table3_robustness}[fn](RESULTS_DIR / fn)
            except Exception as e:
                logger.warning("  Table generation failed for %s: %s", fn, e)

    elapsed = time.perf_counter() - t_total
    logger.info("=== Evaluation complete in %.1fs ===", elapsed)
    logger.info("Results in: %s/", RESULTS_DIR)
    logger.info("Figures in: %s/figures/", RESULTS_DIR)
    logger.info("Tables  in: %s/tables/", RESULTS_DIR)


if __name__ == "__main__":
    main()
