# variables: user_input

parse_prompt = """
You are given a clarified simulation specification intended for webGL.
Your task is to parse this paragraph into a structured JSON object that captures all key attributes needed for code generation.

### JSON Schema Requirements:
1. "pde_description": String. Full PDEs using LaTeX. IMPORTANT: Use double backslashes (e.g., \\\\nabla) for all LaTeX commands to ensure valid JSON escaping.
2. "number_of_state_variables": Integer.
3. "texture_size": Integer (e.g., 512).
4. "spatial_step": Float (the value of dx).
5. "domain_size": Float (the size of the spatial domain, e.g., 20 for [-10,10]).
6. "temporal_step": Float (the value of dt).
7. "time_horizon": Float (the total simulation time, e.g., 100.0).
8. "boundary_conditions": String or Object describing the conditions.
9. "initial_conditions": Object mapping each state variable to its initial value or function.
10. "parameters": Object mapping each model parameter (e.g., D, C_m, tau_pv) to its value.
11. "notes": String (optional, use null if empty).

### Example Output Format:
{{
  "pde_description": '''\\\\frac{{\\\\partial u}}{{\\\\partial t}} = D \\\\nabla^2 u''',
  "number_of_state_variables": 3,
  "texture_size": 512,
  "spatial_step": 0.01,
  "domain_size": 20.0,
  "temporal_step": 0.001,
  "time_horizon": 100.0,
  "boundary_conditions": "Periodic",
  "initial_conditions": {{"u": 0.2}},
    "parameters": {{"D": 0.001, "C_m": 1.0, "tau_pv": 7.99}},
  "notes": "Ensure high precision for Laplacian."
}}

### Constraint:
Output ONLY the raw JSON object. Do not include markdown code blocks (```json ... ```), preamble, or postscript.

Input:
{user_input}

Output:
"""