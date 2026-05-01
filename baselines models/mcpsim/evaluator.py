import os
import re
import numpy as np


def load_fk_ground_truth(data_dir: str):
    npz_path = os.path.join(data_dir, "UVW_array_data.npz")
    data = np.load(npz_path)

    U_all = data["U"]
    V_all = data["V"]
    W_all = data["W"]

    csv_files = [
        f
        for f in os.listdir(data_dir)
        if f.startswith("sim_data_") and f.endswith(".csv")
    ]
    times = []
    for f in csv_files:
        match = re.findall(r"[-+]?\d*\.\d+|\d+", f)
        if match:
            times.append(float(match[0]))
    times.sort()

    t_relative = [t - min(times) for t in times]

    u0 = U_all[0:1].copy()
    v0 = V_all[0:1].copy()
    w0 = W_all[0:1].copy()

    return {
        "u0": u0,
        "v0": v0,
        "w0": w0,
        "t_coordinate": np.array(t_relative),
        "U_ground_truth": U_all,
        "V_ground_truth": V_all,
        "W_ground_truth": W_all,
    }


def compute_nrmse(pred: np.ndarray, truth: np.ndarray) -> float:
    if pred is None or not np.all(np.isfinite(pred)):
        return 1e10
    if pred.shape != truth.shape:
        min_len = min(pred.shape[0], truth.shape[0])
        pred = pred[:min_len]
        truth = truth[:min_len]
    rmse = np.sqrt(np.mean((pred - truth) ** 2))
    norm = np.sqrt(np.mean(truth**2))
    if norm < 1e-12:
        return float(rmse)
    return float(rmse / norm)


def evaluate_fk(result: dict, ground_truth: dict) -> dict:
    u_pred = result["u"]
    v_pred = result["v"]
    w_pred = result["w"]

    U_gt = ground_truth["U_ground_truth"]
    V_gt = ground_truth["V_ground_truth"]
    W_gt = ground_truth["W_ground_truth"]

    u_pred_0 = u_pred[0] if u_pred.ndim == 4 else u_pred
    v_pred_0 = v_pred[0] if v_pred.ndim == 4 else v_pred
    w_pred_0 = w_pred[0] if w_pred.ndim == 4 else w_pred

    nrmse_u = compute_nrmse(u_pred_0, U_gt)
    nrmse_v = compute_nrmse(v_pred_0, V_gt)
    nrmse_w = compute_nrmse(w_pred_0, W_gt)

    nrmse_u_final = compute_nrmse(
        u_pred_0[-1] if u_pred_0.ndim >= 2 else u_pred_0,
        U_gt[-1],
    )

    return {
        "nrmse_u": nrmse_u,
        "nrmse_v": nrmse_v,
        "nrmse_w": nrmse_w,
        "nrmse_u_final": nrmse_u_final,
        "nrmse_avg": (nrmse_u + nrmse_v + nrmse_w) / 3,
    }
