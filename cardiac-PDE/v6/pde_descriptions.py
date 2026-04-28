fenton_karma = '''
The PDE system is a 2D reaction-diffusion model, describing the evolution of the normalized transmembrane potential $u(t, x)$ and two gating variables $v(t, x)$ and $w(t, x)$:

\\begin{{equation}}
\\begin{{cases}} 
\\partial_t u(t, x) = D \\nabla^2 u(t, x) - \\frac{{I_{{fi}}(u, v) + I_{{so}}(u) + I_{{si}}(u, w)}}{{C_m}} \\\\
\\partial_t v(t, x) = 
    \\begin{{cases}} 
    \\frac{{1-v(t, x)}}{{\\tau_{{mv}}(u)}} & u(t, x) < V_c \\\\ 
    \\frac{{-v(t, x)}}{{\\tau_{{pv}}}} & u(t, x) \\ge V_c 
    \\end{{cases}} \\\\
\\partial_t w(t, x) = 
    \\begin{{cases}} 
    \\frac{{1-w(t, x)}}{{\\tau_{{mw}}}} & u(t, x) < V_c \\\\ 
    \\frac{{-w(t, x)}}{{\\tau_{{pw}}}} & u(t, x) \\ge V_c 
    \\end{{cases}}\\\\
    
    I_{{fi}}(u, v) = \\frac{{-v(t, x) \\cdot H(u(t, x) - V_c) \\cdot (u(t, x) - V_c) \\cdot (1 - u(t, x))}}{{\\tau_d}}
\\\\
     I_{{so}}(u) = \\frac{{u(t, x)(1 - H(u(t, x) - V_c))}}{{\\tau_0}} + \\frac{{H(u(t, x) - V_c)}}{{\\tau_r}}
\\\\
     I_{{si}}(u, w) = \\frac{{-w(t, x)(1 + \\tanh(k(u(t, x) - V_{{csi}})))}}{{2\\tau_{{si}}}}\\\\
     H(x) = 
    \\begin{{cases}} 
    0 & x < 0 \\\\
    1 & x \\ge 0 
    \\end{{cases}}
\\end{{cases}}
\\end{{equation}}

where $x \\in (-10,10)^2$ and $t \\in (0,T]$. In our task, we assume No-Flux (Neumann) boundary conditions. The spatial domain is $\\Omega = [-10,10]$.

Given the discretization of $u(0, x), v(0, x), w(0, x)$ each of shape $[batch_size, N, N]$ where $N$ is the number of spatial points, you need to implement a solver to predict the state variables for the specified subsequent time steps ($t = t_1, \\dots, t_T$). The solver outputs $u, v, w$, each of shape $[batch_size, T+1, N]$ (including the initial time frame and subsequent steps). 

To maintain stability, internal time-stepping smaller than the required output intervals should be considered.

Model Parameters are:
    $D = 0.001$, $C_m = 1.0,\\tau_{{pv}}=7.99, \\tau_{{v1}}=9.8, \\tau_{{v2}}=312.5, \\tau_{{pw}}=870.0, \\tau_{{mw}}=41.0, \\tau_{{0}}=12.5, \\tau_{{r}}=33.83, \\tau_{{si}}=29.0,k=10.0, V_{{csi}}=0.861, V_c=0.13, V_v=0.04, \\tau_{{d}}=\\{tau_d}$

**Important implementation notes**:

- Use **512 interior spatial points**

- The domain is $x \\in [-10,10]$ with $dx \\approx 3.90625 \\times 10^{{-2}}$

- Time horizon is $T=100.0$ with $dt =2.5 \\times 10^{{-2}}$

- The boundary conditions must be enforced at every time step

- Use finite difference for spatial discretization (2nd order central differences
recommended)

'''

