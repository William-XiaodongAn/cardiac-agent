SYSTEM_PROMPT = """\
You are an expert in numerical methods, scientific computing, and PDE solving.
Your goal is to implement correct, efficient Python solvers for partial differential equations.
Always use clear, well-structured code. Use NumPy or PyTorch for computation.
"""

CODE_GENERATION_PROMPT = """\
Your task is to solve a partial differential equation (PDE) using Python in batch mode.

{pde_description}

You will be completing the following code skeleton:

```python
{solver_template}
```

Your tasks are:
1. Understand the PDE and the code skeleton.
2. Implement the `solver` function. You must not modify the function signature.

Requirements:
- The generated code must be self-contained, clearly structured, and bug-free.
- Implement auxiliary functions as needed to modularize the code.
- You may use PyTorch or NumPy. If using PyTorch, handle device placement (CPU/GPU).
- Use print statements sparingly to track progress (e.g., every 1000 steps).
- Use simple, robust algorithms (e.g., explicit Euler with finite differences).

Your output must contain exactly one Python code block:

```python
[Your complete implementation including imports and the solver function]
```
"""

DEBUG_EXECUTION_ERROR_PROMPT = """\
The solver code produced the following error when executed:

Code output:
{code_output}

Error message:
{error_message}

Original code:
```python
{code}
```

Think step-by-step to identify the root cause and provide a corrected implementation.
Return exactly one Python code block with the complete fixed solver:

```python
[Your bug-free implementation]
```
"""

DEBUG_NAN_INF_PROMPT = """\
The solver code ran without crashing, but the output contains NaN or Inf values, \
or the normalized RMSE is very high ({nrmse:.4g}).

Code output:
{code_output}

Original code:
```python
{code}
```

Common causes: numerical instability (time step too large), incorrect boundary conditions, \
wrong sign in equations, missing terms, or incorrect parameter values.

Think step-by-step to identify the root cause and provide a corrected implementation.
Return exactly one Python code block with the complete fixed solver:

```python
[Your bug-free implementation]
```
"""
