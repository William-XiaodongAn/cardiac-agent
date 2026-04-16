"""
metrics/metrics.py — Evaluation metrics for the Web-PDE-LLM paper.

Primary metrics (required by user):
  - RMSE
  - Bug-free rate
  - Running time

Additional metrics for completeness:
  - Relative L2 error
  - Max absolute error
  - SSIM
  - Action potential duration (APD)
  - Conduction velocity (CV)
  - Spiral tip count
"""

from __future__ import annotations
import time
import numpy as np
from typing import Optional


# ============================================================
# 1. RMSE (primary)
# ============================================================

def rmse(pred: np.ndarray, gt: np.ndarray) -> float:
    """Root Mean Squared Error."""
    return float(np.sqrt(np.mean((pred - gt) ** 2)))


def rmse_all_vars(
    pred_snaps: dict[float, dict[str, np.ndarray]],
    gt_snaps:   dict[float, dict[str, np.ndarray]],
    var_names:  list[str],
) -> dict[str, float]:
    """
    Mean RMSE over all shared snapshots and variables.
    Returns {"rmse_<var>": float, "rmse_mean": float}.
    """
    shared_times = sorted(set(pred_snaps) & set(gt_snaps))
    per_var = {v: [] for v in var_names}

    for t in shared_times:
        for v in var_names:
            if v in pred_snaps[t] and v in gt_snaps[t]:
                per_var[v].append(rmse(pred_snaps[t][v], gt_snaps[t][v]))

    result = {f"rmse_{v}": float(np.mean(vals)) if vals else float("nan")
              for v, vals in per_var.items()}
    all_vals = [x for vals in per_var.values() for x in vals]
    result["rmse_mean"] = float(np.mean(all_vals)) if all_vals else float("nan")
    return result


# ============================================================
# 2. Bug-free rate (primary)
# ============================================================

def is_physically_valid(
    snaps: dict[float, dict[str, np.ndarray]],
    var_names: list[str],
    valid_range: tuple[float, float] = (0.0, 1.0),
) -> bool:
    """
    A run is considered bug-free (physically valid) if:
      1. At least one snapshot was produced.
      2. All values are finite (no NaN or Inf).
      3. All values fall within valid_range.
    """
    if not snaps:
        return False
    lo, hi = valid_range
    for snap in snaps.values():
        for v in var_names:
            if v not in snap:
                return False
            arr = snap[v]
            if not np.all(np.isfinite(arr)):
                return False
            if np.any(arr < lo - 1e-3) or np.any(arr > hi + 1e-3):
                return False
    return True


def bug_free_rate(trial_results: list[dict]) -> float:
    """
    Fraction of trials where bug_free=True.
    Each element of trial_results should have a "bug_free" key.
    """
    if not trial_results:
        return float("nan")
    return float(sum(1 for r in trial_results if r.get("bug_free", False)) / len(trial_results))


# ============================================================
# 3. Running time (primary)
# ============================================================

class Timer:
    """Context manager for wall-clock timing."""
    def __init__(self, label: str = ""):
        self.label = label
        self.elapsed: float = 0.0

    def __enter__(self):
        self._t0 = time.perf_counter()
        return self

    def __exit__(self, *_):
        self.elapsed = time.perf_counter() - self._t0
        if self.label:
            print(f"  [{self.label}] {self.elapsed:.3f}s")


def running_time_summary(perf_records: list[dict]) -> dict[str, float]:
    """
    Summarise running time across multiple trials.
    Each record should have "wall_time_s".
    """
    times = [r["wall_time_s"] for r in perf_records if "wall_time_s" in r]
    if not times:
        return {"time_mean_s": float("nan"), "time_std_s": float("nan")}
    return {
        "time_mean_s": float(np.mean(times)),
        "time_std_s":  float(np.std(times)),
        "time_min_s":  float(np.min(times)),
        "time_max_s":  float(np.max(times)),
    }


# ============================================================
# 4. Additional accuracy metrics
# ============================================================

def relative_l2_error(pred: np.ndarray, gt: np.ndarray) -> float:
    return float(np.linalg.norm(pred - gt) / (np.linalg.norm(gt) + 1e-10))


def max_absolute_error(pred: np.ndarray, gt: np.ndarray) -> float:
    return float(np.max(np.abs(pred - gt)))


