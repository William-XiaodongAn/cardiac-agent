advection_description = '''
The PDE is the 1D advection equation, given by

\\[
\\begin{{cases}}
\\partial_t u(t, x) + \\beta \\partial_x u(t, x) = 0, & x \\in (0,1), \; t \\in (0,2] \\
u(0, x) = u_0(x), & x \\in (0,1)
\\end{{cases}}
\\]

where $\\beta$ is a constant representing the advection speed. In our task, we assume the periodic boundary condition.

Given the discretization of $u_0(x)$ of shape [batch_size, N], where $N$ is the number of spatial points, you need to implement a solver to predict $u(t, \\cdot)$ for the specified subsequent time steps ($t = t_1, \\ldots, t_T$). The solution is of shape [batch_size, T+1, N] (with the initial time frame and the subsequent steps). Note that although the required time steps are specified, you should consider using smaller time steps internally to obtain more stable simulation.

In particular, your code should be tailored to the case where $\\beta = {advection_beta}$, i.e., optimizing it particularly for this use case.
'''


burgers_description = '''
The PDE is the burgers equation, given by

\\[
\\begin{{cases}}
\\partial_t u(x, t) + \\partial_x \left( \\frac{{u^2(x, t)}}{{2}} \\right) = \\nu \\partial_{{xx}} u(x, t), & x \\in (0,1), \; t \\in (0,1] \\\\
u(x, 0) = u_0(x), & x \\in (0,1)
\\end{{cases}}
\\]

wheer $\\nu$ is a constant representing the viscosity. In our task, we assume the periodic boundary condition.

Given the discretization of $u_0(x)$ of shape [batch_size, N] where $N$ is the number of spatial points, you need to implement a solver to predict u(\cdot, t) for the specified subseqent time steps ($t=t_1, ..., t_T$). The solution is of shape [batch_size, T+1, N] (with the initial time frame and the subsequent steps). Note that although the required time steps are specified, you should consider using smaller time steps internally to obtain more stable simulation.

In particular, your code should be tailored to the case where $\\nu={burgers_nu}$, i.e., optimizing it particularly for this use case.
'''

reacdiff_1d_description = '''
The PDE is a diffusion-reaction equation, given by

\\[
\\begin{{cases}}
\\partial_t u(t, x) - \\nu \\partial_{{xx}} u(t, x) - \\rho u(1 - u) = 0, & x \\in (0,1), \; t \in (0,T] \\\\
u(0, x) = u_0(x), & x \in (0,1)
\end{{cases}}
\\]

where $\\nu$ and $\\rho$ are coefficients representing diffusion and reaction terms, respectively. In our task, we assume the periodic boundary condition.

Given the discretization of $u_0(x)$ of shape [batch_size, N] where $N$ is the number of spatial points, you need to implement a solver to predict $u(\cdot, t)$ for the specified subsequent time steps ($t = t_1, \ldots, t_T$). The solution is of shape [batch_size, T+1, N] (with the initial time frame and the subsequent steps). Note that although the required time steps are specified, you should consider using smaller time steps internally to obtain more stable simulation.

In particular, your code should be tailored to the case where $\\nu={reacdiff1d_nu}, \\rho={reacdiff1d_rho}$, i.e., optimizing it particularly for this use case.
Think carefully about the structure of the reaction and diffusion terms in the PDE and how you can exploit this structure to derive accurate result.
'''


cns1d_description = '''
The PDE is the 1D compressible Navier-Stokes equations, given by

\\[
\\begin{{cases}}
\\partial_t \\rho + \\partial_x (\\rho v) = 0 \\\\
\\rho(\\partial_t v + v\\partial_x v) = -\\partial_x p + \\eta\\partial_{{xx}} v + (\\zeta + \\eta/3)\\partial_x(\\partial_x v) \\\\
\\partial_t \\left[\\epsilon + \\frac{{\\rho v^2}}{{2}}\\right] + \\partial_x\\left[\\left(\\epsilon + p + \\frac{{\\rho v^2}}{{2}}\\right)v - v\\sigma'\\right] = 0
\\end{{cases}}
\\]
where $\\rho$ is the mass density, $v$ is the velocity, $p$ is the gas pressure, $\\epsilon = p/(\\Gamma - 1)$ is the internal energy with $\\Gamma = 5/3$, $\\sigma'=(\\zeta+\\frac{{4}}{{3}}\\eta) \\partial_x v$ is the viscous stress tensor, and $\\eta, \\zeta$ are the shear and bulk viscosity coefficients, respectively. In our task, we assume periodic boundary conditions. The spatial domain is $\\Omega = [-1,1]$.

Given the discretization of the initial velocity, density, pressure, each of shape [batch_size, N] where $N$ is the number of spatial points, you need to implement a solver to predict the state variables for the specified subsequent time steps ($t = t_1, \\ldots, t_T$). The solver outputs velocity, density, pressure, each of shape [batch_size, T+1, N] (with the initial time frame and the subsequent steps). Note that although the required time steps are specified, you should consider using smaller time steps internally to obtain more stable simulation.

In particular, your code should be tailored to the case where $\\eta = \\zeta = {cns1d_eta}$, i.e., optimizing it particularly for this use case.
'''


