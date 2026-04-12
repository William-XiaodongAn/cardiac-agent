# Web-PDE-LLM: A Multi-Agent Framework for Real-Time Cardiac PDE Solving via LLM-Driven WebGL Computing

> **Paper abstract:** Solving PDEs for cardiac electrophysiology (e.g., the Fenton-Karma 3V model) in real time traditionally requires HPC clusters. We present **Web-PDE-LLM**, a multi-agent framework that bridges natural language intent and high-performance browser-based simulations by leveraging LLMs to automate WebGL code generation — achieving high numerical precision and real-time interactivity directly in the browser, without requiring specialized WebGL expertise.

---

## Overview

Web-PDE-LLM is a multi-agent AI framework that lets users describe cardiac electrophysiology simulations in plain language and automatically generates executable, GPU-accelerated WebGL simulations. The system orchestrates multiple LLM agents (Claude and Gemini) to handle parameter extraction, simulation code generation, tool integration, and automated testing.

**Key capabilities:**
- Natural language → real-time cardiac PDE simulation (no WebGL expertise required)
- GPU-accelerated Fenton-Karma 3V model running entirely in the browser via WebGL2
- Multi-agent pipeline with specialized roles: parameter extraction, code generation, and tool integration
- Automated simulation testing with Playwright-based visual validation
- Significantly reduced error rate compared to Python-based SOTA approaches (CodePDE, OpInf-LLM)

---

## Architecture

```
User (natural language)
        │
        ▼
┌───────────────────────────────────────┐
│         LangGraph Orchestrator         │
│  (langgraph_workflow_with_skills.ipynb)│
└───────────┬───────────────────────────┘
            │
    ┌───────┴────────┐
    │                │
    ▼                ▼
parameter_agent   model_agent ──────► tools_agent
(extracts 14      (generates           (integrates
 FK parameters)    WebGL HTML)          pacing, plot,
                                        voltage tools)
                       │
                       ▼
              Browser (WebGL2)
              Real-time simulation
                       │
                       ▼
              simulation-testing
              (Playwright validation)
```

The framework uses three specialized agents:

| Agent | Role |
|---|---|
| `parameter_agent` | Extracts 14 physiological parameters (τ values, voltage constants, membrane capacitance) from user input |
| `model_agent` | Generates the WebGL HTML simulation file using the Fenton-Karma 3V shader skeleton |
| `tools_agent` | Integrates interactive tools (S1-S2 pacing, voltage saving, spiral tip plotting) into the simulation |

---

## Fenton-Karma 3V Model

The cardiac electrophysiology model is implemented as a WebGL2 fragment shader. The simulation solves:

- **Three ionic currents:** fast inward (Ifi), slow outward (Iso), slow inward (Isi)
- **Laplacian diffusion** on a 512×512 grid
- **Rush-Larsen method** for gating variable integration
- **14 configurable parameters:** τ_d, τ_r, τ_si, τ_o, τ_a, τ_b, τ_v1⁻, τ_v2⁻, τ_v⁺, τ_w1⁻, τ_w2⁻, τ_w⁺, u_c, u_v, k, u_csi, C_m

The WebGL implementation runs in real time on consumer hardware, replacing the need for HPC clusters.

---

## Repository Structure

