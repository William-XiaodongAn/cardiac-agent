system_prompt = '''
You are an intelligent AI researcher for coding, numerical algorithms, and scientific computing.
Your goal is to conduct cutting-edge research in the field of PDE solving by leveraging and creatively improving existing algorithms to maximize performances based on feedbacks.
Follow the user's requirements carefully and make sure you understand them.
Always document your code as comments to explain the reason behind them.
Always use Markdown cells to present your code.
'''

code_prompt = """
Given the {PDEs} and {coding_skeleton}, return the complete code implementation for the PDE solver in WebGL.
Output only the raw code. No talk, no markdown, just code.
"""

parse_prompt = """
You are given a clarified simulation specification intended for webGL.
Your task is to parse this paragraph into a structured JSON object that captures all key attributes needed for code generation.

### JSON Schema Requirements:
1. "PDEs": String. Full PDEs using LaTeX. IMPORTANT: Use double backslashes (e.g., \\nabla) for all LaTeX commands to ensure valid JSON escaping. When there is a new line, use \n.
2. "number_of_state_variables": Integer.
3. "texture_size": Integer (e.g., 512).
4. "spatial_step": Float (the value of dx).
5. "domain_size": Float (the size of the spatial domain, e.g., 20 for [-10,10]).
6. "temporal_step": Float (the value of dt).
7. "time_horizon": Float (the total simulation time, e.g., 100.0).
8. "boundary_conditions": String or Object describing the conditions.
9. "parameter_values": Object mapping each parameter to its initial value.
10. "notes": String (optional, use null if empty).

### Example Output Format:
{{
  "PDEs": "\\frac{{\\partial u}}{{\\partial t}} = D \\nabla^2 u \n",
  "number_of_state_variables": 3,
  "texture_size": 512,
  "spatial_step": 0.01,
  "domain_size": 20.0,
  "temporal_step": 0.001,
  "time_horizon": 100.0,
  "boundary_conditions": "Periodic",
  "parameter_values": {{"D": 0.001, "C_m": 1.0, "tau_pv": 7.99}},
}}

Input:
{user_input}

Output:
"""

refine_prompt = """
Given the nRMSE{nrmse} between the simulation results and the simulation codes {simulation_codes}, please refine the simulation to reduce the nRMSE.

Output only the raw code. No talk, no markdown, just code.
"""

debug_prompt = """
Now we have some bugs when using the codes {shader_codes} with the following logs {log_info}.

Output only the raw code. No talk, no markdown, just code.
"""