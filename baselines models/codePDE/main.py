#!/usr/bin/env python3
"""
CodePDE Baseline: LLM-generated Python PDE solver with iterative debugging.

Mirrors the CodePDE paper approach:
  1. Send PDE description + solver template to LLM.
  2. Extract and execute the generated Python solver.
  3. Evaluate against ground truth.
  4. If error or high nRMSE, feed context back to LLM for debugging.
  5. Repeat up to --max-debug-rounds times.
"""
import argparse
import json
import os
import sys
import time

import numpy as np

import llm_client
import prompts
import pde_descriptions
import executor
import evaluator


SOLVER_TEMPLATE = """\
import numpy as np

def solver(u0_batch, v0_batch, w0_batch, t_coordinate, tau_d):
    \"\"\"Solves the Fenton-Karma 3V model.

    Args:
        u0_batch (np.ndarray): Initial condition [batch_size, N, N].
        v0_batch (np.ndarray): Initial condition [batch_size, N, N].
        w0_batch (np.ndarray): Initial condition [batch_size, N, N].
        t_coordinate (np.ndarray): Time coordinates [T+1], starting at t_0=0.
        tau_d (float): The tau_d parameter.

    Returns:
        u_pred (np.ndarray): [batch_size, len(t_coordinate), N, N].
        v_pred (np.ndarray): [batch_size, len(t_coordinate), N, N].
        w_pred (np.ndarray): [batch_size, len(t_coordinate), N, N].
    \"\"\"
    # TODO: Implement the solver
    pass
"""


