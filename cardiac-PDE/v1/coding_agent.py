"""
Coding Agent — Step 2 of the Web-PDE-LLM pipeline.

Generates a complete GLSL fragment shader from the parsed PDE spec and the
model-specific coding skeleton.
"""

# Template variables: {PDEs}, {parameter_values}, {coding_skeleton}
coding_prompt = """
You are a GLSL shader expert implementing cardiac electrophysiology PDEs for WebGL2.

Given the PDE specification and the coding skeleton below, produce a complete,
compilable GLSL ES 3.00 fragment shader.

PDEs (LaTeX):
{PDEs}

Model parameters (use these exact values as GLSL constants):
{parameter_values}

Coding skeleton — fill in ONLY the sections marked "your codes here":
{coding_skeleton}

Rules:
- Output ONLY raw GLSL code. No markdown fences, no explanation, no comments
  outside the shader.
- Keep every existing uniform, define, layout qualifier, and main() signature.
- Fill in the "your codes here" stubs; do not delete or alter anything else.
- Use the parameter values above verbatim — do not invent or change them.
- Implement Neumann (no-flux) boundary conditions for edge pixels by clamping
  or mirroring neighbour texture coordinates.
- Apply explicit Euler time integration: new_x = old_x + dt * dxdt.
- Clamp all state variables to [0.0, 1.0] before writing to ocolor.
"""