tp06_model = '''
The PDE system is a 2D reaction-diffusion model representing the Ten Tusscher-Noble-Noble-Panfilov (TP06) human ventricular action potential with 17 state variables.

\\begin{{equation}}
\\begin{{cases}} 
\\partial_t V(t, x) = D \\nabla^2 V(t, x) - \\frac{{I_{{ion}} + I_{{stim}}}}{{C_m}} \\\\
I_{{ion}} = \\sum C_i I_i \\\\
\\partial_t y_i = \\frac{{y_{{i,\\infty}} - y_i}}{{\\tau_{{y_i}}}}, \\quad y_i \\in \\{m, h, j, d, f, f_2, f_{{CaSS}}, r, s, x_s, x_{{r1}}, x_{{r2}}\\} \\\\
\\partial_t [Na^+]_i = -\\frac{{(I_{{Na}} + I_{{bNa}} + 3I_{{NaK}} + 3I_{{NaCa}}) C_m}}{{V_c F}} \\cdot capacitance \\\\
\\Delta [Ca^{{2+}}]_{{free}} = \\frac{{\\sqrt{{b^2 + 4c}} - b}}{{2}} \\text{ (Quadratic Buffering Solution)}
\\end{{cases}}
\\end{{equation}}

Where the quadratic terms for each compartment are derived from total calcium change:
$b = Buf - [Ca]_{{buf}} - \\Delta [Ca]_{{unbuf}} - [Ca] + K_{{buf}}$
$c = K_{{buf}}([Ca]_{{buf}} + \\Delta [Ca]_{{unbuf}} + [Ca])$

Model Parameters:
$D = 0.001$, $C_m = 1.0$, $capacitance = 0.185$, $V_c = 0.016404$, $V_{{sr}} = 0.001094$, $V_{{ss}} = 0.00005468$, $RR = 8314.3$, $FF = 96486.7$, $TT = 310.0$, $K_o = 5.4$, $Ca_o = 2.0$, $Na_o = 140.0$, $Buf_c = 0.2$, $K_{{bufc}} = 0.001$, $Buf_{{sr}} = 10.0$, $K_{{bufsr}} = 0.3$, $Buf_{{ss}} = 0.4$, $K_{{bufss}} = 0.00025$, $V_{{maxup}} = 0.006375$, $K_{{up}} = 0.00025$, $V_{{rel}} = 0.102$, $V_{{leak}} = 0.00036$, $V_{{xfer}} = 0.0038$, $G_{{Kr}} = 0.153$, $G_{{K1}} = 5.405$, $G_{{Na}} = 14.838$, $G_{{CaL}} = 0.00003980$, $knak = 2.724$, $knaca = 1000.0$, $G_{{ks\\_epi}} = 0.392$, $G_{{to\\_epi}} = 0.294$, $C_{{Na}}=1.0, C_{{NaCa}}=1.0, C_{{to}}=1.0, C_{{CaL}}=1.0, C_{{Kr}}=1.0, C_{{Ks}}=1.0, C_{{K1}}=1.0, C_{{NaK}}=1.0, C_{{bNa}}=1.0, C_{{pK}}=1.0, C_{{bCa}}=1.0, C_{{pCa}}=1.0, C_{{leak}}=1.0, C_{{up}}=1.0, C_{{rel}}=1.0, C_{{xfer}}=1.0$.

**Important implementation notes**:
- Use 512 interior spatial points.
- Spatial domain $x \\in [0,12]$ with $dx = 0.0234375$.
- Time step $dt = 0.1$.
- Laplacian: 9-point weighted stencil with $\\gamma = 1/3$.
- Boundary conditions: No-Flux (Neumann) for $V$.
'''

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
\\tau_{{mv}}(u) = 
    \\begin{{cases}} 
    \\tau_{{v1}} & u(t, x) < V_v \\\\ 
    \\tau_{{v2}} & u(t, x) \\ge V_v 
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

To maintain stability, internal time-stepping smaller than the required output intervals might be considered.

Model Parameters are:
    $D = 0.001$, $C_m = 1.0,\\tau_{{pv}}=7.99, \\tau_{{v1}}=9.8, \\tau_{{v2}}=312.5, \\tau_{{pw}}=870.0, \\tau_{{mw}}=41.0, \\tau_{{0}}=12.5, \\tau_{{r}}=33.83, \\tau_{{si}}=29.0,k=10.0, V_{{csi}}=0.861, V_c=0.13, V_v=0.04, \\tau_{{d}}=\\{tau_d}$

**Important implementation notes**:

- Use 512 interior spatial points

- The domain is $x \\in [0,10]$ with $dx \\approx 1.953125 \\times 10^{{-2}}$

- Time horizon is $T=100.0$ with $dt =2.5 \\times 10^{{-2}}$

- Use No-Flux (Neumann) boundary conditions.

'''

advection = '''
The PDE system is a 1D advection model:

\\begin{{equation}}
\\begin{{cases}} 
\\partial_t u(t, x) = -\\beta \\partial_x u(t,x) \\\\
\\end{{cases}}
\\end{{equation}}

To maintain stability, internal time-stepping smaller than the required output intervals should be considered.

Model Parameters are:
    $\\beta={beta}$

    **Important implementation notes**:

- Use 1024 interior spatial points

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

To maintain stability, internal time-stepping smaller than the required output intervals should be considered.

Model Parameters are:
    $\\nu={nu}$

    **Important implementation notes**:

- Use 1024 interior spatial points

- The domain is $x \\in [0,1]$ with $dx \\approx 9.765625 \\times 10^{{-4}}$

- Time horizon is $T=2.0$ with $dt < 1.0 \\times 10^{{-4}}$

- Use periodic boundary conditions.

'''

oneD_reaction_diffusion = '''
The PDE system is a 2D reaction-diffusion model:

\\begin{{equation}}
\\begin{{cases}} 
\\partial_t u(t,x) - \\nu \\partial_{{xx}} u(t,x) - \\rho u(t,x) (1 - u(t,x)) = 0 \\\\
\\end{{cases}}
\\end{{equation}}

To maintain stability, internal time-stepping smaller than the required output intervals might be considered.

Use 1024 interior spatial points

The domain is $x \\in [0,1]$ with $dx \\approx 9.765625 \\times 10^{{-4}}$

Time horizon is $T=1.0$ with $dt < 1.0 \\times 10^{{-4}}$

Model Parameters are:
    $\\nu = {nu}$,
    $\\rho = {rho}$,

    **Important implementation notes**:

- Use periodic boundary conditions. 

- Source term handled via Piecewise-Exact Solution

'''

twoD_reaction_diffusion = '''
The PDE system is a 2D reaction-diffusion model:

\\begin{{equation}}
\\begin{{cases}} 
\\partial_t u(t,x) = D_u \\partial_{{xx}} u(t,x) + D_u \\partial_{{yy}} u(t,x) + u(t,x) - u(t,x)^3 - k - v \\\\
\\partial_t v(t,x) = D_v \\partial_{{xx}} v(t,x) + D_v \\partial_{{yy}} v(t,x) + u(t,x) - v(t,x)
\\end{{cases}}
\\end{{equation}}

To maintain stability, internal time-stepping smaller than the required output intervals might be considered.

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
oneD_reaction_diffusion_Nu0_5_Rho1_0 = oneD_reaction_diffusion