darcy_description = '''The PDE is the 2D Darcy flow equation, given by:

\\[-\\nabla \\cdot (a(x) \\nabla u(x)) = 1, \\quad x \\in (0,1)^2\\]

with the boundary condition:

\\[ u(x) = 0, \\quad x \\in \\partial (0,1)^2 \\]

where $u(x)$ is the solution function, and $a(x)$ is a batch of coefficient function. 

Given the discretization of the coefficient function $a(x)$ of shape [batch_size, N, N], where $N$ is the number of spatial grid points in each direction, you need to implement a solver to predict $u(x)$ for the specified subsequent time steps. The solution should be of shape [batch_size, N, N].'''


fk_description = '''
The PDE system is a 2D reaction-diffusion model (specifically the Bueno-Orovio-Cherry-Fenton model), describing the evolution of the normalized transmembrane potential $u(t, x)$ and two gating variables $v(t, x)$ and $w(t, x)$:

\\[
\\begin{cases} 
\\partial_t u(t, x) = \\diffCoef \\nabla^2 u(t, x) - \\frac{I_{fi}(u, v) + I_{so}(u) + I_{si}(u, w)}{C_m} \\\\
\\partial_t v(t, x) = \\begin{cases} \\frac{1-v(t, x)}{\\tau_{mv}(u)} & u(t, x) < V_c \\\\ \\frac{-v(t, x)}{\\tau_{pv}} & u(t, x) \\ge V_c \\end{cases} \\\\
\\partial_t w(t, x) = \\begin{cases} \\frac{1-w(t, x)}{\\tau_{mw}} & u(t, x) < V_c \\\\ \\frac{-w(t, x)}{\\tau_{pw}} & u(t, x) \\ge V_c \\end{cases}
\\end{cases}
\\]

where $x \in (0,1)^2$ and $t \in (0,T]$. The ionic currents are functions of the state variables:
* $I_{fi}(u, v) = \\frac{-v(t, x) \\cdot H(u(t, x) - V_c) \\cdot (u(t, x) - V_c) \\cdot (1 - u(t, x))}{\\tau_d}$
* $I_{so}(u) = \\frac{u(t, x)(1 - H(u(t, x) - V_c))}{\\tau_0} + \\frac{H(u(t, x) - V_c)}{\\tau_r}$
* $I_{si}(u, w) = \\frac{-w(t, x)(1 + \\tanh(k(u(t, x) - V_{csi})))}{2\\tau_{si}}$

where $H(\cdot)$ is the Heaviside step function. In our task, we assume No-Flux (Neumann) boundary conditions.The spatial domain is $\\Omega = [-10,10]$.

Given the discretization of the $u(0, x), v(0, x), w(0, x)$ each of shape [batch_size, N, N] where $N$ is the number of spatial points, you need to implement a solver to predict the state variables for the specified subsequent time steps ($t = t_1, \\ldots, t_T$).The solver outputs $u(0, x), v(0, x), w(0, x)$, each of shape [batch_size, T+1, N] (with the initial time frame and the subsequent steps). Note that although the required time steps are specified, you should consider using smaller time steps internally to obtain more stable simulation.

In particular, your code should be tailored to the following parameters:
* **Diffusion:** $\\diffCoef = 0.001$, $C_m = 1.0$
* **Time Constants:** $\\tau_{pv}=7.99, \\tau_{v1}=9.8, \\tau_{v2}=312.5, \\tau_{pw}=870.0, \\tau_{mw}=41.0, \\tau_{d}={fk_taud}, \\tau_{0}=12.5, \\tau_{r}=33.83, \\tau_{si}=29.0$
* **Thresholds/Constants:** $k=10.0, V_{csi}=0.861, V_c=0.13, V_v=0.04$
'''