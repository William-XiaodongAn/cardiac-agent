fk_description = r"""
The PDE system is a 2D reaction-diffusion model (Fenton-Karma 3V), describing the evolution of the normalized transmembrane potential $u(t, x)$ and two gating variables $v(t, x)$ and $w(t, x)$:

\begin{{cases}}
\partial_t u(t, x) = D \nabla^2 u(t, x) - \frac{{I_{{fi}}(u, v) + I_{{so}}(u) + I_{{si}}(u, w)}}{{C_m}} \\
\partial_t v(t, x) =
    \begin{{cases}}
    \frac{{1-v(t, x)}}{{\tau_{{mv}}(u)}} & u(t, x) < V_c \\
    \frac{{-v(t, x)}}{{\tau_{{pv}}}} & u(t, x) \ge V_c
    \end{{cases}} \\
\partial_t w(t, x) =
    \begin{{cases}}
    \frac{{1-w(t, x)}}{{\tau_{{mw}}}} & u(t, x) < V_c \\
    \frac{{-w(t, x)}}{{\tau_{{pw}}}} & u(t, x) \ge V_c
    \end{{cases}}
\end{{cases}}

where $x \in (0,1)^2$ and $t \in (0,T]$. The ionic currents are:

- $I_{{fi}}(u, v) = \frac{{-v \cdot H(u - V_c) \cdot (u - V_c) \cdot (1 - u)}}{{\tau_d}}$
- $I_{{so}}(u) = \frac{{u(1 - H(u - V_c))}}{{\tau_0}} + \frac{{H(u - V_c)}}{{\tau_r}}$
- $I_{{si}}(u, w) = \frac{{-w(1 + \tanh(k(u - V_{{csi}})))}}{{2\tau_{{si}}}}$

where $H(\cdot)$ is the Heaviside step function, and $\tau_{{mv}}(u) = (1-H(u-V_v))\tau_{{v1}} + H(u-V_v)\tau_{{v2}}$.

----end of PDEs----

In our task, we assume No-Flux (Neumann) boundary conditions. The spatial domain is $\Omega = [-10,10]^2$.

Given the discretization of $u(0, x), v(0, x), w(0, x)$ each of shape $[batch\_size, N, N]$ where $N$ is the number of spatial points, you need to implement a solver to predict the state variables for the specified subsequent time steps ($t = t_1, \dots, t_T$). The solver outputs $u, v, w$, each of shape $[batch\_size, T+1, N, N]$ (including the initial time frame and subsequent steps).

To maintain stability, internal time-stepping smaller than the required output intervals should be considered.

Model Parameters:
    $D = 0.001$, $C_m = 1.0$, $\tau_{{pv}}=7.99$, $\tau_{{v1}}=9.8$, $\tau_{{v2}}=312.5$,
    $\tau_{{pw}}=870.0$, $\tau_{{mw}}=41.0$, $\tau_{{0}}=12.5$, $\tau_{{r}}=33.83$,
    $\tau_{{si}}=29.0$, $k=10.0$, $V_{{csi}}=0.861$, $V_c=0.13$, $V_v=0.04$,
    $\tau_d = {tau_d}$

Important implementation notes:
- Use **512 interior spatial points** (N=512)
- The domain is $x \in [-10,10]$ so domain size = 20, with $dx = 20/N \approx 3.90625 \times 10^{{-2}}$
- HOWEVER, the ground truth uses $dx = 10/N \approx 1.953125 \times 10^{{-2}}$ (domain_size=10 convention)
- Time horizon is $T=100.0$ with $dt = 2.5 \times 10^{{-2}}$
- The boundary conditions must be enforced at every time step (Neumann = replicate edge values)
- Use finite difference for spatial discretization (2nd order central differences, 5-point stencil for 2D)
"""