def run_pipeline(
    llm_model: str,
    data_dir: str,
    tau_d: float,
    max_debug_rounds: int,
    output_dir: str,
    timeout: int,
):
    os.makedirs(output_dir, exist_ok=True)

    print(f"Loading ground truth from {data_dir} ...")
    gt = evaluator.load_fk_ground_truth(data_dir)
    print(
        f"  IC shape: {gt['u0'].shape}, "
        f"t_coordinate: {gt['t_coordinate']}, "
        f"ground truth shape: {gt['U_ground_truth'].shape}"
    )

    pde_desc = pde_descriptions.fk_description.format(tau_d=tau_d)
    gen_prompt = prompts.CODE_GENERATION_PROMPT.format(
        pde_description=pde_desc,
        solver_template=SOLVER_TEMPLATE,
    )

    print(f"\n[Step 1] Generating solver with {llm_model} ...")
    t0 = time.time()
    raw_response = llm_client.chat(llm_model, prompts.SYSTEM_PROMPT, gen_prompt)
    gen_time = time.time() - t0
    print(f"  LLM response received in {gen_time:.1f}s ({len(raw_response)} chars)")

    code = executor.extract_code(raw_response)

    with open(os.path.join(output_dir, "generated_code_v0.py"), "w") as f:
        f.write(code)
    with open(os.path.join(output_dir, "raw_response_v0.md"), "w") as f:
        f.write(raw_response)

    best_nrmse = 1e10
    best_code = code
    best_version = 0

    for attempt in range(max_debug_rounds + 1):
        version_tag = f"v{attempt}"
        print(f"\n[Step 2] Executing solver ({version_tag}) ...")

        t0 = time.time()
        result, stdout, stderr = executor.run_solver(
            code,
            gt["u0"],
            gt["v0"],
            gt["w0"],
            gt["t_coordinate"],
            tau_d,
            timeout=timeout,
        )
        exec_time = time.time() - t0

        if stdout:
            stdout_preview = stdout[:500] + ("..." if len(stdout) > 500 else "")
            print(f"  stdout: {stdout_preview}")

        if result is None:
            print(f"  EXECUTION FAILED ({exec_time:.1f}s)")
            error_preview = stderr[:1000] if stderr else "unknown error"
            print(f"  error: {error_preview}")

            metrics = {
                "version": version_tag,
                "status": "execution_error",
                "exec_time_s": exec_time,
                "error": stderr[:2000],
            }
            _save_metrics(output_dir, version_tag, metrics)

            if attempt < max_debug_rounds:
                print(f"\n[Step 3] Debugging with {llm_model} (round {attempt + 1}/{max_debug_rounds}) ...")
                debug_prompt = prompts.DEBUG_EXECUTION_ERROR_PROMPT.format(
                    code_output=stdout[:2000],
                    error_message=stderr[:2000],
                    code=code,
                )
                raw_response = llm_client.chat(
                    llm_model, prompts.SYSTEM_PROMPT, debug_prompt
                )
                code = executor.extract_code(raw_response)
                with open(
                    os.path.join(output_dir, f"generated_code_{version_tag}_debug.py"),
                    "w",
                ) as f:
                    f.write(code)
            continue

        print(f"  Execution succeeded ({exec_time:.1f}s)")
        print(
            f"  Output shapes: u={result['u'].shape}, v={result['v'].shape}, w={result['w'].shape}"
        )

        metrics_dict = evaluator.evaluate_fk(result, gt)
        metrics_dict.update(
            {
                "version": version_tag,
                "status": "success",
                "exec_time_s": exec_time,
            }
        )
        _save_metrics(output_dir, version_tag, metrics_dict)

        nrmse = metrics_dict["nrmse_u_final"]
        print(f"  nRMSE(u, final): {nrmse:.6f}")
        print(f"  nRMSE(u, all):   {metrics_dict['nrmse_u']:.6f}")
        print(f"  nRMSE(v, all):   {metrics_dict['nrmse_v']:.6f}")
        print(f"  nRMSE(w, all):   {metrics_dict['nrmse_w']:.6f}")

        if nrmse < best_nrmse:
            best_nrmse = nrmse
            best_code = code
            best_version = attempt

        if nrmse < 0.1:
            print(f"\n  nRMSE < 0.1 — solver is accurate enough. Stopping.")
            break

        if attempt < max_debug_rounds:
            print(
                f"\n[Step 3] nRMSE too high. Debugging with {llm_model} "
                f"(round {attempt + 1}/{max_debug_rounds}) ..."
            )
            debug_prompt = prompts.DEBUG_NAN_INF_PROMPT.format(
                nrmse=nrmse,
                code_output=stdout[:2000],
                code=code,
            )
            raw_response = llm_client.chat(
                llm_model, prompts.SYSTEM_PROMPT, debug_prompt
            )
            code = executor.extract_code(raw_response)
            with open(
                os.path.join(output_dir, f"generated_code_{version_tag}_debug.py"), "w"
            ) as f:
                f.write(code)

    with open(os.path.join(output_dir, "best_solver.py"), "w") as f:
        f.write(best_code)

    summary = {
        "llm_model": llm_model,
        "tau_d": tau_d,
        "best_version": f"v{best_version}",
        "best_nrmse_u_final": best_nrmse,
        "total_attempts": min(attempt + 1, max_debug_rounds + 1),
        "bug_free": best_nrmse < 1e10,
    }
    with open(os.path.join(output_dir, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"  Model:        {llm_model}")
    print(f"  Best version: v{best_version}")
    print(f"  Best nRMSE:   {best_nrmse:.6f}")
    print(f"  Bug-free:     {best_nrmse < 1e10}")
    print(f"  Results in:   {output_dir}")
    print(f"{'='*60}")

    return summary


REFERENCE_SOLVER = """\
import numpy as np

def solver(u0_batch, v0_batch, w0_batch, t_coordinate, tau_d):
    D = 0.001; C_m = 1.0; tau_pv = 7.99; tau_v1 = 9.8; tau_v2 = 312.5
    tau_pw = 870.0; tau_mw = 41.0; tau_0 = 12.5; tau_r = 33.83
    tau_si = 29.0; k = 10.0; V_csi = 0.861; V_c = 0.13; V_v = 0.04
    dt = 0.025
    N = u0_batch.shape[-1]
    dx = 10.0 / N

    u = u0_batch.copy().astype(np.float64)
    v = v0_batch.copy().astype(np.float64)
    w = w0_batch.copy().astype(np.float64)

    results_u = [u.copy()]
    results_v = [v.copy()]
    results_w = [w.copy()]

    current_t = 0.0
    for target_t in t_coordinate[1:]:
        n_steps = int(round((target_t - current_t) / dt))
        for _ in range(n_steps):
            u_pad = np.pad(u, ((0,0),(1,1),(1,1)), mode='edge')
            lap = (u_pad[:, 2:, 1:-1] + u_pad[:, :-2, 1:-1] +
                   u_pad[:, 1:-1, 2:] + u_pad[:, 1:-1, :-2] - 4*u) / dx**2

            H_uc = (u >= V_c).astype(np.float64)
            H_uv = (u >= V_v).astype(np.float64)
            I_fi = -v * H_uc * (u - V_c) * (1 - u) / tau_d
            I_so = u * (1 - H_uc) / tau_0 + H_uc / tau_r
            I_si = -w * (1 + np.tanh(k * (u - V_csi))) / (2 * tau_si)

            u = u + dt * (D * lap - (I_fi + I_so + I_si) / C_m)

            tau_mv = (1 - H_uv) * tau_v1 + H_uv * tau_v2
            v = v + dt * np.where(u < V_c, (1-v)/tau_mv, -v/tau_pv)
            w = w + dt * np.where(u < V_c, (1-w)/tau_mw, -w/tau_pw)
        current_t = target_t
        results_u.append(u.copy())
        results_v.append(v.copy())
        results_w.append(w.copy())
        print(f't={target_t:.0f}')

    return (np.stack(results_u, axis=1),
            np.stack(results_v, axis=1),
            np.stack(results_w, axis=1))
"""


def run_test(data_dir: str, tau_d: float, output_dir: str, timeout: int):
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 60)
    print("TEST MODE: Running pipeline with reference solver (no LLM)")
    print("=" * 60)

    print(f"\nLoading ground truth from {data_dir} ...")
    gt = evaluator.load_fk_ground_truth(data_dir)
    print(f"  IC shape: {gt['u0'].shape}, ground truth shape: {gt['U_ground_truth'].shape}")

    print("\nExecuting reference solver ...")
    t0 = time.time()
    result, stdout, stderr = executor.run_solver(
        REFERENCE_SOLVER, gt["u0"], gt["v0"], gt["w0"],
        gt["t_coordinate"], tau_d, timeout=timeout,
    )
    exec_time = time.time() - t0

    if result is None:
        print(f"FAILED ({exec_time:.1f}s): {stderr[:500]}")
        return

    print(f"  Succeeded in {exec_time:.1f}s")
    print(f"  Output shapes: u={result['u'].shape}")

    metrics = evaluator.evaluate_fk(result, gt)
    print(f"\nMetrics:")
    for k, v in metrics.items():
        print(f"  {k}: {v:.6f}")

    with open(os.path.join(output_dir, "test_metrics.json"), "w") as f:
        json.dump({**metrics, "exec_time_s": exec_time, "mode": "test"}, f, indent=2)

    passed = metrics["nrmse_u_final"] < 0.1
    print(f"\nTest {'PASSED' if passed else 'FAILED'} (nRMSE_u_final = {metrics['nrmse_u_final']:.6f}, threshold = 0.1)")
    print(f"Results saved to {output_dir}")


