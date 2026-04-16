"""
metrics.py — All evaluation metrics for the Web-PDE-LLM paper.

All functions accept numpy arrays of shape (H, W) or (T, H, W).
"""

import numpy as np
from typing import Tuple, Dict, Optional


# ---------------------------------------------------------------------------
# 3.1 Numerical accuracy
# ---------------------------------------------------------------------------

def relative_l2_error(pred: np.ndarray, gt: np.ndarray) -> float:
    """Relative L2 error: ‖pred − gt‖₂ / ‖gt‖₂."""
    return float(np.linalg.norm(pred - gt) / (np.linalg.norm(gt) + 1e-10))


def rmse(pred: np.ndarray, gt: np.ndarray) -> float:
    """Root mean squared error."""
    return float(np.sqrt(np.mean((pred - gt) ** 2)))


def max_absolute_error(pred: np.ndarray, gt: np.ndarray) -> float:
    """Maximum absolute pointwise error."""
    return float(np.max(np.abs(pred - gt)))


def ssim(pred: np.ndarray, gt: np.ndarray, data_range: float = 1.0) -> float:
    """
    Structural Similarity Index (Wang et al. 2004).
    Computed on 2D spatial fields. Uses an 11×11 Gaussian window.
    """
    from skimage.metrics import structural_similarity
    return float(structural_similarity(pred, gt, data_range=data_range))


def accuracy_suite(
    pred: np.ndarray,
    gt: np.ndarray,
    var_name: str = "u",
) -> Dict[str, float]:
    """
    Run all accuracy metrics on a single (H, W) field.
    Returns a flat dict ready for DataFrame construction.
    """
    return {
        f"l2_{var_name}":    relative_l2_error(pred, gt),
        f"rmse_{var_name}":  rmse(pred, gt),
        f"mae_{var_name}":   max_absolute_error(pred, gt),
        f"ssim_{var_name}":  ssim(pred, gt),
    }


def accuracy_suite_uvw(
    pred_u: np.ndarray, gt_u: np.ndarray,
    pred_v: np.ndarray, gt_v: np.ndarray,
    pred_w: np.ndarray, gt_w: np.ndarray,
) -> Dict[str, float]:
    """Compute full accuracy suite for all three FK state variables."""
    result = {}
    for pred, gt, name in [(pred_u, gt_u, "u"), (pred_v, gt_v, "v"), (pred_w, gt_w, "w")]:
        result.update(accuracy_suite(pred, gt, name))
    return result


# ---------------------------------------------------------------------------
# 3.2 Physiological metrics
# ---------------------------------------------------------------------------

def action_potential_duration(
    u_trace: np.ndarray,
    dt: float = 0.025,
    threshold: float = 0.13,
    min_peak: float = 0.5,
) -> float:
    """
    Estimate Action Potential Duration (APD) from a voltage time series.

    Detects the first complete excitation cycle where u > threshold,
    with peak u > min_peak (to exclude sub-threshold events).

    Returns APD in simulation time units. Returns NaN if no AP detected.
    """
    above = (u_trace > threshold).astype(int)
    transitions = np.diff(above)
    rises  = np.where(transitions ==  1)[0]
    falls  = np.where(transitions == -1)[0]

    for r in rises:
        valid_falls = falls[falls > r]
        if len(valid_falls) == 0:
            continue
        f = valid_falls[0]
        if np.max(u_trace[r:f]) > min_peak:
            return float((f - r) * dt)

    return float("nan")


def conduction_velocity(
    u_field_t1: np.ndarray,
    u_field_t2: np.ndarray,
    dt_between: float,
    dx: float = 0.0390625,
    threshold: float = 0.13,
) -> float:
    """
    Estimate planar wave conduction velocity (CV) in spatial units / time unit.

    Finds the wavefront position (first column where u > threshold) in two
    consecutive spatial snapshots and divides the distance by elapsed time.
    Returns NaN if a clean wavefront cannot be identified.
    """
    def wavefront_x(field):
        cols_above = np.any(field > threshold, axis=0)
        indices = np.where(cols_above)[0]
        return float(indices[0]) if len(indices) > 0 else None

    x1 = wavefront_x(u_field_t1)
    x2 = wavefront_x(u_field_t2)
    if x1 is None or x2 is None:
        return float("nan")
    distance = abs(x2 - x1) * dx
    return float(distance / dt_between) if dt_between > 0 else float("nan")


