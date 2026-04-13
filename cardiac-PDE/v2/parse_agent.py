"""
Parse Agent — Step 1 of the Web-PDE-LLM pipeline.

Converts a clarified natural-language / LaTeX PDE description into a
structured JSON specification used by the coding agent.
"""

# Template variable: {user_input}
parse_prompt = """
You are given a clarified simulation specification for a WebGL cardiac PDE solver.
Parse it into a structured JSON object capturing every attribute needed for
GLSL shader code generation.

JSON Schema:
1.  "PDEs"                       String. Full PDEs in LaTeX. Use double-backslashes
                                 for LaTeX commands (e.g., \\\\nabla). Newlines as \\n.
2.  "number_of_state_variables"  Integer.
3.  "texture_size"               Integer (e.g., 512).
4.  "spatial_step"               Float (dx value).
5.  "domain_size"                Float (total domain length, e.g., 20.0 for [-10,10]).
6.  "temporal_step"              Float (dt value).
7.  "time_horizon"               Float (total simulation time T).
8.  "boundary_conditions"        String ("Neumann", "Dirichlet", or "Periodic").
9.  "parameter_values"           Object mapping each named parameter to its numeric value.
10. "notes"                      String (implementation hints) or null.

Example output:
{{
  "PDEs": "\\\\frac{{\\\\partial u}}{{\\\\partial t}} = D \\\\nabla^2 u\\n",
  "number_of_state_variables": 3,
  "texture_size": 512,
  "spatial_step": 0.0390625,
  "domain_size": 20.0,
  "temporal_step": 0.025,
  "time_horizon": 100.0,
  "boundary_conditions": "Neumann",
  "parameter_values": {{"D": 0.001, "C_m": 1.0}},
  "notes": "Use 2nd-order central differences for the Laplacian."
}}

Input specification:
{user_input}

Output ONLY valid JSON, no markdown fences, no explanation:
"""