#!/usr/bin/env python3
"""
MCP-SIM Baseline: Multi-agent LLM framework for PDE simulation.

Reproduces the MCP-SIM architecture (Park et al., npj AI 2026):
  1. Input Clarifier: clarifies vague PDE description into precise spec
  2. Parsing Agent: extracts structured JSON from clarified text
  3. Code Builder: generates solver code from parsed spec
  4. Simulation Executor: runs code in sandbox
  5. Error Diagnosis: classifies errors as code-level or spec-level
  6. Input Rewriter: rewrites spec when diagnosis says "parsing" error
  7. Repeat Plan-Act-Reflect-Revise loop until success or max iterations
"""
import argparse
import json
import os
import sys
import time

import numpy as np

import agents
import executor
import evaluator


FK_RAW_INPUT = """\
Simulate the 2D Fenton-Karma three-variable (3V) cardiac electrophysiology model.
The system describes the evolution of normalized transmembrane potential u(t,x)
and two gating variables v(t,x) and w(t,x) on a 2D spatial domain.

The PDE system is:
  du/dt = D * laplacian(u) - (I_fi + I_so + I_si) / C_m
  dv/dt = (1-v)/tau_mv  if u < V_c,  else  -v/tau_pv
  dw/dt = (1-w)/tau_mw  if u < V_c,  else  -w/tau_pw

Ionic currents:
  I_fi = -v * H(u - V_c) * (u - V_c) * (1 - u) / tau_d
  I_so = u * (1 - H(u - V_c)) / tau_0 + H(u - V_c) / tau_r
  I_si = -w * (1 + tanh(k * (u - V_csi))) / (2 * tau_si)

where H is the Heaviside step function and
  tau_mv(u) = (1 - H(u - V_v)) * tau_v1 + H(u - V_v) * tau_v2

Parameters: D=0.001, C_m=1.0, tau_pv=7.99, tau_v1=9.8, tau_v2=312.5,
tau_pw=870.0, tau_mw=41.0, tau_0=12.5, tau_r=33.83, tau_si=29.0,
k=10.0, V_csi=0.861, V_c=0.13, V_v=0.04, tau_d={tau_d}

Spatial domain: 512x512 grid. The ground truth uses dx = 10/N.
Time horizon: T=100 with outputs every 10 time units.
Internal time step: dt=0.025 for numerical stability.
Boundary conditions: Neumann (no-flux).
"""