def _save_metrics(output_dir: str, version_tag: str, metrics: dict):
    path = os.path.join(output_dir, f"metrics_{version_tag}.json")
    with open(path, "w") as f:
        json.dump(metrics, f, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="CodePDE Baseline: LLM-generated PDE solver with debug loop"
    )
    parser.add_argument(
        "--llm",
        default=None,
        help="LLM model name (e.g., gemini-2.5-flash, gpt-4o, claude-sonnet-4-6, qwen3:8b)",
    )
    parser.add_argument(
        "--data-dir",
        default=os.path.join(
            os.path.dirname(__file__), "..", "fk_data", "tau_d_0.5714"
        ),
        help="Path to FK ground truth data directory",
    )
    parser.add_argument(
        "--tau-d",
        type=float,
        default=0.5714,
        help="tau_d parameter for FK model (default: 0.5714)",
    )
    parser.add_argument(
        "--max-debug-rounds",
        type=int,
        default=3,
        help="Maximum LLM debug iterations (default: 3)",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output directory (default: results/<llm_name>)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Solver execution timeout in seconds (default: 300)",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run pipeline with a known-good reference solver (no LLM needed)",
    )
    args = parser.parse_args()

    if args.test:
        if args.output_dir is None:
            args.output_dir = os.path.join(os.path.dirname(__file__), "results", "test")
        run_test(
            data_dir=args.data_dir,
            tau_d=args.tau_d,
            output_dir=args.output_dir,
            timeout=args.timeout,
        )
    elif args.llm:
        if args.output_dir is None:
            safe_name = args.llm.replace("/", "_").replace(":", "_").replace(".", "_")
            args.output_dir = os.path.join(
                os.path.dirname(__file__), "results", safe_name
            )
        run_pipeline(
            llm_model=args.llm,
            data_dir=args.data_dir,
            tau_d=args.tau_d,
            max_debug_rounds=args.max_debug_rounds,
            output_dir=args.output_dir,
            timeout=args.timeout,
        )
    else:
        parser.error("Either --llm or --test is required")


if __name__ == "__main__":
    main()
