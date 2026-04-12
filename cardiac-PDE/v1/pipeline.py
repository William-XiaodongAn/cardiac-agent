"""
Web-PDE-LLM — Production Pipeline
===================================
End-to-end CLI for generating cardiac WebGL PDE simulations via a 5-agent
LLM workflow. Supports single-model and parallel multi-model runs.

Usage
-----
  # Run Fenton-Karma (default tau_d)
  python pipeline.py --model fenton_karma

  # Run Aliev-Panfilov
  python pipeline.py --model aliev_panfilov

  # Run BOTH models in parallel
  python pipeline.py --all

  # Custom tau_d for Fenton-Karma
  python pipeline.py --model fenton_karma --tau-d 0.45

  # Override the Ollama model used for code generation
  python pipeline.py --all --code-model qwen3:14b

  # Custom output directory
  python pipeline.py --all --output-dir results/run1

Agent pipeline (per model)
--------------------------
  Step 0  Clarifier   — validate / complete the user spec
  Step 1  Parse       — spec → structured JSON
  Step 2  Coding      — JSON + skeleton → GLSL shader
  Step 3  Debug       — fix compilation / obvious errors (up to N retries)
  Step 4  Validation  — static physical correctness check
            └─ if fail → back to Debug with validation report
"""

import argparse
import asyncio
import concurrent.futures
import json
import logging
import time
from pathlib import Path
from typing import Optional

from ollama import chat

import clarifier_agent
import coding_agent
import debug_agent
import parse_agent
import pde_descriptions
import validation_agent
from config import Config

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)-8s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("pipeline")


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def strip_code_fences(text: str, lang: str = "") -> str:
    """Remove markdown code fences that LLMs sometimes add to their output."""
    text = text.strip()
    for fence in (f"```{lang}", "```"):
        if text.startswith(fence):
            text = text[len(fence):]
            break
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


