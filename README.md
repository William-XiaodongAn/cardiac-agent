# Web-PDE-LLM: A Multi-Agent Framework for Real-Time Cardiac PDE Solving via LLM-Driven WebGL Computing

> Solving PDEs for cardiac electrophysiology (e.g., the Fenton-Karma 3V model) in real time traditionally requires HPC clusters. **Web-PDE-LLM** bridges natural language intent and high-performance browser-based simulations by leveraging LLMs to automate WebGL shader code generation — achieving real-time interactivity directly in the browser without requiring specialized WebGL expertise.

---

## Overview

Web-PDE-LLM is a multi-agent AI framework that takes a natural language or mathematical description of a cardiac PDE and automatically produces a GPU-accelerated WebGL fragment shader that runs in real time in the browser.

The core pipeline lives in [`cardiac-PDE/v1/`](./cardiac-PDE/v1/) and orchestrates three specialized LLM agents:

```
Natural Language / PDE Spec
          │
          ▼
   ┌─────────────┐
   │ Parse Agent │  → parsed_resp.json     (structured PDE spec)
   └──────┬──────┘
          │
          ▼
   ┌──────────────┐
   │ Coding Agent │  → march_shader.frag   (GLSL fragment shader)
   └──────┬───────┘
          │  (on compilation errors)
          ▼
   ┌─────────────┐
   │ Debug Agent │  → corrected march_shader.frag
   └─────────────┘
          │
          ▼
   Browser (WebGL2) — real-time cardiac simulation
```

---

## Agent Pipeline

### 0. Clarifier Agent (`clarifier_agent.py`) — NEW
Validates the user's input before parsing. Infers standard defaults (grid size, time step, canonical parameter values) for known cardiac models, and flags fields that are genuinely missing with concrete questions. Prevents downstream failures caused by underspecified prompts.

Output: `{"status": "complete"|"incomplete", "clarified_spec": "...", "missing": [...], "questions": [...]}`

### 1. Parse Agent (`parse_agent.py`)
Converts the clarified spec into a structured JSON specification. Extracts:
- Mathematical PDEs (LaTeX form)
- Grid and domain configuration (texture size, spatial/temporal resolution)
- Physical parameters (diffusion coefficient, τ constants, voltage thresholds)
- Boundary conditions

Output: `parsed_resp.json`

### 2. Coding Agent (`coding_agent.py`)
Takes the parsed JSON and a model-specific GLSL skeleton and generates a complete WebGL fragment shader. Fills in:
- Laplacian computation (4-point finite difference stencil, Neumann BCs)
- Ionic current / reaction term expressions
- Gating variable kinetics (piecewise thresholding)
- Explicit Euler time integration with clamping

Output: `march_shader.frag`

### 3. Debug Agent (`debug_agent.py`)
If the generated shader has compilation errors or fails validation, the debug agent receives the shader source and the error/validation report, then returns corrected code. Called up to `max_debug_attempts` times.

Output: corrected `march_shader.frag`

### 4. Validation Agent (`validation_agent.py`) — NEW
Performs static analysis of the generated shader before it reaches the browser. Checks:
- All state variable channels are updated (`ocolor.r/g/b`)
- Laplacian is normalized by dx²
- Neumann boundary conditions are enforced
- Parameter values match the spec
- No division-by-zero / NaN risks
- Correct explicit Euler integration
- All ionic currents / reaction terms are present

If validation fails, issues are fed back to the debug agent automatically.

Output: `{"status": "pass"|"warn"|"fail", "checks": {...}, "issues": [...], "suggestion": "..."}`

---

## Supported Cardiac Models

### Fenton-Karma 3V (default)

Three coupled PDEs on a 512×512 grid:

| Variable | Texture Channel | Meaning |
|---|---|---|
| `u` | R | Transmembrane voltage |
| `v` | G | Fast gating variable |
| `w` | B | Slow gating variable |

- `du/dt = D·∇²u − (I_fi + I_so + I_si) / C_m`
- `dv/dt`, `dw/dt` — piecewise gating kinetics (threshold V_c = 0.13)

### Aliev-Panfilov 2V — NEW

Simpler two-variable model, good for generalizability comparison:

| Variable | Texture Channel | Meaning |
|---|---|---|
| `u` | R | Transmembrane potential |
| `v` | G | Recovery variable |

- `du/dt = D·∇²u − k·u·(u−a)·(u−1) − u·v`
- `dv/dt = ε(u,v)·(−v − k·u·(u−a−1))`,  ε(u,v) = ε₀ + μ₁v/(μ₂+u)

**Common configuration (both models):**
- Domain: 20.0 units, 512×512 grid (Δx ≈ 0.039), dt = 0.025, D = 0.001
- Boundary: Neumann (no-flux)

---

## Repository Structure