```
cardiac-agent/
├── langgraph_workflow_with_skills.ipynb   # Main multi-agent orchestration notebook
├── 3V MODEL skeleton.html                  # Reference WebGL Fenton-Karma simulation
├── gemini.config.json                      # Gemini model configuration
├── flowchart.png                           # System architecture diagram
│
├── .claude/                                # Claude Code agent configuration
│   └── skills/
│       ├── cardiac-model-generate/         # Skill: generate WebGL simulation HTML
│       │   ├── SKILL.md
│       │   └── reference/                  # Reference files (Abubu.js, model HTML, tools)
│       └── simulation-testing/             # Skill: automated simulation validation
│           ├── SKILL.md
│           └── scripts/
│               ├── simulation-testing.py   # Playwright 20s simulation runner
│               ├── capture_spiral.py       # Single spiral wave screenshot
│               └── capture_spiral_multiple.py  # Multi-timestep screenshot capture
│
├── .gemini/                                # Gemini CLI agent configuration
│   └── skills/
│       ├── cardiac-model-generate/         # Skill: generate simulation from scratch
│       ├── cardiac-model-tools/            # Skill: integrate interactive tools
│       └── simulation-testing/             # Skill: simulation validation
│
├── cardiac-PDE/
│   ├── v1/                                 # Multi-agent workflow notebooks and Python agents
│   └── tester/                             # HTML test harness and fragment shaders
│
├── baselines models/
│   ├── LLM/llm_code.ipynb                  # LLM baseline (FitzHugh-Nagumo solver)
│   ├── codePDE/                            # CodePDE baseline implementation
│   └── fk_data/                            # Ground-truth simulation data (CSV, NPZ)
│
└── papers/                                 # Reference papers on cardiac modeling and LLM agents
```

---

## Interactive Simulation Tools

Three JavaScript tools can be integrated into any generated simulation:

| Tool | File | Description |
|---|---|---|
| S1-S2 Pacing | `S1_S2_init.html` | Two-stage stimulus protocol using voltage-threshold state transitions |
| Pacing | `pacing.js` | Periodic stimulus at configurable intervals |
| Plot Spiral Tip | `plot_tip.js` | Toggle spiral wave tip visualization over a time window |
| Save Voltage | `save_voltage.js` | Export canvas as PNG at a specified simulation time |

---

## Getting Started

### Prerequisites

- A modern browser with WebGL2 support (Chrome, Firefox, Edge)
- Python 3.8+ with Jupyter
- [Claude Code CLI](https://claude.ai/claude-code) or [Gemini CLI](https://github.com/google-gemini/gemini-cli)
- Playwright (`pip install playwright && playwright install chromium`) for simulation testing

### Running the Multi-Agent Workflow

1. **Clone the repository:**
   ```bash
   git clone https://github.com/William-XiaodongAn/cardiac-agent.git
   cd cardiac-agent
   ```

2. **Open the main orchestration notebook:**
   ```bash
   jupyter notebook langgraph_workflow_with_skills.ipynb
   ```

3. **Set your API key** (Google Generative AI / Gemini):
   ```python
   import google.generativeai as genai
   genai.configure(api_key="YOUR_API_KEY")
   ```

4. **Run the workflow** — describe your simulation in natural language, e.g.:
   > *"Generate a 2D Fenton-Karma simulation with tau_d=0.25 showing spiral wave breakup, with S1-S2 pacing and voltage trace export at t=500ms."*

5. **Open the generated HTML file** in your browser to view the real-time simulation.

### Running Simulation Tests

```bash
cd .claude/skills/simulation-testing/scripts
# Run a 20-second simulation and capture output
python simulation-testing.py path/to/simulation.html

# Capture spiral wave at multiple timesteps
python capture_spiral_multiple.py path/to/simulation.html --times 100 200 500
```

---

## Baselines

We compare against two SOTA approaches:

| Method | Approach | Limitation |
|---|---|---|
| **CodePDE** | LLM-generated Python PDE solver | Slow execution, no real-time interactivity |
| **OpInf-LLM** | Operator inference with LLM | Python-based, limited browser integration |
| **Web-PDE-LLM (ours)** | LLM → WebGL, browser-native GPU | Real-time, interactive, no HPC required |

Ground-truth simulation data for comparison is in `baselines models/fk_data/`.

---

## Citation

If you use this work, please cite:

```bibtex
@article{an2025webpdellm,
  title={Web-PDE-LLM: A Multi-Agent Framework for Real-Time Cardiac PDEs Solving via LLM-Driven WebGL Computing},
  author={An, William Xiaodong and others},
  year={2025}
}
```

---

## License

The **Abubu.js** WebGL library (included in `reference/`) is licensed under the MIT License. See the license header in `Abubu.js` for details.
