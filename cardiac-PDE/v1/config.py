"""
Centralized configuration for the Web-PDE-LLM pipeline.
Modify this file to switch LLM backends, tune retry limits, or change output paths.
"""
from dataclasses import dataclass, field
from typing import List


@dataclass
class Config:
    # --- LLM model assignments (Ollama model names) ---
    clarifier_model: str = "qwen3:8b"
    parse_model: str = "qwen3:8b"
    code_model: str = "qwen3:8b"
    debug_model: str = "qwen2.5-coder:3b"
    validation_model: str = "qwen3:8b"

    # --- Pipeline behavior ---
    max_debug_attempts: int = 3       # max debug→validate retry loops
    parallel_models: bool = True      # run FK + AP pipelines in parallel threads

    # --- Output ---
    output_dir: str = "outputs"       # root for per-model subdirectories

    # --- Supported cardiac models ---
    available_models: List[str] = field(
        default_factory=lambda: ["fenton_karma", "aliev_panfilov"]
    )

    # --- Skeleton mapping (model_name → skeleton file) ---
    skeleton_map: dict = field(
        default_factory=lambda: {
            "fenton_karma": "coding_skeleton.frag",
            "aliev_panfilov": "ap_coding_skeleton.frag",
        }
    )
