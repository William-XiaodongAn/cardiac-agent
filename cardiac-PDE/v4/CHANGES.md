# v4 Evaluation Framework — Changes, Setup & Running Guide

This document covers:
1. What changed from the earlier `evaluation/` framework
2. Environment setup (Python, data, models)
3. How to run each experiment

---

## 1. What Changed

### 1.1 New baseline: OpInf-LLM

**File:** `baselines/opinf_llm.py`

Added the Operator Inference + LLM baseline following:

> *OpInf-LLM: Parametric PDE Solving with LLMs via Operator Inference*,
> arxiv.org/abs/2602.01493

The implementation has two phases:

**Offline (fit)**
1. Collect snapshot trajectories from the data source.
2. Compute a shared POD basis Φ per state variable via truncated SVD.
3. Project snapshots to the reduced space: r̂ = Φᵀu.
4. Estimate time derivatives via 2nd-order finite differences.
5. Learn operators A (linear), H (quadratic), c (constant bias) by solving
   the least-squares system: min ‖[r, r⊗r, 1] O − dr/dt‖² + λ‖O‖².
6. *(Optional)* Query an LLM to decide which terms to include.

**Online (predict)**
1. Project the initial condition: r₀ = Φᵀu₀.
2. Integrate dr/dt = Ar + H(r⊗r) + c with scipy RK45.
3. Reconstruct: u ≈ Φr, then clip to [0, 1].

**Parametric extension** (Exp C): when multiple parameter values are
available, operators at an unseen parameter are extrapolated via polynomial
regression over the training parameters.

**LLM involvement** (enabled with `--llm-terms`): the LLM is queried once
to decide whether to include the quadratic term. This is the online LLM step
from the paper; it costs one API call and avoids fitting unnecessary terms.

---

### 1.2 New data layer

**Files:** `data/base.py`, `data/pdebench_loader.py`, `data/fk_loader.py`, `data/custom_loader.py`

All data sources share a common `DataSource` interface with three methods:
- `get_metadata()` → `DatasetMetadata`
- `load_ic(sample_idx)` → `{var: array}`
- `load_snapshots(sample_idx, time_indices)` → `{t: {var: array}}`

Switch data sources with `--data <name>`:

| `--data` value       | Dataset                                      |
|----------------------|----------------------------------------------|
| `fk`                 | Fenton-Karma ground truth (existing CSV/NPZ) |
| `pdebench_2d_rd`     | PDEBench 2D Reaction-Diffusion (FitzHugh-Nagumo, 128×128 or 512×512) |
| `pdebench_1d_burgers`| PDEBench 1D Burgers                          |
| `custom`             | Your own data (extend `CustomLoader`)        |

To add a new data source: copy `data/custom_loader.py`, implement the three
methods, and register in `data/base.py::get_data_source()`.

---

### 1.3 Expanded metrics

**File:** `metrics/metrics.py`

Primary metrics (required for paper):

| Metric | Function | Definition |
|--------|----------|------------|
| **RMSE** | `rmse()` | √(mean((pred−gt)²)) per variable, averaged over snapshots |
| **Bug-free rate** | `bug_free_rate()` | Fraction of trials where code ran + output finite + values in [0,1] |
| **Running time** | `running_time_summary()` | Wall-clock mean ± std across trials (seconds) |

Additional metrics included:
- Relative L2 error, Max absolute error, SSIM
- Action potential duration (APD), Conduction velocity (CV)
- Spiral wave tip count (phase singularity detection)

---

### 1.4 Consolidated pipeline

**File:** `pipeline/eval_pipeline.py`

Three experiments, all runnable from one CLI:

| Experiment | Flag | What it measures |
|------------|------|-----------------|
| A — Accuracy | `--exp accuracy` | RMSE, L2, SSIM, running time for all methods |
| B — Robustness | `--exp robustness` | Bug-free rate over N trials; mean debug iterations |
| C — OpInf parametric | `--exp opinf_parametric` | Operator extrapolation to unseen parameters |

All methods are compared on the same initial condition and snapshot times.
Results written to `results/` as CSVs; LaTeX tables in `results/tables/`.

---

### 1.5 Carried over from `evaluation/`

- `webgl_capture.py` logic re-used via `_webgl_capture()` in `eval_pipeline.py`
- Visualisation and LaTeX table generation available in `evaluation/visualize.py`
  and `evaluation/generate_tables.py` (referenced, not duplicated)

---

## 2. Environment Setup

### 2.1 Python environment

```bash
cd v4/
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium      # only if using WebGL capture
```

### 2.2 LLM backend (Ollama)

```bash
# Install Ollama: https://ollama.com/download
ollama serve                     # start the daemon
ollama pull qwen3:8b             # code generation model
ollama pull qwen2.5-coder:3b     # debug model
```

### 2.3 FK ground truth data

The FK ground truth files must be present at:
```
../baselines models/fk_data/tau_d_0.5714/
    IC.csv
    UVW_array_data.npz
    sim_data_831.25.csv  ...  sim_data_931.25.csv
```

These are already in the repository. No download needed.

### 2.4 PDEBench data (optional)

PDEBench datasets are **not** included in the repo (files are 15–34 MB each).
Download the ones you need:

**Option A — direct wget:**