```
cardiac-agent/
├── cardiac-PDE/v1/                              # Core framework (main)
│   ├── pipeline.py                              # Production CLI — single or parallel runs
│   ├── config.py                                # Centralized LLM + pipeline configuration
│   ├── multi_agent_workflow_small_model.ipynb   # Interactive 5-agent notebook (FK + AP)
│   │
│   ├── clarifier_agent.py                       # Agent 0: validate / complete user spec
│   ├── parse_agent.py                           # Agent 1: spec → structured JSON
│   ├── coding_agent.py                          # Agent 2: JSON + skeleton → GLSL shader
│   ├── debug_agent.py                           # Agent 3: error log → fixed shader
│   ├── validation_agent.py                      # Agent 4: static physical correctness check
│   ├── system_prompt.py                         # Shared LLM system prompt
│   │
│   ├── pde_descriptions.py                      # Model specs: Fenton-Karma + Aliev-Panfilov
│   ├── coding_skeleton.frag                     # GLSL skeleton — Fenton-Karma 3V
│   ├── ap_coding_skeleton.frag                  # GLSL skeleton — Aliev-Panfilov 2V
│   ├── march_shader.frag                        # Reference generated shader (FK)
│   ├── requirements.txt                         # Python dependencies
│   │
│   ├── outputs/
│   │   ├── fenton_karma/                        # FK pipeline outputs (JSON + .frag)
│   │   └── aliev_panfilov/                      # AP pipeline outputs (JSON + .frag)
│   └── 3V MODEL skeleton.html                   # Browser harness for running shaders
│
├── cardiac-PDE/tester/                          # Test harness (HTML + fragment shader)
├── baselines models/
│   ├── LLM/llm_code.ipynb                       # LLM baseline (Python PDE solver)
│   ├── codePDE/                                 # CodePDE baseline
│   └── fk_data/                                 # Ground-truth simulation data (CSV, NPZ)
├── 3V MODEL skeleton.html                       # Standalone WebGL simulation reference
├── flowchart.png                                # System architecture diagram
└── papers/                                      # Reference papers
```

---

## Getting Started

### Prerequisites
- Python 3.8+ with Jupyter
- Google Generative AI API key (Gemini)
- A modern browser with WebGL2 support (Chrome, Firefox, Edge)

### Run the Pipeline

1. **Clone the repository:**
   ```bash
   git clone https://github.com/William-XiaodongAn/cardiac-agent.git
   cd cardiac-agent/cardiac-PDE/v1
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run via CLI (recommended):**
   ```bash
   # Fenton-Karma only
   python pipeline.py --model fenton_karma

   # Aliev-Panfilov only
   python pipeline.py --model aliev_panfilov

   # Both models in parallel
   python pipeline.py --all

   # Custom tau_d for FK
   python pipeline.py --model fenton_karma --tau-d 0.45
   ```

4. **Or run interactively in the notebook:**
   ```bash
   jupyter notebook multi_agent_workflow_small_model.ipynb
   ```
   The notebook walks through all 5 agents step-by-step for both FK and AP models.

5. **Open `3V MODEL skeleton.html`** in your browser, point it at the generated `outputs/<model>/march_shader.frag`, and view the real-time simulation.

---

## Key Files

| File | Purpose |
|---|---|
| `pipeline.py` | Production CLI — single or parallel multi-model runs |
| `config.py` | LLM model assignments, retry limits, output paths |
| `multi_agent_workflow_small_model.ipynb` | Interactive 5-agent notebook (FK + AP) |
| `pde_descriptions.py` | Sample inputs: Fenton-Karma 3V + Aliev-Panfilov 2V specs |
| `system_prompt.py` | System prompt shared across all agents |
| `coding_skeleton.frag` | GLSL template for Fenton-Karma |
| `ap_coding_skeleton.frag` | GLSL template for Aliev-Panfilov |
| `clarifier_agent.py` | Agent 0: spec validation + default inference |
| `validation_agent.py` | Agent 4: static physical correctness checks |
| `outputs/*/march_shader.frag` | Generated WebGL fragment shaders |
| `outputs/*/parsed_resp.json` | Intermediate structured PDE specifications |

---

## Baselines

| Method | Approach | Limitation |
|---|---|---|
| **CodePDE** | LLM-generated Python solver | Slow, no browser interactivity |
| **OpInf-LLM** | Operator inference + LLM | Python-based, limited real-time use |
| **Web-PDE-LLM (ours)** | LLM → WebGL shader, GPU in browser | Real-time, interactive, no HPC required |

Ground-truth data for quantitative comparison is in `baselines models/fk_data/`.

---

## Citation

```bibtex
@article{an2025webpdellm,
  title={Web-PDE-LLM: A Multi-Agent Framework for Real-Time Cardiac PDEs Solving via LLM-Driven WebGL Computing},
  author={An, William Xiaodong and others},
  year={2025}
}
```
