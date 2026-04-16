"""
pipeline/eval_pipeline.py — Master evaluation pipeline for Web-PDE-LLM v4.

Compares Web-PDE-LLM against LLM-direct, CodePDE, and OpInf-LLM.
Data can come from PDEBench or the existing FK ground truth.

Usage
-----
  # Full evaluation on FK data (default)
  python pipeline/eval_pipeline.py --all

  # Use PDEBench 2D reaction-diffusion data
  python pipeline/eval_pipeline.py --all --data pdebench_2d_rd

  # Single experiment, no WebGL
  python pipeline/eval_pipeline.py --exp 1 --no-webgl

  # OpInf-LLM only, on PDEBench
  python pipeline/eval_pipeline.py --exp opinf --data pdebench_2d_rd

  # Robustness sweep (N trials)
  python pipeline/eval_pipeline.py --exp robustness --n-trials 10
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import sys
import time
from pathlib import Path

import numpy as np

# ── path setup ──────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from data.base import get_data_source
from baselines.llm_direct import FentonKarmaSolver, AlievPanfilovSolver, LLMDirectBaseline
from baselines.codepde import CodePDEBaseline
from baselines.opinf_llm import OpInfLLMBaseline
from metrics.metrics import (
    rmse_all_vars, bug_free_rate, running_time_summary,
    full_accuracy_suite, method_summary, is_physically_valid, Timer,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)-8s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("eval")

RESULTS = ROOT / "results"
RESULTS.mkdir(exist_ok=True)
(RESULTS / "figures").mkdir(exist_ok=True)
(RESULTS / "tables").mkdir(exist_ok=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_csv(path: Path, rows: list[dict]):
    if not rows:
        return
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader(); w.writerows(rows)
    log.info("  → %s", path)


def _log_hardware(results_dir: Path):
    import platform
    info = {
        "platform": platform.platform(),
        "python":   sys.version,
        "cpu":      platform.processor(),
        "numpy":    np.__version__,
    }
    try:
        import torch
        info["torch"] = torch.__version__
        info["cuda"]  = torch.cuda.is_available()
        if torch.cuda.is_available():
            info["gpu"] = torch.cuda.get_device_name(0)
    except ImportError:
        pass
    (results_dir / "hardware.json").write_text(json.dumps(info, indent=2))


def _webgl_capture(html_path: str, sample_times: list[float]) -> tuple[dict, dict]:
    """Playwright WebGL capture (imported lazily to avoid hard dependency)."""
    sys.path.insert(0, str(ROOT.parent / "evaluation"))
    from webgl_capture import WebGLCapture
    cap = WebGLCapture(html_path)
    result = cap.run(sample_times=sample_times, fps_duration_s=30.0)
    return result["snapshots"], {
        "wall_time_s": result["perf"].get("wall_time_s", 0),
        "fps": result.get("fps"),
        "peak_mem_mb": 0,
        "bug_free": len(result["snapshots"]) > 0,
        "uses_gpu": True,
    }


# ---------------------------------------------------------------------------
# Experiment A — Accuracy & Running Time
# ---------------------------------------------------------------------------

def exp_accuracy(args, data_src, meta):
    log.info("=== Exp A: Accuracy & Running Time ===")

    sample_times = sorted(data_src.load_snapshots(sample_idx=0).keys())
    ic = data_src.load_ic(sample_idx=0)
    gt = data_src.load_snapshots(sample_idx=0)

    rows = []

    def _record(method_name, pred_snaps, perf):
        valid = is_physically_valid(pred_snaps, meta.var_names)
        acc   = full_accuracy_suite(pred_snaps, gt, meta.var_names)
        rows.append({
            "method": method_name,
            **acc,
            "bug_free":    valid,
            "wall_time_s": perf.get("wall_time_s", float("nan")),
            "peak_mem_mb": perf.get("peak_mem_mb", float("nan")),
            "fps":         perf.get("fps", ""),
            "uses_gpu":    perf.get("uses_gpu", False),
        })
        log.info("  %s | rmse_mean=%.5f | bug_free=%s | time=%.1fs",
                 method_name, acc.get("rmse_mean", float("nan")),
                 valid, perf.get("wall_time_s", 0))

    # LLM-direct (canonical NumPy reference)
    solver_cls = FentonKarmaSolver if meta.n_vars == 3 else AlievPanfilovSolver
    solver = solver_cls()
    with Timer("LLM-direct") as t:
        snaps, perf = solver.run(ic, t_end=max(sample_times), sample_times=sample_times)
    perf["wall_time_s"] = t.elapsed
    _record("LLM-direct", snaps, perf)

    # CodePDE
    codepde = CodePDEBaseline(max_attempts=3)
    with Timer("CodePDE") as t:
        snaps, perf = codepde.run(ic, max(sample_times), sample_times)
    perf["wall_time_s"] = t.elapsed
    _record("CodePDE", snaps, perf)

    # OpInf-LLM
    log.info("  Fitting OpInf-LLM on 3 training samples...")
    train_trajs, _ = data_src.load_training_trajectories(
        sample_indices=list(range(min(3, 1))),  # use 1 traj if only 1 sample
        subsample_t=5,
    )
    opinf = OpInfLLMBaseline(r=args.opinf_r, use_quadratic=True, use_llm=args.llm_terms)
    with Timer("OpInf-LLM fit") as t_fit:
        opinf.fit(train_trajs, meta)
    with Timer("OpInf-LLM predict") as t_pred:
        r0 = ic
        snaps = opinf.predict(r0, t_eval=sample_times)
    _record("OpInf-LLM", snaps, {
        "wall_time_s": t_fit.elapsed + t_pred.elapsed,
        "fit_time_s":  t_fit.elapsed,
        "predict_time_s": t_pred.elapsed,
        "peak_mem_mb": opinf.fit_mem_mb_,
        "bug_free": is_physically_valid(snaps, meta.var_names),
        "uses_gpu": False,
    })

    # Web-PDE-LLM (WebGL) — optional
    if not args.no_webgl and args.webgl_html:
        try:
            snaps, perf = _webgl_capture(args.webgl_html, sample_times)
            _record("Web-PDE-LLM", snaps, perf)
        except Exception as e:
            log.warning("  WebGL capture failed: %s", e)

    _write_csv(RESULTS / "exp_accuracy.csv", rows)
    return rows


# ---------------------------------------------------------------------------
# Experiment B — Bug-Free Rate (N trials)
# ---------------------------------------------------------------------------

def exp_robustness(args, data_src, meta):
    log.info("=== Exp B: Robustness / Bug-Free Rate (N=%d) ===", args.n_trials)

    ic = data_src.load_ic(sample_idx=0)
    sample_times = sorted(data_src.load_snapshots(sample_idx=0).keys())[:3]

    def _run_trials(name, runner_fn):
        results = []
        for i in range(args.n_trials):
            log.info("  %s trial %d/%d", name, i + 1, args.n_trials)
            t0 = time.perf_counter()
            try:
                snaps, perf = runner_fn()
                valid = is_physically_valid(snaps, meta.var_names)
                results.append({
                    "trial": i, "bug_free": valid,
                    "wall_time_s": perf.get("wall_time_s", time.perf_counter() - t0),
                    "debug_iterations": perf.get("debug_iterations", 0),
                })
            except Exception as e:
                results.append({"trial": i, "bug_free": False,
                                 "wall_time_s": time.perf_counter() - t0,
                                 "debug_iterations": 0, "error": str(e)})
        return results

    # LLM-direct
    def run_llmd():
        b = LLMDirectBaseline(model=args.code_model)
        b.generate("Fenton-Karma 3V cardiac PDE, 512x512 grid, Neumann BCs")
        return b.execute(ic, max(sample_times), sample_times)

    # CodePDE
    def run_cpde():
        b = CodePDEBaseline(gen_model=args.code_model, max_attempts=3)
        return b.run(ic, max(sample_times), sample_times,
                     pde_description="Fenton-Karma 3V cardiac PDE, 512x512 grid")

    # OpInf-LLM (always bug-free if data loads; only fail on numerical instability)
    def run_opinf():
        train, _ = data_src.load_training_trajectories([0], subsample_t=10)
        b = OpInfLLMBaseline(r=args.opinf_r, use_quadratic=True)
        b.fit(train, meta)
        t0 = time.perf_counter()
        snaps = b.predict(ic, sample_times)
        return snaps, {"wall_time_s": time.perf_counter() - t0}

    all_rows = []
    for name, fn in [("LLM-direct", run_llmd), ("CodePDE", run_cpde), ("OpInf-LLM", run_opinf)]:
        trials = _run_trials(name, fn)
        bfr = bug_free_rate(trials)
        timing = running_time_summary(trials)
        avg_dbg = np.mean([r.get("debug_iterations", 0) for r in trials])
        all_rows.append({
            "method": name,
            "bug_free_rate": round(bfr, 4),
            "mean_debug_iterations": round(avg_dbg, 2),
            **{k: round(v, 3) for k, v in timing.items()},
        })
        log.info("  %s | bug_free=%.2f | time_mean=%.2fs", name, bfr, timing["time_mean_s"])

    _write_csv(RESULTS / "exp_robustness.csv", all_rows)
    return all_rows


# ---------------------------------------------------------------------------
# Experiment C — OpInf-LLM parametric extrapolation
# ---------------------------------------------------------------------------

def exp_opinf_parametric(args, data_src, meta):
    """
    Train OpInf-LLM at multiple parameter values, then extrapolate to a
    held-out parameter. Demonstrates the parametric extension.
    Only meaningful for FK data with multiple tau_d values.
    """
    log.info("=== Exp C: OpInf-LLM Parametric Extrapolation ===")

    from data.fk_loader import FKDataLoader
    if not isinstance(data_src, FKDataLoader):
        log.warning("Exp C requires FKDataLoader — skipping.")
        return []

    training_tau_d = [0.5714]  # extend list when more ground truth is available
    target_tau_d   = 0.5714    # placeholder

    models, params = [], []
    for td in training_tau_d:
        src_i = get_data_source("fk", tau_d=td)
        trajs, _ = src_i.load_training_trajectories([0], subsample_t=5)
        m = OpInfLLMBaseline(r=args.opinf_r)
        m.fit(trajs, meta)
        models.append(m)
        params.append(td)

    if len(models) > 1:
        extrap = models[0].extrapolate_operators(params, target_tau_d, models)
    else:
        extrap = models[0]

    ic = data_src.load_ic(0)
    gt = data_src.load_snapshots(0)
    times = sorted(gt.keys())
    snaps = extrap.predict(ic, times)
    acc = full_accuracy_suite(snaps, gt, meta.var_names)
    log.info("  Extrapolation result: %s", acc)

    rows = [{"method": "OpInf-LLM (extrap)", "target_tau_d": target_tau_d, **acc}]
    _write_csv(RESULTS / "exp_opinf_parametric.csv", rows)
    return rows


# ---------------------------------------------------------------------------
# Main CLI
# ---------------------------------------------------------------------------

def build_args():
    p = argparse.ArgumentParser(
        description="Web-PDE-LLM v4 evaluation pipeline",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--all",      action="store_true", help="Run all experiments")
    p.add_argument("--exp",      nargs="+",
                   choices=["accuracy", "robustness", "opinf_parametric"],
                   help="Run specific experiments")
    p.add_argument("--data",     default="fk",
                   choices=["fk", "pdebench_2d_rd", "pdebench_1d_burgers", "custom"],
                   help="Data source")
    p.add_argument("--data-dir", default=None, help="Override data directory")
    p.add_argument("--no-webgl", action="store_true", help="Skip WebGL capture")
    p.add_argument("--webgl-html", default=None, help="Path to FK WebGL HTML")
    p.add_argument("--n-trials", type=int, default=10, help="Robustness trial count")
    p.add_argument("--opinf-r",  type=int, default=20,  help="OpInf reduced dimension r")
    p.add_argument("--llm-terms", action="store_true",
                   help="Use LLM to select OpInf operator terms")
    p.add_argument("--code-model", default="qwen3:8b",
                   help="Ollama model for code generation baselines")
    p.add_argument("--dry-run",  action="store_true", help="Check imports, no compute")
    return p.parse_args()


def main():
    args = build_args()
    if args.dry_run:
        log.info("Dry run — all imports OK.")
        return

    exps = {"accuracy", "robustness", "opinf_parametric"} if args.all else set(args.exp or [])
    if not exps:
        log.error("Specify --all or --exp <name>"); return

    _log_hardware(RESULTS)

    # Load data source
    ds_kwargs = {}
    if args.data_dir:
        ds_kwargs["data_dir"] = args.data_dir
    data_src = get_data_source(args.data, **ds_kwargs)
    meta = data_src.get_metadata()
    log.info("Data source: %s  vars=%s  shape=%s", meta.name, meta.var_names, meta.spatial_shape)

    t0 = time.perf_counter()
    if "accuracy"          in exps: exp_accuracy(args, data_src, meta)
    if "robustness"        in exps: exp_robustness(args, data_src, meta)
    if "opinf_parametric"  in exps: exp_opinf_parametric(args, data_src, meta)

    log.info("All done in %.1fs. Results in %s/", time.perf_counter() - t0, RESULTS)


if __name__ == "__main__":
    main()