```bash
mkdir -p v4/data/raw/pdebench

# 2D Reaction-Diffusion (FitzHugh-Nagumo, 128×128, ~230 MB)
wget -O v4/data/raw/pdebench/2D_diff-react_NA_NA.h5 \
  "https://darus.uni-stuttgart.de/api/access/datafile/:persistentId/?persistentId=doi:10.18419/darus-2986/7"

# 1D Burgers, nu=0.01 (~40 MB)
mkdir -p v4/data/raw/pdebench/1D/Burgers/Train
wget -O v4/data/raw/pdebench/1D/Burgers/Train/1D_Burgers_Sols_Nu0.01.hdf5 \
  "https://darus.uni-stuttgart.de/api/access/datafile/:persistentId/?persistentId=doi:10.18419/darus-2986/1"
```

**Option B — HuggingFace (requires `pip install huggingface_hub`):**

```bash
huggingface-cli download pdebench/pdebench \
  "2D/diffusion-reaction/2D_diff-react_NA_NA.h5" \
  --local-dir v4/data/raw/pdebench/
```

**Option C — PDEBench pip package (small datasets only):**

```bash
pip install pdebench
python -c "from pdebench.data_download.download_direct import download_direct; download_direct()"
```

After download, set the data directory:
```bash
export PDEBENCH_DATA_DIR=/path/to/v4/data/raw/pdebench
# or pass --data-dir at runtime
```

---

## 3. Running the Pipeline

### 3.1 Quick-start (FK data, no WebGL)

```bash
cd v4/
python pipeline/eval_pipeline.py --all --no-webgl
```

Runs Experiments A and B on the existing FK ground truth.
Outputs written to `v4/results/`.

### 3.2 Experiment A — Accuracy

```bash
# FK data
python pipeline/eval_pipeline.py --exp accuracy

# PDEBench 2D reaction-diffusion
python pipeline/eval_pipeline.py --exp accuracy --data pdebench_2d_rd

# Include WebGL (requires the HTML file from cardiac-PDE/v1/outputs/)
python pipeline/eval_pipeline.py --exp accuracy \
  --webgl-html ../cardiac-PDE/v1/outputs/fenton_karma/march_shader.frag
```

Output: `results/exp_accuracy.csv`

Columns: `method, rmse_u, rmse_v, rmse_w, rmse_mean, l2_mean, ssim_u,
          bug_free, wall_time_s, peak_mem_mb, fps, uses_gpu`

### 3.3 Experiment B — Bug-free rate (robustness)

```bash
python pipeline/eval_pipeline.py --exp robustness --n-trials 10
```

For each of LLM-direct, CodePDE, and OpInf-LLM: generates N independent
solver runs and measures how many produce valid output.

Output: `results/exp_robustness.csv`

Columns: `method, bug_free_rate, mean_debug_iterations, time_mean_s, time_std_s`

### 3.4 Experiment C — OpInf parametric extrapolation

```bash
python pipeline/eval_pipeline.py --exp opinf_parametric
```

Trains OpInf-LLM at available tau_d values, extrapolates to a held-out
value, and reports RMSE against ground truth.

Output: `results/exp_opinf_parametric.csv`

### 3.5 Full run with all options

```bash
python pipeline/eval_pipeline.py \
  --all \
  --data pdebench_2d_rd \
  --data-dir ./data/raw/pdebench \
  --opinf-r 30 \
  --llm-terms \
  --n-trials 10 \
  --code-model qwen3:8b \
  --webgl-html ../cardiac-PDE/v1/outputs/fenton_karma/3V\ MODEL\ skeleton.html
```

### 3.6 Dry run (check imports)

```bash
python pipeline/eval_pipeline.py --dry-run
```

### 3.7 OpInf-LLM reduced dimension tuning

The reduced dimension `r` is the key hyperparameter for OpInf-LLM.
Typical values:

| Problem | Recommended r | Notes |
|---------|--------------|-------|
| FK 3V (512×512) | 15–30 | Higher r = better accuracy, slower fit |
| AP 2V (512×512) | 10–20 | Simpler dynamics, lower r sufficient |
| PDEBench 2D-RD (128×128) | 10–20 | Lower resolution, fewer modes needed |
| PDEBench 1D Burgers | 5–15 | 1D, well-conditioned |

```bash
python pipeline/eval_pipeline.py --exp accuracy --opinf-r 30
```

---

## 4. Output Files

```
v4/results/
├── hardware.json             # CPU/GPU/Python version log
├── exp_accuracy.csv          # Exp A: RMSE, L2, SSIM, time per method
├── exp_robustness.csv        # Exp B: bug-free rate, debug iterations
├── exp_opinf_parametric.csv  # Exp C: parametric extrapolation accuracy
├── figures/                  # (generate with evaluation/visualize.py)
└── tables/                   # (generate with evaluation/generate_tables.py)
```

To generate LaTeX tables from the CSVs:
```bash
cd evaluation/
python generate_tables.py --results-dir ../v4/results/
```

---

## 5. Adding a New Baseline

1. Create `v4/baselines/my_baseline.py` implementing a `run(ic, t_end, sample_times)` method that returns `(snapshots, perf_dict)`.
2. Import it in `v4/pipeline/eval_pipeline.py` and add a call block in `exp_accuracy()`.
3. The `perf_dict` must contain: `wall_time_s`, `bug_free`, `peak_mem_mb`.

## 6. Adding a New Data Source

1. Copy `v4/data/custom_loader.py` → `v4/data/my_loader.py`.
2. Implement `get_metadata()`, `load_ic()`, `load_snapshots()`.
3. Register in `v4/data/base.py::get_data_source()`.
4. Use with `--data my_source`.