advection = '''
The PDE system is a 1D advection model:

\\begin{{equation}}
\\begin{{cases}} 
\\partial_t u(t, x) = -\\beta \\partial_x u(t,x) \\\\
\\end{{cases}}
\\end{{equation}}

where $x \\in (0,1)$ and $t \\in (0,T]$. The spatial domain is $\\Omega = [0,1]$.
    
Given the discretization of $u(0, x)$ of shape $[batch_size, N]$ where $N$ is the number of spatial points, you need to implement a solver to predict the state variables for the specified subsequent time steps ($t = t_1, \\dots, t_T$). The solver outputs $u$, each of shape $[batch_size, T+1, N]$ (including the initial time frame and subsequent steps). 

To maintain stability, internal time-stepping smaller than the required output intervals should be considered.

Model Parameters are:
    $\\beta={beta}$

    **Important implementation notes**:

- Use **1024 interior spatial points**

- The domain is $x \\in [0,1]$ with $dx \\approx 9.765625 \\times 10^{{-4}}$

- Time horizon is $T=2.0$ with $dt < 1.0 \\times 10^{{-3}}$

- Use periodic boundary conditions.

'''

burgers = '''
The PDE system is a 1D advection model:

\\begin{{equation}}
\\begin{{cases}} 
\\partial_t u(t, x) + \\partial_x (u(t,x)^2) / 2 = \\nu / 3.1415926 *  \\partial_{{xx}} u(t,x) \\\\
\\end{{cases}}
\\end{{equation}}

where $x \\in (0,1)$ and $t \\in (0,T]$. The spatial domain is $\\Omega = [0,1]$.
    
Given the discretization of $u(0, x)$ of shape $[batch_size, N]$ where $N$ is the number of spatial points, you need to implement a solver to predict the state variables for the specified subsequent time steps ($t = t_1, \\dots, t_T$). The solver outputs $u$, each of shape $[batch_size, T+1, N]$ (including the initial time frame and subsequent steps). 

To maintain stability, internal time-stepping smaller than the required output intervals should be considered.

Model Parameters are:
    $\\nu={nu}$

    **Important implementation notes**:

- Use **1024 interior spatial points**

- The domain is $x \\in [0,1]$ with $dx \\approx 9.765625 \\times 10^{{-4}}$

- Time horizon is $T=2.0$ with $dt < 1.0 \\times 10^{{-4}}$

- Use periodic boundary conditions.

'''

twoD_reaction_diffusion = '''
The PDE system is a 2D reaction-diffusion model:

\\begin{{equation}}
\\begin{{cases}} 
\\partial_t u(t,x) = D_u \\partial_{{xx}} u(t,x) + D_u \\partial_{{yy}} u(t,x) + u(t,x) - u(t,x)^3 - k - v \\\\
\\partial_t v(t,x) = D_v \\partial_{{xx}} v(t,x) + D_v \\partial_{{yy}} v(t,x) + u(t,x) - v(t,x)
\\end{{cases}}
\\end{{equation}}

where $x \\in (-1,1)^2$ and $t \\in (0,T]$. The spatial domain is $\\Omega = [-1,1]$.
    
Given the discretization of $u(0, x)$ of shape $[batch_size, N]$ where $N$ is the number of spatial points, you need to implement a solver to predict the state variables for the specified subsequent time steps ($t = t_1, \\dots, t_T$). The solver outputs $u$, each of shape $[batch_size, T+1, N]$ (including the initial time frame and subsequent steps). 

To maintain stability, internal time-stepping smaller than the required output intervals should be considered.

Model Parameters are:
    $D_u = 1 \\times 10^{{-3}}$,
    $D_v = 5 \\times 10^{{-3}}$,
    $k = 5 \\times 10^{{-3}}$,

    **Important implementation notes**:

- Use **128 interior spatial points**

- The domain is $x \\in [-1,1]$ with $dx \\approx 1.5625 \\times 10^{{-2}}$

- Time horizon is $T=1.0$ with $dt < 1.0 \\times 10^{{-4}}$

- Use No-Flux (Neumann) boundary conditions.

'''

advection_beta0_1 = advection
advection_beta1_0 = advection
burgers_nu0_001 = burgers
burgers_nu1_0 = burgers