def ssim(pred: np.ndarray, gt: np.ndarray, data_range: float = 1.0) -> float:
    try:
        from skimage.metrics import structural_similarity
        return float(structural_similarity(pred, gt, data_range=data_range))
    except ImportError:
        return float("nan")


def full_accuracy_suite(
    pred_snaps: dict[float, dict[str, np.ndarray]],
    gt_snaps:   dict[float, dict[str, np.ndarray]],
    var_names:  list[str],
) -> dict[str, float]:
    """
    Compute RMSE, L2, MaxAE, SSIM for all shared snapshots and variables.
    Returns a flat dict with keys like rmse_u, l2_u, mae_u, ssim_u, rmse_mean, etc.
    """
    shared = sorted(set(pred_snaps) & set(gt_snaps))
    per_var: dict[str, dict[str, list]] = {
        v: {"rmse": [], "l2": [], "mae": [], "ssim": []}
        for v in var_names
    }

    for t in shared:
        for v in var_names:
            if v in pred_snaps[t] and v in gt_snaps[t]:
                p, g = pred_snaps[t][v], gt_snaps[t][v]
                per_var[v]["rmse"].append(rmse(p, g))
                per_var[v]["l2"].append(relative_l2_error(p, g))
                per_var[v]["mae"].append(max_absolute_error(p, g))
                per_var[v]["ssim"].append(ssim(p, g))

    result = {}
    for v, metrics in per_var.items():
        for name, vals in metrics.items():
            result[f"{name}_{v}"] = float(np.mean(vals)) if vals else float("nan")

    # Mean across all variables
    result["rmse_mean"] = float(np.nanmean([result[f"rmse_{v}"] for v in var_names]))
    result["l2_mean"]   = float(np.nanmean([result[f"l2_{v}"]   for v in var_names]))
    return result


# ============================================================
# 5. Physiological metrics (secondary)
# ============================================================

def action_potential_duration(
    u_trace: np.ndarray,
    dt: float = 0.025,
    threshold: float = 0.13,
    min_peak: float = 0.5,
) -> float:
    above = (u_trace > threshold).astype(int)
    diff  = np.diff(above)
    rises = np.where(diff ==  1)[0]
    falls = np.where(diff == -1)[0]
    for r in rises:
        valid = falls[falls > r]
        if len(valid) and np.max(u_trace[r: valid[0]]) > min_peak:
            return float((valid[0] - r) * dt)
    return float("nan")


def conduction_velocity(
    u1: np.ndarray, u2: np.ndarray,
    dt_between: float, dx: float = 0.0390625,
    threshold: float = 0.13,
) -> float:
    def front(field):
        cols = np.any(field > threshold, axis=0)
        idx  = np.where(cols)[0]
        return float(idx[0]) if len(idx) else None
    x1, x2 = front(u1), front(u2)
    if x1 is None or x2 is None or dt_between <= 0:
        return float("nan")
    return abs(x2 - x1) * dx / dt_between


def detect_spiral_tips(u: np.ndarray, v: np.ndarray,
                        v_c: float = 0.13, v_v: float = 0.04) -> np.ndarray:
    from scipy.ndimage import gaussian_filter, label
    dist = np.sqrt((u - v_c) ** 2 + (v - v_v) ** 2)
    mask = gaussian_filter((dist < 0.05).astype(float), sigma=2.0) > 0.3
    labeled, n = label(mask)
    tips = [np.argwhere(labeled == i).mean(axis=0) for i in range(1, n + 1)]
    return np.array(tips) if tips else np.empty((0, 2))


# ============================================================
# 6. Aggregate summary for one method
# ============================================================

def method_summary(
    pred_snaps:     dict[float, dict[str, np.ndarray]],
    gt_snaps:       dict[float, dict[str, np.ndarray]],
    perf:           dict,
    var_names:      list[str],
    is_bug_free:    bool = True,
) -> dict:
    """
    Single dict covering all primary and secondary metrics for one method run.
    """
    acc = full_accuracy_suite(pred_snaps, gt_snaps, var_names)
    return {
        **acc,
        "bug_free":    is_bug_free,
        "wall_time_s": perf.get("wall_time_s", float("nan")),
        "peak_mem_mb": perf.get("peak_mem_mb", float("nan")),
        "fps":         perf.get("fps", None),
    }
