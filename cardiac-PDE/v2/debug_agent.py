"""
Debug Agent — Step 3 of the Web-PDE-LLM pipeline.

Receives a broken GLSL shader + an error log (WebGL compilation errors or
physical-validation failure notes) and returns a corrected shader.
"""

# Template variables: {shader_codes}, {log_info}
debug_prompt = """
You are a GLSL debugging expert. Fix the WebGL fragment shader below.

Error / validation report:
{log_info}

Shader code to fix:
{shader_codes}

Rules:
- Output ONLY the corrected raw GLSL code. No markdown, no explanation.
- Preserve ALL uniforms, defines, in/out declarations, and layout qualifiers.
- Address every issue described in the error / validation report.
- Do not introduce new features or change the numerical scheme beyond what is
  needed to fix the reported errors.
"""