def llm_call(model: str, prompt: str, system: str = "") -> str:
    """Blocking LLM call via Ollama. Returns the assistant message text."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    response = chat(model=model, messages=messages)
    return response.message.content


def load_system_prompt() -> str:
    try:
        import system_prompt as sp
        return sp.system_prompt
    except ImportError:
        return ""


# ---------------------------------------------------------------------------
# Agent steps
# ---------------------------------------------------------------------------

def run_clarifier(user_input: str, cfg: Config) -> dict:
    """Step 0 — Validate and complete the user spec."""
    logger.info("  [0] Clarifier agent")
    prompt = clarifier_agent.clarifier_prompt.format(user_input=user_input)
    raw = llm_call(cfg.clarifier_model, prompt)
    raw = strip_code_fences(raw, "json")
    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("  [0] Clarifier returned non-JSON — treating spec as complete.")
        result = {"status": "complete", "clarified_spec": user_input, "missing": []}
    if result.get("missing"):
        logger.warning("  [0] Missing fields detected: %s", result["missing"])
    return result


def run_parser(clarified_input: str, cfg: Config, output_path: Path) -> dict:
    """Step 1 — Parse clarified spec into structured JSON."""
    logger.info("  [1] Parse agent")
    prompt = parse_agent.parse_prompt.format(user_input=clarified_input)
    raw = llm_call(cfg.parse_model, prompt)
    raw = strip_code_fences(raw, "json")
    parsed = json.loads(raw)
    output_path.write_text(json.dumps(parsed, indent=2), encoding="utf-8")
    logger.info("      Parsed spec → %s", output_path)
    return parsed


def run_coder(parsed_spec: dict, skeleton_path: Path, cfg: Config) -> str:
    """Step 2 — Generate GLSL shader from parsed spec + skeleton."""
    logger.info("  [2] Coding agent  (skeleton: %s)", skeleton_path.name)
    skeleton = skeleton_path.read_text(encoding="utf-8")
    prompt = coding_agent.coding_prompt.format(
        PDEs=parsed_spec["PDEs"],
        parameter_values=json.dumps(parsed_spec.get("parameter_values", {}), indent=2),
        coding_skeleton=skeleton,
    )
    raw = llm_call(cfg.code_model, prompt, system=load_system_prompt())
    return strip_code_fences(raw, "glsl")


def run_debugger(shader_code: str, log_content: str, cfg: Config) -> str:
    """Step 3 — Fix shader errors."""
    logger.info("  [3] Debug agent")
    prompt = debug_agent.debug_prompt.format(
        shader_codes=shader_code,
        log_info=log_content,
    )
    raw = llm_call(cfg.debug_model, prompt)
    return strip_code_fences(raw, "glsl")


def run_validator(shader_code: str, parsed_spec: dict, cfg: Config) -> dict:
    """Step 4 — Static physical correctness validation."""
    logger.info("  [4] Validation agent")
    prompt = validation_agent.validation_prompt.format(
        shader_code=shader_code,
        parameter_values=json.dumps(parsed_spec.get("parameter_values", {}), indent=2),
        num_state_vars=parsed_spec.get("number_of_state_variables", 3),
        model_notes=parsed_spec.get("notes") or "",
    )
    raw = llm_call(cfg.validation_model, prompt)
    raw = strip_code_fences(raw, "json")
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("  [4] Could not parse validation JSON.")
        return {"status": "warn", "checks": {}, "issues": ["Validator response was not valid JSON."]}


# ---------------------------------------------------------------------------
# Single-model pipeline
# ---------------------------------------------------------------------------

def run_single_model(model_name: str, user_input: str, cfg: Config) -> dict:
    """
    Full 5-step pipeline for one cardiac model.

    Returns a result dict with keys:
        model, shader_path, validation, elapsed_s, parsed_spec
    """
    t0 = time.time()
    output_dir = Path(cfg.output_dir) / model_name
    output_dir.mkdir(parents=True, exist_ok=True)

    skeleton_path = Path(cfg.skeleton_map.get(model_name, "coding_skeleton.frag"))
    logger.info("=== Pipeline: %s ===", model_name)

    # ── Step 0: Clarify ────────────────────────────────────────────────────
    clarified = run_clarifier(user_input, cfg)
    clarified_input = clarified.get("clarified_spec") or user_input

    # ── Step 1: Parse ─────────────────────────────────────────────────────
    parsed = run_parser(clarified_input, cfg, output_dir / "parsed_resp.json")

    # ── Step 2: Code ──────────────────────────────────────────────────────
    shader_code = run_coder(parsed, skeleton_path, cfg)

    # ── Step 3 + 4: Debug → Validate loop ────────────────────────────────
    validation: dict = {}
    for attempt in range(cfg.max_debug_attempts):

        # Quick static check for gross GLSL errors before calling the LLM validator
        lower = shader_code.lower()
        has_glsl_error = any(tok in lower for tok in ("error:", "syntax error", "undefined identifier"))
        if has_glsl_error:
            logger.warning("  Apparent GLSL error found — running debug (attempt %d)", attempt + 1)
            shader_code = run_debugger(shader_code, "Static scan: possible GLSL syntax error detected.", cfg)
            continue  # re-check before validation

        validation = run_validator(shader_code, parsed, cfg)
        status = validation.get("status", "warn")
        logger.info("      Validation: %s | checks: %s", status, validation.get("checks", {}))

        if status == "pass":
            break

        if attempt < cfg.max_debug_attempts - 1:
            issues = "\n".join(validation.get("issues", []))
            suggestion = validation.get("suggestion") or ""
            log_content = f"Physical validation {status}:\n{issues}\nSuggestion: {suggestion}"
            shader_code = run_debugger(shader_code, log_content, cfg)
        else:
            logger.warning("  Max debug attempts reached — saving best available shader.")

    # ── Write output ───────────────────────────────────────────────────────
    shader_path = output_dir / "march_shader.frag"
    shader_path.write_text(shader_code, encoding="utf-8")
    elapsed = round(time.time() - t0, 1)
    logger.info("=== Done: %s  |  %.1fs  |  %s ===", model_name, elapsed, shader_path)

    return {
        "model": model_name,
        "shader_path": str(shader_path),
        "validation": validation,
        "elapsed_s": elapsed,
        "parsed_spec": parsed,
    }


# ---------------------------------------------------------------------------
# Parallel multi-model runner
# ---------------------------------------------------------------------------

async def run_parallel(models: list[str], user_inputs: dict, cfg: Config) -> list[dict]:
    """
    Run multiple model pipelines concurrently in a thread pool.
    LLM calls are I/O-bound so thread-level parallelism is appropriate.
    """
    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(models)) as pool:
        futures = [
            loop.run_in_executor(
                pool,
                run_single_model,
                m,
                user_inputs.get(m, user_inputs["default"]),
                cfg,
            )
            for m in models
        ]
        results = await asyncio.gather(*futures, return_exceptions=True)

    out = []
    for m, r in zip(models, results):
        if isinstance(r, Exception):
            logger.error("Pipeline for %s failed: %s", m, r)
            out.append({"model": m, "error": str(r)})
        else:
            out.append(r)
    return out


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Web-PDE-LLM: natural language → WebGL cardiac PDE shader",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    group = p.add_mutually_exclusive_group()
    group.add_argument(
        "--model",
        choices=["fenton_karma", "aliev_panfilov"],
        help="Run a single cardiac model.",
    )
    group.add_argument(
        "--all",
        action="store_true",
        help="Run all supported models in parallel.",
    )
    p.add_argument("--input", type=str, default=None,
                   help="Custom PDE description (overrides built-in model descriptions).")
    p.add_argument("--tau-d", type=float, default=0.5714,
                   help="tau_d for Fenton-Karma model.")
    p.add_argument("--output-dir", type=str, default="outputs",
                   help="Root directory for output files.")
    p.add_argument("--code-model", type=str, default=None,
                   help="Override the Ollama model used for the coding agent.")
    p.add_argument("--max-retries", type=int, default=3,
                   help="Maximum debug→validate retry attempts.")
    return p


def main() -> None:
    args = build_parser().parse_args()

    cfg = Config(
        output_dir=args.output_dir,
        max_debug_attempts=args.max_retries,
    )
    if args.code_model:
        cfg.code_model = args.code_model

    # Build per-model user inputs
    fk_input = pde_descriptions.fk_description.format(tau_d=args.tau_d)
    ap_input = pde_descriptions.ap_description
    user_inputs: dict = {
        "fenton_karma": fk_input,
        "aliev_panfilov": ap_input,
        "default": args.input or fk_input,
    }
    if args.input:
        # Custom input overrides both models when --all is used
        user_inputs["fenton_karma"] = args.input
        user_inputs["aliev_panfilov"] = args.input

    # Dispatch
    if args.all:
        logger.info("Running all models in parallel: %s", cfg.available_models)
        results = asyncio.run(run_parallel(cfg.available_models, user_inputs, cfg))
    elif args.model:
        results = [run_single_model(args.model, user_inputs[args.model], cfg)]
    else:
        # Default: Fenton-Karma
        results = [run_single_model("fenton_karma", fk_input, cfg)]

    # Summary
    print("\n" + "=" * 60)
    print("  SUMMARY")
    print("=" * 60)
    for r in results:
        if "error" in r:
            print(f"  {r['model']:<20}  ERROR: {r['error']}")
        else:
            v_status = r.get("validation", {}).get("status", "—")
            print(
                f"  {r['model']:<20}  {v_status:<6}  "
                f"{r['elapsed_s']}s  →  {r['shader_path']}"
            )
    print("=" * 60)


if __name__ == "__main__":
    main()
