"""
Validation Agent — Step 4 of the Web-PDE-LLM pipeline.

Performs static analysis of the generated GLSL fragment shader to check for
physical and numerical correctness before the simulation is handed to the
browser. Issues found are fed back to the debug agent for auto-correction.
"""

validation_prompt = """
You are a numerical analysis expert specializing in cardiac electrophysiology
WebGL (GLSL) simulations.

Perform a static code review of the fragment shader below and validate that it
correctly implements the described cardiac PDE model.

Number of state variables: {num_state_vars}
Model parameters (reference): {parameter_values}
Implementation notes: {model_notes}

Shader code:
{shader_code}

Check each of the following (answer true/false and explain failures):

1. state_updates
   Are ALL {num_state_vars} state variable channels of ocolor updated with
   time-stepped values (e.g., ocolor.r = u + dudt*dt)?

2. laplacian
   Is the spatial Laplacian computed with a correct 4-point stencil and
   normalized by dx*dx (or dx²)?

3. boundary
   Are Neumann (no-flux) boundary conditions handled?
   Edge pixels should clamp or mirror their neighbor coordinates so the
   gradient at the boundary is zero.

4. parameters
   Do the constant values declared in the shader match the reference
   parameter_values above (within floating-point precision)?

5. stability
   Are there any obvious NaN / divide-by-zero risks (e.g., division by a
   parameter that could be 0, tanh overflow)?

6. time_integration
   Is explicit Euler integration applied correctly:
   new_x = old_x + dt * dxdt  for each state variable?

7. ionic_currents (for Fenton-Karma) or reaction_terms (for Aliev-Panfilov)
   Are all ionic current / reaction terms present and correctly signed?

Respond with ONLY this JSON (no markdown, no explanation):
{{
  "status": "pass" | "warn" | "fail",
  "checks": {{
    "state_updates": true | false,
    "laplacian": true | false,
    "boundary": true | false,
    "parameters": true | false,
    "stability": true | false,
    "time_integration": true | false,
    "ionic_currents": true | false
  }},
  "issues": ["<concise description of each failed check>"],
  "suggestion": "<targeted GLSL fix if status is fail, otherwise null>"
}}
"""