def run_pipeline(
    llm_model: str,
    data_dir: str,
    tau_d: float,
    max_iterations: int,
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

    clarifier = agents.InputClarifierAgent(llm_model)
    parser = agents.ParsingAgent(llm_model)
    builder = agents.CodeBuilderAgent(llm_model)
    diagnoser = agents.ErrorDiagnosisAgent(llm_model)
    rewriter = agents.InputRewriterAgent(llm_model)

    raw_input = FK_RAW_INPUT.format(tau_d=tau_d)

    memory = {
        "raw_input": raw_input,
        "iterations": [],
        "error_history": [],
    }

    best_nrmse = 1e10
    best_code = ""
    best_version = 0
    code = None
    clarified_text = None
    parsed_json = None

    for iteration in range(max_iterations):
        print(f"\n{'='*60}")
        print(f"ITERATION {iteration}")
        print(f"{'='*60}")

        needs_clarify = (
            clarified_text is None
            or (memory["iterations"] and memory["iterations"][-1].get("fix_type") == "parsing")
        )

        if needs_clarify:
            print(f"\n[Agent 1: Input Clarifier] Clarifying input ...")
            t0 = time.time()
            clarified_text = clarifier.clarify(raw_input)
            dt_clarify = time.time() - t0
            print(f"  Done ({dt_clarify:.1f}s, {len(clarified_text)} chars)")
            _save_artifact(output_dir, f"clarified_v{iteration}.txt", clarified_text)

            print(f"\n[Agent 2: Parsing Agent] Extracting structured spec ...")
            t0 = time.time()
            parsed_json = parser.parse(clarified_text)
            dt_parse = time.time() - t0
            print(f"  Done ({dt_parse:.1f}s)")
            _save_artifact(
                output_dir,
                f"parsed_v{iteration}.json",
                json.dumps(parsed_json, indent=2),
            )

            if parsed_json.get("parse_error"):
                print(f"  WARNING: JSON parsing failed, using raw response")

            print(f"\n[Agent 3: Code Builder] Generating solver ...")
            t0 = time.time()
            code = builder.build_code(clarified_text, parsed_json)
            dt_build = time.time() - t0
            print(f"  Done ({dt_build:.1f}s, {len(code)} chars)")
            _save_artifact(output_dir, f"generated_code_v{iteration}.py", code)

        elif code is None:
            print(f"\n[Agent 3: Code Builder] Generating solver ...")
            t0 = time.time()
            code = builder.build_code(clarified_text, parsed_json)
            dt_build = time.time() - t0
            print(f"  Done ({dt_build:.1f}s, {len(code)} chars)")
            _save_artifact(output_dir, f"generated_code_v{iteration}.py", code)

        print(f"\n[Agent 4: Simulation Executor] Running solver ...")
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
            print(f"  stdout: {stdout[:500]}{'...' if len(stdout) > 500 else ''}")

        iteration_record = {"iteration": iteration, "exec_time_s": exec_time}

        if result is None:
            print(f"  EXECUTION FAILED ({exec_time:.1f}s)")
            error_preview = stderr[:1000] if stderr else "unknown error"
            print(f"  error: {error_preview}")

            iteration_record.update({
                "status": "execution_error",
                "error": stderr[:2000],
            })
            memory["iterations"].append(iteration_record)
            memory["error_history"].append(
                f"Iter {iteration}: execution error: {stderr[:500]}"
            )
            _save_metrics(output_dir, f"v{iteration}", iteration_record)

            if iteration < max_iterations - 1:
                print(f"\n[Agent 5: Error Diagnosis] Analyzing error ...")
                t0 = time.time()
                diagnosis = diagnoser.diagnose_execution_error(
                    error_message=stderr,
                    simulation_output=stdout,
                    code=code,
                    error_history="\n".join(memory["error_history"]),
                    iteration=iteration,
                )
                dt_diag = time.time() - t0
                print(f"  Done ({dt_diag:.1f}s)")
                print(f"  fix_type: {diagnosis.get('fix_type', 'unknown')}")
                print(f"  hint: {diagnosis.get('hint', 'none')[:200]}")
                print(f"  confidence: {diagnosis.get('confidence', 0)}")

                _save_artifact(
                    output_dir,
                    f"diagnosis_v{iteration}.json",
                    json.dumps(diagnosis, indent=2, default=str),
                )

                iteration_record["fix_type"] = diagnosis.get("fix_type", "code")
                iteration_record["hint"] = diagnosis.get("hint", "")

                if diagnosis.get("fix_type") == "parsing":
                    print(f"\n[Agent 6: Input Rewriter] Rewriting input ...")
                    t0 = time.time()
                    raw_input = rewriter.rewrite(
                        raw_input, diagnosis.get("hint", "")
                    )
                    dt_rewrite = time.time() - t0
                    print(f"  Done ({dt_rewrite:.1f}s)")
                    _save_artifact(
                        output_dir, f"rewritten_input_v{iteration}.txt", raw_input
                    )
                    memory["raw_input"] = raw_input
                    clarified_text = None
                elif diagnosis.get("after_code"):
                    code = diagnosis["after_code"]
                    _save_artifact(
                        output_dir, f"generated_code_v{iteration}_fix.py", code
                    )

            continue

        print(f"  Execution succeeded ({exec_time:.1f}s)")
        print(
            f"  Output shapes: u={result['u'].shape}, "
            f"v={result['v'].shape}, w={result['w'].shape}"
        )

        metrics_dict = evaluator.evaluate_fk(result, gt)
        iteration_record.update({
            "status": "success",
            **metrics_dict,
        })
        memory["iterations"].append(iteration_record)
        _save_metrics(output_dir, f"v{iteration}", iteration_record)

        nrmse = metrics_dict["nrmse_u_final"]
        fmt = lambda x: f"{x:.6f}" if abs(x) < 1e6 else f"{x:.4g}"
        print(f"  nRMSE(u, final): {fmt(nrmse)}")
        print(f"  nRMSE(u, all):   {fmt(metrics_dict['nrmse_u'])}")
        print(f"  nRMSE(v, all):   {fmt(metrics_dict['nrmse_v'])}")
        print(f"  nRMSE(w, all):   {fmt(metrics_dict['nrmse_w'])}")

        if nrmse < best_nrmse:
            best_nrmse = nrmse
            best_code = code
            best_version = iteration

        if nrmse < 0.1:
            print(f"\n  nRMSE < 0.1 — solver is accurate enough. Stopping.")
            break

        if iteration < max_iterations - 1:
            print(
                f"\n[Agent 5: Error Diagnosis] nRMSE too high, analyzing ..."
            )
            t0 = time.time()
            diagnosis = diagnoser.diagnose_numerical_error(
                nrmse=nrmse,
                simulation_output=stdout,
                code=code,
                parsed_json=parsed_json or {},
                error_history="\n".join(memory["error_history"]),
                iteration=iteration,
            )
            dt_diag = time.time() - t0
            print(f"  Done ({dt_diag:.1f}s)")
            print(f"  fix_type: {diagnosis.get('fix_type', 'unknown')}")
            print(f"  hint: {diagnosis.get('hint', 'none')[:200]}")
            print(f"  confidence: {diagnosis.get('confidence', 0)}")

            _save_artifact(
                output_dir,
                f"diagnosis_v{iteration}.json",
                json.dumps(diagnosis, indent=2, default=str),
            )

            memory["error_history"].append(
                f"Iter {iteration}: nRMSE={nrmse:.4g}, hint={diagnosis.get('hint', '')[:200]}"
            )
            iteration_record["fix_type"] = diagnosis.get("fix_type", "code")
            iteration_record["hint"] = diagnosis.get("hint", "")

            if diagnosis.get("fix_type") == "parsing":
                print(f"\n[Agent 6: Input Rewriter] Rewriting input ...")
                t0 = time.time()
                raw_input = rewriter.rewrite(
                    raw_input, diagnosis.get("hint", "")
                )
                dt_rewrite = time.time() - t0
                print(f"  Done ({dt_rewrite:.1f}s)")
                _save_artifact(
                    output_dir, f"rewritten_input_v{iteration}.txt", raw_input
                )
                memory["raw_input"] = raw_input
                clarified_text = None
            elif diagnosis.get("after_code"):
                code = diagnosis["after_code"]
                _save_artifact(
                    output_dir, f"generated_code_v{iteration}_fix.py", code
                )

    if best_code:
        _save_artifact(output_dir, "best_solver.py", best_code)

    summary = {
        "llm_model": llm_model,
        "tau_d": tau_d,
        "best_version": f"v{best_version}",
        "best_nrmse_u_final": best_nrmse,
        "total_iterations": min(iteration + 1, max_iterations),
        "bug_free": best_nrmse < 1e10,
        "method": "mcpsim",
    }
    _save_artifact(output_dir, "summary.json", json.dumps(summary, indent=2))
    _save_artifact(output_dir, "memory.json", json.dumps(memory, indent=2, default=str))

    print(f"\n{'='*60}")
    print(f"SUMMARY (MCP-SIM)")
    print(f"  Model:           {llm_model}")
    print(f"  Best version:    v{best_version}")
    print(f"  Best nRMSE:      {best_nrmse:.6f}")
    print(f"  Bug-free:        {best_nrmse < 1e10}")
    print(f"  Total iterations:{summary['total_iterations']}")
    print(f"  Results in:      {output_dir}")
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
    print("TEST MODE: Running MCP-SIM pipeline with reference solver (no LLM)")
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


def _save_artifact(output_dir: str, filename: str, content: str):
    path = os.path.join(output_dir, filename)
    with open(path, "w") as f:
        f.write(content)


def _save_metrics(output_dir: str, version_tag: str, metrics: dict):
    path = os.path.join(output_dir, f"metrics_{version_tag}.json")
    with open(path, "w") as f:
        json.dump(metrics, f, indent=2, default=str)


def main():
    parser = argparse.ArgumentParser(
        description="MCP-SIM Baseline: Multi-agent PDE solver with Plan-Act-Reflect-Revise loop"
    )
    parser.add_argument(
        "--llm",
        default=None,
        help="LLM model name (e.g., gemini-2.5-flash, gpt-4o, claude-sonnet-4-6, qwen3:32b)",
    )
    parser.add_argument(
        "--data-dir",
        default=os.path.join(
            os.path.dirname(__file__), "..", "fk_data", "tau_d_0.5714"
        ),
    )
    parser.add_argument("--tau-d", type=float, default=0.5714)
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=5,
        help="Maximum Plan-Act-Reflect-Revise iterations (default: 5)",
    )
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run with reference solver (no LLM needed)",
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
            max_iterations=args.max_iterations,
            output_dir=args.output_dir,
            timeout=args.timeout,
        )
    else:
        parser.error("Either --llm or --test is required")


if __name__ == "__main__":
    main()
