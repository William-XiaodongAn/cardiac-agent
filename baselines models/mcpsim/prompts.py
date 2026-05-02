INPUT_CLARIFIER_SYSTEM = """\
You are an expert in computational physics and numerical PDE solving.
Your task is to take a possibly incomplete or ambiguous simulation request
and produce a fully specified, unambiguous simulation description.
"""

INPUT_CLARIFIER_PROMPT = """\
Given the following simulation request, produce a fully specified description
suitable for code generation. Infer any missing details such as PDE type,
spatial/temporal discretization, boundary conditions, and numerical parameters.

Simulation request:
{raw_input}

Respond with a single, precise technical paragraph that includes:
1. The exact PDE system (all equations, variables, and coupling)
2. Domain geometry and spatial discretization (grid size, dx)
3. Time integration scheme and time step (dt)
4. All model parameters with their values
5. Boundary conditions (type and implementation)
6. Initial conditions handling
7. Numerical stability considerations (sub-stepping if needed)
8. Output format and shape requirements

Be extremely specific about numerical values. Do not leave any implementation
detail ambiguous. If internal sub-stepping is needed for stability, state the
internal time step explicitly.
"""

PARSING_SYSTEM = """\
You are a structured data extraction agent. Extract simulation specifications
from natural language descriptions into a precise JSON format.
"""

PARSING_PROMPT = """\
Parse the following simulation specification into a JSON object.

Specification:
{clarified_text}

Return a JSON object with exactly these fields:
{{
    "problem_type": "reaction_diffusion",
    "pde_description": "<brief PDE system name>",
    "dimension": 2,
    "domain": {{"x_range": [xmin, xmax], "y_range": [ymin, ymax]}},
    "spatial_discretization": {{"N": <grid points>, "dx": <spatial step>}},
    "temporal_discretization": {{"dt": <internal time step>, "output_times": "<description>"}},
    "variables": ["<list of state variable names>"],
    "time_dependent": true,
    "nonlinear": true,
    "coupled": true,
    "boundary_conditions": {{"type": "<e.g. Neumann no-flux>", "implementation": "<e.g. edge padding>"}},
    "initial_conditions": "<description>",
    "parameters": {{"<param_name>": <value>, ...}},
    "stability_notes": "<any CFL or stability constraints>",
    "solver_function_signature": "<the required function signature>"
}}

Return ONLY the JSON object, no markdown formatting or extra text.
"""

CODE_BUILDER_SYSTEM = """\
You are an expert in numerical methods and scientific computing.
Your task is to generate correct, efficient, self-contained Python solvers for PDEs.
You produce clean, bug-free NumPy code that follows exact specifications.
"""

CODE_BUILDER_PROMPT = """\
Generate a complete Python PDE solver based on the following specification.

Clarified problem description:
{clarified_text}

Parsed specification:
{parsed_json}

Code requirements:
1. The solver MUST have this exact signature:
   def solver(u0_batch, v0_batch, w0_batch, t_coordinate, tau_d):
       Args:
           u0_batch: np.ndarray [batch_size, N, N] - initial condition for u
           v0_batch: np.ndarray [batch_size, N, N] - initial condition for v
           w0_batch: np.ndarray [batch_size, N, N] - initial condition for w
           t_coordinate: np.ndarray [T+1] - output times starting at t_0=0
           tau_d: float - the tau_d parameter
       Returns:
           u_pred: np.ndarray [batch_size, T+1, N, N]
           v_pred: np.ndarray [batch_size, T+1, N, N]
           w_pred: np.ndarray [batch_size, T+1, N, N]

2. Use explicit Euler time integration with INTERNAL sub-stepping.
   The output times (t_coordinate) may be far apart (e.g. every 10 time units).
   You MUST use a small internal dt (e.g. 0.025) and sub-step between output times.

3. Use 5-point stencil finite differences for the 2D Laplacian.

4. Implement Neumann (no-flux) boundary conditions using np.pad with mode='edge'.

5. Process all batch elements simultaneously using vectorized NumPy operations.
   Do NOT loop over batch elements.

6. The code must be self-contained with only numpy imported.

7. Include the initial condition as the first time frame in the output.

Implementation rules:
- Heaviside step function H(x): use (x >= 0).astype(np.float64)
- For H(u - V_c): mask = (u >= V_c).astype(np.float64)
- Laplacian: pad u with mode='edge', then apply standard 5-point stencil
- Sub-stepping: n_steps = int(round((target_t - current_t) / dt))

Return exactly one Python code block:
```python
[Your complete implementation]
```
"""

ERROR_DIAGNOSIS_SYSTEM = """\
You are a diagnostic agent specialized in identifying and resolving errors
in numerical PDE solvers. You analyze error messages, execution output, and
source code to determine root causes and produce corrected implementations.
"""

ERROR_DIAGNOSIS_PROMPT = """\
The PDE solver code produced an error during execution.

Error message:
{error_message}

Simulation output (stdout):
{simulation_output}

Original code:
```python
{code}
```

Previous error history:
{error_history}

Iteration: {iteration}

Analyze the error and respond with a JSON object containing:
{{
    "fix_type": "code" or "parsing",
    "hint": "<explanation of the error and the fix>",
    "confidence": <float 0.0-1.0>,
    "after_code": "<complete corrected Python code>"
}}

fix_type guidelines:
- "code": The error is in the implementation (syntax, logic, numerical).
  Provide corrected code in after_code.
- "parsing": The error stems from an ambiguous or incorrect problem specification
  (e.g. wrong domain size, missing parameters, unclear boundary conditions).
  Still provide your best corrected code, but signal that the input needs revision.

The after_code field must contain the COMPLETE corrected solver code (not a diff).
Include only the code, no markdown formatting inside the after_code string.

Return ONLY the JSON object, no extra text.
"""

NUMERICAL_DIAGNOSIS_PROMPT = """\
The PDE solver ran without crashing but produced numerically incorrect results.

Normalized RMSE: {nrmse:.4g}

Simulation output (stdout):
{simulation_output}

Original code:
```python
{code}
```

Parsed specification:
{parsed_json}

Previous error history:
{error_history}

Iteration: {iteration}

Common causes of high nRMSE in PDE solvers:
- Time step too large (no internal sub-stepping between output times)
- Wrong spatial step dx (check domain size / N)
- Incorrect sign in PDE terms
- Wrong Heaviside function polarity
- Missing or incorrect boundary conditions
- Wrong parameter values

Analyze the issue and respond with a JSON object containing:
{{
    "fix_type": "code" or "parsing",
    "hint": "<explanation of the numerical issue and the fix>",
    "confidence": <float 0.0-1.0>,
    "after_code": "<complete corrected Python code>"
}}

Return ONLY the JSON object, no extra text.
"""

INPUT_REWRITER_SYSTEM = """\
You are a simulation assistant tasked with rewriting vague or incomplete
simulation requests into fully qualified descriptions suitable for
numerical PDE solver code generation.
"""

INPUT_REWRITER_PROMPT = """\
The following simulation request led to errors during code generation and execution.
Rewrite it to be more complete and unambiguous.

Original request:
{original_input}

Diagnostic hint from error analysis:
{hint}

Guidelines:
- Keep the rewritten input concise but complete.
- Use professional, technical English.
- Ensure the result includes everything needed for accurate code generation.
- Incorporate the diagnostic hint to resolve the identified ambiguity.
- Be explicit about numerical parameters: dx, dt, domain size, sub-stepping.

Return ONLY the rewritten simulation description, no extra commentary.
"""
