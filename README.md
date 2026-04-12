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

### 1. Parse Agent (`parse_agent.py`)
Converts a natural language or LaTeX PDE description into a structured JSON specification. Extracts:
- Mathematical PDEs (LaTeX form)
- Grid and domain configuration (texture size, spatial/temporal resolution)
- Physical parameters (diffusion coefficient, τ constants, voltage thresholds)
- Boundary conditions

Output: `parsed_resp.json`

### 2. Coding Agent (`coding_agent.py`)
Takes the parsed JSON and a GLSL skeleton (`coding_skeleton.frag`) and generates a complete WebGL fragment shader. Fills in:
- Laplacian computation (4-point finite difference stencil)
- Ionic current expressions (Ifi, Iso, Isi)
- Gating variable kinetics (Rush-Larsen, piecewise thresholding)
- Explicit Euler time integration

Output: `march_shader.frag`

### 3. Debug Agent (`debug_agent.py`)
If the generated shader fails to compile, the debug agent receives the shader source and the WebGL error log, then returns corrected code.

Output: corrected `march_shader.frag`

---

## Cardiac Model: Fenton-Karma 3V

The target model solves three coupled PDEs on a 512×512 grid:

| Variable | Texture Channel | Meaning |
|---|---|---|
| `u` | R | Transmembrane voltage |
| `v` | G | Fast gating variable |
| `w` | B | Slow gating variable |

**Governing equations:**
- `du/dt = D·∇²u + I_fi(u,v) + I_so(u) + I_si(u,w)`
- `dv/dt`, `dw/dt` — piecewise gating kinetics with threshold V_c = 0.13

**Default configuration:**
- Domain: 20.0 units, 512×512 grid (Δx ≈ 0.039)
- Time step: dt = 0.025, diffusion D = 0.001
- Boundary: Neumann (no-flux)

---

## Repository Structure

```
cardiac-agent/
├── cardiac-PDE/v1/                              # Core framework (main)
│   ├── multi_agent_workflow_small_model.ipynb   # Main workflow notebook
│   ├── multi_agent_workflow.ipynb               # Extended workflow notebook
│   ├── parse_agent.py                           # Agent 1: PDE spec → JSON
│   ├── coding_agent.py                          # Agent 2: JSON → GLSL shader
│   ├── debug_agent.py                           # Agent 3: error log → fixed shader
│   ├── system_prompt.py                         # Shared LLM system prompt
│   ├── pde_descriptions.py                      # Sample input: Fenton-Karma 3V spec
│   ├── coding_skeleton.frag                     # GLSL template given to coding agent
│   ├── march_shader.frag                        # Generated output shader
│   ├── parsed_resp.json                         # Example parse agent output
│   ├── parsed_resp_gemini.json                  # Gemini parse agent output
│   ├── coding_skeleton_prepare.ipynb            # Skeleton preparation notebook
│   └── 3V MODEL skeleton.html                   # Browser harness for running the shader
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
   pip install google-generativeai jupyter
   ```

3. **Open the main notebook:**
   ```bash
   jupyter notebook multi_agent_workflow_small_model.ipynb
   ```

4. **Set your API key and run all cells.** The notebook will:
   - Feed the cardiac PDE description (`pde_descriptions.py`) to the parse agent
   - Pass the parsed JSON to the coding agent to generate `march_shader.frag`
   - Invoke the debug agent automatically if compilation errors are detected

5. **Open `3V MODEL skeleton.html`** in your browser to load the generated shader and view the real-time simulation.

---

## Key Files

| File | Purpose |
|---|---|
| `multi_agent_workflow_small_model.ipynb` | End-to-end pipeline notebook |
| `pde_descriptions.py` | Sample input: Fenton-Karma 3V PDE spec |
| `system_prompt.py` | System prompt shared across all agents |
| `coding_skeleton.frag` | GLSL template provided to the coding agent |
| `march_shader.frag` | Final output: generated WebGL fragment shader |
| `parsed_resp.json` | Intermediate output: structured PDE specification |

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