def peak_voltage(u_trace: np.ndarray) -> float:
    """Maximum transmembrane potential over time."""
    return float(np.max(u_trace))


def resting_voltage(u_trace: np.ndarray, tail_fraction: float = 0.2) -> float:
    """
    Resting (diastolic) voltage: mean of the final tail_fraction of the trace,
    which should be in steady repolarized state.
    """
    tail_len = max(1, int(len(u_trace) * tail_fraction))
    return float(np.mean(u_trace[-tail_len:]))


# ---------------------------------------------------------------------------
# 3.2b Spiral wave analysis
# ---------------------------------------------------------------------------

def detect_spiral_tips(
    u_field: np.ndarray,
    v_field: np.ndarray,
    v_c: float = 0.13,
    v_v: float = 0.04,
) -> np.ndarray:
    """
    Detect spiral wave tip locations using the Fenton-Karma phase singularity
    criterion: pixels where u ≈ V_c and v ≈ V_v simultaneously.

    Returns an (N, 2) array of (row, col) tip coordinates.
    Applies a small Gaussian blur first to reduce noise.
    """
    from scipy.ndimage import gaussian_filter, label

    # Proximity to the (V_c, V_v) saddle point in (u, v) phase space
    dist = np.sqrt((u_field - v_c) ** 2 + (v_field - v_v) ** 2)
    threshold = 0.05
    tip_mask = (dist < threshold).astype(float)
    tip_smooth = gaussian_filter(tip_mask, sigma=2.0)
    binary = tip_smooth > 0.3

    labeled, n_features = label(binary)
    tips = []
    for i in range(1, n_features + 1):
        coords = np.argwhere(labeled == i)
        tips.append(coords.mean(axis=0))  # centroid of each cluster

    return np.array(tips) if tips else np.empty((0, 2))


def spiral_tip_count(u_field: np.ndarray, v_field: np.ndarray) -> int:
    """Number of spiral wave tips in a snapshot."""
    return len(detect_spiral_tips(u_field, v_field))


# ---------------------------------------------------------------------------
# 3.3 Code generation robustness (for aggregation scripts)
# ---------------------------------------------------------------------------

def code_generation_summary(trials: list[dict]) -> Dict[str, float]:
    """
    Aggregate code-generation trial results.

    Each trial dict should have:
        - "compiled": bool
        - "debug_iterations": int
        - "validation_passed": bool
        - "physically_plausible": bool (u stays in [0,1])

    Returns aggregated stats.
    """
    n = len(trials)
    if n == 0:
        return {}
    return {
        "first_gen_success_rate": sum(t["compiled"] and t["debug_iterations"] == 0 for t in trials) / n,
        "compilation_success_rate": sum(t["compiled"] for t in trials) / n,
        "mean_debug_iterations": np.mean([t["debug_iterations"] for t in trials]),
        "validation_pass_rate": sum(t["validation_passed"] for t in trials) / n,
        "physical_plausibility_rate": sum(t["physically_plausible"] for t in trials) / n,
    }


# ---------------------------------------------------------------------------
# 3.4 Performance timing
# ---------------------------------------------------------------------------

class Timer:
    """Context manager for wall-clock timing."""

    def __init__(self, label: str = ""):
        self.label = label
        self.elapsed: float = 0.0

    def __enter__(self):
        import time
        self._start = time.perf_counter()
        return self

    def __exit__(self, *_):
        import time
        self.elapsed = time.perf_counter() - self._start
        if self.label:
            print(f"  [{self.label}] {self.elapsed:.2f}s")
