"""
Clarifier Agent — Step 0 of the Web-PDE-LLM pipeline.

Validates that a user's PDE description is complete before it reaches the
parse agent. Infers standard defaults where safe, and flags fields that are
genuinely missing so the pipeline can surface them to the user.
"""

clarifier_prompt = """
You are a simulation specification validator for cardiac electrophysiology WebGL simulations.

Review the user's PDE specification and determine whether it is complete enough
for a WebGL shader generator to produce a correct GLSL implementation.

A complete specification must include (or allow confident inference of):
1. Cardiac model type (Fenton-Karma 3V, Aliev-Panfilov 2V, or custom)
2. All governing PDEs with ionic current / reaction term definitions
3. Grid parameters: texture size N, spatial step dx, domain size
4. Time parameters: dt, total simulation time T
5. All named model parameters with numeric values
6. Boundary conditions (Neumann/Dirichlet/Periodic)

Rules for inference:
- If the model is clearly Fenton-Karma 3V and a parameter is not stated,
  fill in the canonical value: D=0.001, C_m=1.0, tau_pv=7.99, tau_v1=9.8,
  tau_v2=312.5, tau_pw=870.0, tau_mw=41.0, tau_0=12.5, tau_r=33.83,
  tau_si=29.0, k=10.0, V_csi=0.861, V_c=0.13, V_v=0.04.
- If the model is clearly Aliev-Panfilov 2V and a parameter is not stated,
  fill in: D=0.001, a=0.1, k=8.0, eps_0=0.01, mu1=0.07, mu2=0.3.
- If grid/time params are absent, infer: texture_size=512, dx=0.0390625,
  domain=20.0, dt=0.025, T=100.0, boundary=Neumann.
- Only flag a field as missing if it cannot be safely inferred.

User input:
{user_input}

Respond with ONLY this JSON (no markdown fences, no explanation):
{{
  "status": "complete" | "incomplete",
  "model_type": "<fenton_karma | aliev_panfilov | custom | null>",
  "clarified_spec": "<full specification text with inferred defaults filled in>",
  "missing": ["<field name if truly missing>"],
  "questions": ["<one question per missing field to ask the user>"]
}}
"""
