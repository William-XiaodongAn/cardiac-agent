TNNP = '''
The PDE system is a 19-state-variables model representing the Ten Tusscher-Noble-Noble-Panfilov (TP06) human ventricular action potential with 17 state variables.
\\begin{{equation}}
inverseVcF2 = \\frac{{1}}{{2 \\cdot Vc \\cdot FF}} \\\\
inverseVcF = \\frac{{1}}{{Vc \\cdot FF}} \\\\
inversevssF2 = \\frac{{1}}{{2 \\cdot Vss \\cdot FF}} \\\\
rtof = \\frac{{RR \\cdot TT}}{{FF}} \\\\
fort = \\frac{{1}}{{rtof}} \\\\
KmNai3 = KmNai^3 \\\\
Nao3 = Nao^3 \\\\
Gkrfactor = \\sqrt{{\\frac{{Ko}}{{5.4}}}}\\\\
AM = \\frac{{1}}{{1 + \\exp\\left(\\frac{{-60 - V}}{{5}}\\right)}} \\\\
BM = \\frac{{0.1}}{{1 + \\exp\\left(\\frac{{V + 35}}{{5}}\\right)}} + \\frac{{0.10}}{{1 + \\exp\\left(\\frac{{V - 50}}{{200}}\\right)}} \\\\
minft = \\frac{{1}}{{\\left(1 + \\exp\\left(\\frac{{-56.86 - V}}{{9.03}}\\right)\\right)^2}} \\\\
\\tau_M = AM \\cdot BM \\\\
exptaumt = \\exp\\left(-\\frac{{dt}}{{\\tau_M}}\\right) \\\\
hinft = \\frac{{1}}{{\\left(1 + \\exp\\left(\\frac{{V + 71.55}}{{7.43}}\\right)\\right)^2}} \\\\
sm = minft - (minft - sm) \\cdot exptaumt \\\\
AH = \\begin{{cases}} 0, & V \\ge -40 \\\\ 0.057 \\exp\\left(-\\frac{{V + 80}}{{6.8}}\\right), & V < -40 \\end{{cases}} \\\\
BH = \\begin{{cases}} \\frac{{0.77}}{{0.13 \\left(1 + \\exp\\left(-\\frac{{V + 10.66}}{{11.1}}\\right)\\right)}}, & V \\ge -40 \\\\ 2.7 \\exp(0.079 \\cdot V) + 3.1 \\times 10^5 \\exp(0.3485 \\cdot V), & V < -40 \\end{{cases}} \\\\
\\tau_H = \\frac{{1.0}}{{AH + BH}} \\\\
exptauht = \\exp\\left(-\\frac{{dt}}{{\\tau_H}}\\right) \\\\
sh = hinft - (hinft - sh) \\cdot exptauht \\\\
AJ = \\begin{{cases}} 0, & V \\ge -40 \\\\ \\frac{{\\left(-2.5428 \\times 10^4 \\exp(0.2444 \\cdot V) - 6.948 \\times 10^{{-6}} \\exp(-0.04391 \\cdot V)\\right) \\cdot (V + 37.78)}}{{1 + \\exp(0.311 \\cdot (V + 79.23))}}, & V < -40 \\end{{cases}} \\\\
BJ = \\begin{{cases}} \\frac{{0.6 \\exp(0.057 \\cdot V)}}{{1 + \\exp(-0.1 \\cdot (V + 32))}}, & V \\ge -40 \\\\ \\frac{{0.02424 \\exp(-0.01052 \\cdot V)}}{{1 + \\exp(-0.1378 \\cdot (V + 40.14))}}, & V < -40 \\end{{cases}} \\\\
\\tau_J = \\frac{{1.0}}{{AJ + BJ}} \\\\
exptaujt = \\exp\\left(-\\frac{{dt}}{{\\tau_J}}\\right) \\\\
sj = hinft - (hinft - sj) \\cdot exptaujt \\\\
xsinft = \\frac{{1}}{{1 + \\exp\\left(\\frac{{-5 - V}}{{14}}\\right)}} \\\\
Axs = \\frac{{1400}}{{\\sqrt{{1 + \\exp\\left(\\frac{{5 - V}}{{6}}\\right)}}}} \\\\
Bxs = \\frac{{1}}{{1 + \\exp\\left(\\frac{{V - 35}}{{15}}\\right)}} \\\\
\\tau_{{Xs}} = Axs \\cdot Bxs + 80 \\\\
exptauxst = \\exp\\left(-\\frac{{dt}}{{\\tau_{{Xs}}}}\\right) \\\\
sxs = xsinft - (xsinft - sxs) \\cdot exptauxst\\\\
dinft = \\frac{{1}}{{1 + \\exp\\left(\\frac{{-8 - V}}{{7.5}}\\right)}} \\\\
Ad = \\frac{{1.4}}{{1 + \\exp\\left(\\frac{{-35 - V}}{{13}}\\right)}} + 0.25 \\\\
Bd = \\frac{{1.4}}{{1 + \\exp\\left(\\frac{{V + 5}}{{5}}\\right)}} \\\\
Cd = \\frac{{1}}{{1 + \\exp\\left(\\frac{{50 - V}}{{20}}\\right)}} \\\\
\\tau_D = Ad \\cdot Bd + Cd \\\\
exptaudt = \\exp\\left(-\\frac{{dt}}{{\\tau_D}}\\right) \\\\
sd = dinft - (dinft - sd) \\cdot exptaudt \\\\
finft = \\frac{{1}}{{1 + \\exp\\left(\\frac{{V + 20}}{{7}}\\right)}} \\\\
Af = 1102.5 \\exp\\left(-\\frac{{(V + 27)^2}}{{225}}\\right) \\\\
Bf = \\frac{{200}}{{1 + \\exp\\left(\\frac{{13 - V}}{{10}}\\right)}} \\\\
Cf = \\frac{{180}}{{1 + \\exp\\left(\\frac{{V + 30}}{{10}}\\right)}} + 20 \\\\
\\tau_F = Af + Bf + Cf \\\\
exptauft = \\exp\\left(-\\frac{{dt}}{{\\tau_F}}\\right) \\\\
sf = finft - (finft - sf) \\cdot exptauft \\\\
f2inft = \\frac{{0.67}}{{1 + \\exp\\left(\\frac{{V + 35}}{{7}}\\right)}} + 0.33 \\\\
Af2 = 600 \\exp\\left(-\\frac{{(V + 25)^2}}{{49}}\\right) \\\\
Bf2 = \\frac{{31}}{{1 + \\exp\\left(\\frac{{25 - V}}{{10}}\\right)}} \\\\
Cf2 = \\frac{{16}}{{1 + \\exp\\left(\\frac{{V + 30}}{{10}}\\right)}} \\\\
\\tau_{{F2}} = Af2 + Bf2 + Cf2 \\\\
exptauf2t = \\exp\\left(-\\frac{{dt}}{{\\tau_{{F2}}}}\\right) \\\\
sf2 = f2inft - (f2inft - sf2) \\cdot exptauf2t \\\\
fcassinft = \\frac{{0.6}}{{1 + \\left(\\frac{{CaSS}}{{0.05}}\\right)^2}} + 0.4 \\\\
\\tau_{{fcass}} = \\frac{{80}}{{1 + \\left(\\frac{{CaSS}}{{0.05}}\\right)^2}} + 2 \\\\
exptaufcasst = \\exp\\left(-\\frac{{dt}}{{\\tau_{{fcass}}}}\\right) \\\\
exptaufcassinf = \\exp\\left(-\\frac{{dt}}{{2.0}}\\right) \\\\
casshi = 1.0 \\\\
FCaSS\\_INF = \\begin{{cases}} 0.4, & CaSS \\ge casshi \\\\ fcassinft, & CaSS < casshi \\end{{cases}} \\\\
exptaufcass = \\begin{{cases}} exptaufcassinf, & CaSS \\ge casshi \\\\ exptaufcasst, & CaSS < casshi \\end{{cases}} \\\\
sfcass = FCaSS\\_INF - (FCaSS\\_INF - sfcass) \\cdot exptaufcass\\\\
rinft = \\frac{{1}}{{1 + \\exp\\left(\\frac{{20 - V}}{{6}}\\right)}} \\\\
sinft = \\frac{{1}}{{1 + \\exp\\left(\\frac{{V + 20}}{{5}}\\right)}} \\\\
\\tau_R = 9.5 \\exp\\left(-\\frac{{(V + 40)^2}}{{1800}}\\right) + 0.8 \\\\
\\tau_S = 85 \\exp\\left(-\\frac{{(V + 45)^2}}{{320}}\\right) + \\frac{{5}}{{1 + \\exp\\left(\\frac{{V - 20}}{{5}}\\right)}} + 3 \\\\
exptaurt = \\exp\\left(-\\frac{{dt}}{{\\tau_R}}\\right) \\\\
exptaust = \\exp\\left(-\\frac{{dt}}{{\\tau_S}}\\right) \\\\
sr = rinft - (rinft - sr) \\cdot exptaurt \\\\
ss = sinft - (sinft - ss) \\cdot exptaust \\\\
xr1inft = \\frac{{1}}{{1 + \\exp\\left(\\frac{{-26 - V}}{{7}}\\right)}} \\\\
axr1 = \\frac{{450}}{{1 + \\exp\\left(\\frac{{-45 - V}}{{10}}\\right)}} \\\\
bxr1 = \\frac{{6}}{{1 + \\exp\\left(\\frac{{V + 30}}{{11.5}}\\right)}} \\\\
\\tau_{{Xr1}} = axr1 \\cdot bxr1 \\\\
exptauxr1t = \\exp\\left(-\\frac{{dt}}{{\\tau_{{Xr1}}}}\\right) \\\\
sxr1 = xr1inft - (xr1inft - sxr1) \\cdot exptauxr1t \\\\
xr2inft = \\frac{{1}}{{1 + \\exp\\left(\\frac{{V + 88}}{{24}}\\right)}} \\\\
axr2 = \\frac{{3}}{{1 + \\exp\\left(\\frac{{-60 - V}}{{20}}\\right)}} \\\\
bxr2 = \\frac{{1.12}}{{1 + \\exp\\left(\\frac{{V - 60}}{{20}}\\right)}} \\\\
\\tau_{{Xr2}} = axr2 \\cdot bxr2 \\\\
exptauxr2t = \\exp\\left(-\\frac{{dt}}{{\\tau_{{Xr2}}}}\\right) \\\\
sxr2 = xr2inft - (xr2inft - sxr2) \\cdot exptauxr2t\\\\
Ek = rtof \\cdot \\ln\\left(\\frac{{Ko}}{{Ki}}\\right) \\\\
Ena = rtof \\cdot \\ln\\left(\\frac{{Nao}}{{Nai}}\\right) \\\\
Eks = rtof \\cdot \\ln\\left(\\frac{{Ko + pKNa \\cdot Nao}}{{Ki + pKNa \\cdot Nai}}\\right) \\\\
Eca = 0.5 \\cdot rtof \\cdot \\ln\\left(\\frac{{Cao}}{{Cai}}\\right) \\\\
INa = GNa \\cdot sm^3 \\cdot sh \\cdot sj \\cdot (V - Ena) \\\\
IKr = Gkr \\cdot Gkrfactor \\cdot sxr1 \\cdot sxr2 \\cdot (V - Ek) \\\\
IKs = Gks \\cdot sxs^2 \\cdot (V - Eks) \\\\
Ito = Gto \\cdot sr \\cdot ss \\cdot (V - Ek) \\\\
vmek = V - Ek \\\\
Ak1 = \\frac{{0.1}}{{1 + \\exp(0.06 \\cdot (vmek - 200))}} \\\\
Bk1 = \\frac{{3 \\exp(0.0002 \\cdot (vmek + 100)) + \\exp(0.1 \\cdot (vmek - 10))}}{{1 + \\exp(-0.5 \\cdot vmek)}} \\\\
ik1coefft = \\frac{{GK1 \\cdot Ak1}}{{Ak1 + Bk1}} \\\\
IK1 = ik1coefft \\cdot (V - Ek) \\\\
ipkcoefft = \\frac{{GpK}}{{1 + \\exp\\left(\\frac{{25 - V}}{{5.98}}\\right)}} \\\\
IpK = ipkcoefft \\cdot (V - Ek) \\\\
IbNa = GbNa \\cdot (V - Ena) \\\\
inakcoefft = \\left(\\frac{{1}}{{1 + 0.1245 \\exp(-0.1 \\cdot V \\cdot fort) + 0.0353 \\exp(-V \\cdot fort)}}\\right) \\cdot knak \\cdot \\left(\\frac{{Ko}}{{Ko + KmK}}\\right) \\\\
INaK = inakcoefft \\cdot \\left(\\frac{{Nai}}{{Nai + KmNa}}\\right) \\\\
temp = \\exp((n - 1) \\cdot V \\cdot fort) \\\\
temp2 = \\frac{{knaca}}{{(KmNai3 + Nao3) \\cdot (KmCa + Cao) \\cdot (1 + ksat \\cdot temp)}} \\\\
inaca1t = temp2 \\cdot \\exp(n \\cdot V \\cdot fort) \\cdot Cao \\\\
inaca2t = temp2 \\cdot temp \\cdot Nao3 \\cdot alphanaca \\\\
INaCa = inaca1t \\cdot Nai^3 - inaca2t \\cdot Cai\\\\
dNai = -(INa + IbNa + 3 \\cdot INaK + 3 \\cdot INaCa) \\cdot inverseVcF \\cdot CAPACITANCE \\\\
Nai = Nai + dt \\cdot dNai \\\\
Istim = 0.0 \\\\
dKi = -(Istim + IK1 + Ito + IKr + IKs - 2 \\cdot INaK + IpK) \\cdot inverseVcF \\cdot CAPACITANCE \\\\
Ki = Ki + dt \\cdot dKi \\\\
ISumNaK = INa + IbNa + INaK + IK1 + IKr + IKs + IpK + Ito \\\\
temp\\_ical = \\exp(2 \\cdot (V - 15) \\cdot fort) \\\\
ical1t = \\begin{{cases}} GCaL \\cdot 4 \\cdot 10^{{-4}} \\cdot (FF \\cdot fort) \\cdot \\frac{{0.25 \\cdot \\exp(2 \\cdot 10^{{-4}} \\cdot fort)}}{{\\exp(2 \\cdot 10^{{-4}} \\cdot fort) - 1}}, & |V - 15| < 10^{{-4}} \\\\ GCaL \\cdot 4 \\cdot (V - 15) \\cdot (FF \\cdot fort) \\cdot \\frac{{0.25 \\cdot temp\\_ical}}{{temp\\_ical - 1}}, & \\text{{otherwise}} \\end{{cases}} \\\\
ical2t = \\begin{{cases}} GCaL \\cdot 4 \\cdot 10^{{-4}} \\cdot (FF \\cdot fort) \\cdot \\frac{{Cao}}{{\\exp(2 \\cdot 10^{{-4}} \\cdot fort) - 1}}, & |V - 15| < 10^{{-4}} \\\\ GCaL \\cdot 4 \\cdot (V - 15) \\cdot (FF \\cdot fort) \\cdot \\frac{{Cao}}{{temp\\_ical - 1}}, & \\text{{otherwise}} \\end{{cases}} \\\\
ICaL = sd \\cdot sf \\cdot sf2 \\cdot sfcass \\cdot (ical1t \\cdot CaSS - ical2t) \\\\
IpCa = \\frac{{GpCa \\cdot Cai}}{{KpCa + Cai}} \\\\
IbCa = GbCa \\cdot (V - Eca) \\\\
kCaSR = maxsr - \\frac{{maxsr - minsr}}{{1 + \\left(\\frac{{EC}}{{CaSR}}\\right)^2}} \\\\
k1 = \\frac{{k1prime}}{{kCaSR}} \\\\
k2 = k2prime \\cdot kCaSR \\\\
dRR = k4 \\cdot (1 - sRR) - k2 \\cdot CaSS \\cdot sRR \\\\
sRR = sRR + dt \\cdot dRR \\\\
sOO = \\frac{{k1 \\cdot CaSS^2 \\cdot sRR}}{{k3 + k1 \\cdot CaSS^2}} \\\\
Irel = Vrel \\cdot sOO \\cdot (CaSR - CaSS) \\\\
Ileak = Vleak \\cdot (CaSR - Cai) \\\\
Iup = \\frac{{Vmaxup}}{{1 + \\left(\\frac{{Kup}}{{Cai}}\\right)^2}} \\\\
Ixfer = Vxfer \\cdot (CaSS - Cai)\\\\
CaCSQN = \\frac{{Bufsr \\cdot CaSR}}{{CaSR + Kbufsr}} \\\\
dCaSR = dt \\cdot (Iup - Irel - Ileak) \\\\
bjsr = Bufsr - CaCSQN - dCaSR - CaSR + Kbufsr \\\\
cjsr = Kbufsr \\cdot (CaCSQN + dCaSR + CaSR) \\\\
CaSR = \\frac{{\\sqrt{{bjsr^2 + 4 \\cdot cjsr}} - bjsr}}{{2}} \\\\
CaSSBuf = \\frac{{Bufss \\cdot CaSS}}{{CaSS + Kbufss}} \\\\
dCaSS = dt \\cdot \\left(-Ixfer \\cdot \\frac{{Vc}}{{Vss}} + Irel \\cdot \\frac{{Vsr}}{{Vss}} - ICaL \\cdot inversevssF2 \\cdot CAPACITANCE\\right) \\\\
bcss = Bufss - CaSSBuf - dCaSS - CaSS + Kbufss \\\\
ccss = Kbufss \\cdot (CaSSBuf + dCaSS + CaSS) \\\\
CaSS = \\frac{{\\sqrt{{bcss^2 + 4 \\cdot ccss}} - bcss}}{{2}} \\\\
CaBuf = \\frac{{Bufc \\cdot Cai}}{{Cai + Kbufc}} \\\\
dCai = dt \\cdot \\left( -(IbCa + IpCa - 2 \\cdot INaCa) \\cdot inverseVcF2 \\cdot CAPACITANCE - (Iup - Ileak) \\cdot \\frac{{Vsr}}{{Vc}} + Ixfer \\right) \\\\
bc = Bufc - CaBuf - dCai - Cai + Kbufc \\\\
cc = Kbufc \\cdot (CaBuf + dCai + Cai) \\\\
Cai = \\frac{{\\sqrt{{bc^2 + 4 \\cdot cc}} - bc}}{{2}} \\\\
ISumCa = ICaL + IpCa + IbCa \\\\
dVlt2dt =diffCoef \\nabla V \\\\
I\\_sum = ISumCa + ISumNaK + INaCa \\\\
dVlt2dt = dVlt2dt - I\\_sum \\\\
V = V + dVlt2dt \\cdot dt\\\\
\\end{{equation}}

where $x \\in (0,10)^2$ and $t \\in (0,T]$. In our task, we assume No-Flux (Neumann) boundary conditions. The spatial domain is $\\Omega = [0,10]$.

Where the quadratic terms for each compartment are derived from total calcium change:
$b = Buf - [Ca]_{{buf}} - \\Delta [Ca]_{{unbuf}} - [Ca] + K_{{buf}}$
$c = K_{{buf}}([Ca]_{{buf}} + \\Delta [Ca]_{{unbuf}} + [Ca])$

Model Parameters:
$ Ko = 5.4 $,$ Cao = 2.0 $,$ Nao = 140.0 $,$ Vc = 0.016404 $,$ Vsr = 0.001094 $,$ Vss = 0.00005468 $,$ Bufc = 0.2 $,$ Kbufc = 0.001 $,$ Bufsr = 10.0 $,$ Kbufsr = 0.3 $,$ Bufss = 0.4 $,$ Kbufss = 0.00025 $,$ Vmaxup = 0.006375 $,$ Kup = 0.00025 $,$ Vrel = 0.102 $,$ k3 = 0.060 $,$ k4 = 0.005 $,$ k1prime = 0.15 $,$ k2prime = 0.045 $,$ EC = 1.5 $,$ maxsr = 2.5 $,$ minsr = 1.0 $,$ Vleak = 0.00036 $,$ Vxfer = 0.0038 $,$ RR = 8314.3 $,$ FF = 96486.7 $,$ TT = 310.0 $,$ CAPACITANCE = 0.185 $,$ Gks = 0.392 $,$ Gto = 0.294 $,$ Gkr = 0.153 $,$ pKNa = 0.03 $,$ GK1 = 5.405 $,$ alphanaca = z2.5 $,$ GNa = 14.838 $,$ GbNa = 0.00029 $,$ KmK = 1.0 $,$ KmNa = 40.0 $,$ knak = 2.724 $,$ GCaL = 0.00003980 $,$ GbCa = 0.000592 $,$ knaca = 1000.0 $,$ KmNai = 87.5 $,$ KmCa = 1.38 $,$ ksat = 0.1 $,$ n = 0.35 $,$ GpCa = 0.1238 $,$ KpCa = 0.0005 $,$ GpK = 0.0146 $,$ diffCoef = 0.001$.

- Use 512 interior spatial points.
- Spatial domain $x \\in [0,12]$ with $dx = 0.0234375$.
- Time horizon is $T=100.0$ with $dt =2.5 \\times 10^{{-2}}$
- Boundary conditions: No-Flux (Neumann)

**Important implementation notes**:
Texture 1: ($V$, $sRR$, $Nai$, $Ki$)
Texture 2: ($Cai$, $CaSS$, $CaSR$, $ISumCa$)
Texture 3: ($sm$, $sh$, $sj$, $sxs$)
Texture 4: ($sd$, $sf$, $sf2$, $sfcass$)
Texture 5: ($sr$, $ss$, $sxr1$, $sxr2$)

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

where $x \\in (0,10)^2$ and $t \\in (0,T]$. In our task, we assume No-Flux (Neumann) boundary conditions. The spatial domain is $\\Omega = [0,10]$.

Given the discretization of $u(0, x), v(0, x), w(0, x)$ each of shape $[batch_size, N, N]$ where $N$ is the number of spatial points, you need to implement a solver to predict the state variables for the specified subsequent time steps ($t = t_1, \\dots, t_T$). The solver outputs $u, v, w$, each of shape $[batch_size, T+1, N]$ (including the initial time frame and subsequent steps). 

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

where $x \\in (0,1)$ and $t \\in (0,T]$. The spatial domain is $\\Omega = [0,1]$.
    
Given the discretization of $u(0, x)$ of shape $[batch_size, N]$ where $N$ is the number of spatial points, you need to implement a solver to predict the state variables for the specified subsequent time steps ($t = t_1, \\dots, t_T$). The solver outputs $u$, each of shape $[batch_size, T+1, N]$ (including the initial time frame and subsequent steps). 

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

where $x \\in (0,1)$ and $t \\in (0,T]$. The spatial domain is $\\Omega = [0,1]$.
    
Given the discretization of $u(0, x)$ of shape $[batch_size, N]$ where $N$ is the number of spatial points, you need to implement a solver to predict the state variables for the specified subsequent time steps ($t = t_1, \\dots, t_T$). The solver outputs $u$, each of shape $[batch_size, T+1, N]$ (including the initial time frame and subsequent steps). 

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

where $x \\in (0,1)^2$ and $t \\in (0,T]$. The spatial domain is $\\Omega = [0,1]$.
    
Given the discretization of $u(0, x)$ of shape $[batch_size, N]$ where $N$ is the number of spatial points, you need to implement a solver to predict the state variables for the specified subsequent time steps ($t = t_1, \\dots, t_T$). The solver outputs $u$, each of shape $[batch_size, T+1, N]$ (including the initial time frame and subsequent steps). 

To maintain stability, internal time-stepping smaller than the required output intervals should be considered.

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

where $x \\in (-1,1)^2$ and $t \\in (0,T]$. The spatial domain is $\\Omega = [-1,1]$.
    
Given the discretization of $u(0, x)$ of shape $[batch_size, N,N]$ where $N$ is the number of spatial points, you need to implement a solver to predict the state variables for the specified subsequent time steps ($t = t_1, \\dots, t_T$). The solver outputs $u$, each of shape $[batch_size, T+1, N,N]$ (including the initial time frame and subsequent steps). 

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
oneD_reaction_diffusion_Nu0_5_Rho1_0 = oneD_reaction_diffusion