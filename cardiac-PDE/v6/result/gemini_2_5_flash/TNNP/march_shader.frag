precision highp float ;
precision highp int ;

uniform sampler2D   inTexture1 ;
uniform sampler2D   inTexture2 ;
uniform sampler2D   inTexture3 ;
uniform sampler2D   inTexture4 ;
uniform sampler2D   inTexture5 ;

uniform float       dt, dx, dy;

in vec2 cc, pixPos ;

layout (location = 0) out vec4 ocolor1 ;
layout (location = 1) out vec4 ocolor2 ;
layout (location = 2) out vec4 ocolor3 ;
layout (location = 3) out vec4 ocolor4 ;
layout (location = 4) out vec4 ocolor5 ;

#define r1       color1.r
#define g1       color1.g
#define b1       color1.b
#define a1       color1.a

#define r2       color2.r
#define g2       color2.g
#define b2       color2.b
#define a2       color2.a

#define r3       color3.r
#define g3       color3.g
#define b3       color3.b
#define a3       color3.a

#define r4       color4.r
#define g4       color4.g
#define b4       color4.b
#define a4       color4.a

#define r5       color5.r
#define g5       color5.g
#define b5       color5.b
#define a5       color5.a

    const float Ko = 5.4;
    const float Cao = 2.0;
    const float Nao = 140.0;
    const float Vc = 0.016404;
    const float Vsr = 0.001094;
    const float Vss = 5.468e-05;
    const float Bufc = 0.2;
    const float Kbufc = 0.001;
    const float Bufsr = 10.0;
    const float Kbufsr = 0.3;
    const float Bufss = 0.4;
    const float Kbufss = 0.00025;
    const float Vmaxup = 0.006375;
    const float Kup = 0.00025;
    const float Vrel = 0.102;
    const float k3 = 0.06;
    const float k4 = 0.005;
    const float k1prime = 0.15;
    const float k2prime = 0.045;
    const float EC = 1.5;
    const float maxsr = 2.5;
    const float minsr = 1.0;
    const float Vleak = 0.00036;
    const float Vxfer = 0.0038;
    const float RR = 8314.3;
    const float FF = 96486.7;
    const float TT = 310.0;
    const float CAPACITANCE = 0.185;
    const float Gks = 0.392;
    const float Gto = 0.294;
    const float Gkr = 0.153;
    const float pKNa = 0.03;
    const float GK1 = 5.405;
    const float alphanaca = 2.5;
    const float GNa = 14.838;
    const float GbNa = 0.00029;
    const float KmK = 1.0;
    const float KmNa = 40.0;
    const float knak = 2.724;
    const float GCaL = 3.98e-05;
    const float GbCa = 0.000592;
    const float knaca = 1000.0;
    const float KmNai = 87.5;
    const float KmCa = 1.38;
    const float ksat = 0.1;
    const float n = 0.35;
    const float GpCa = 0.1238;
    const float KpCa = 0.0005;
    const float GpK = 0.0146;
    const float diffCoef = 0.001;
// your codes here for helper function

// Main body of the shader
void main() {
    // ii and jj are already normalized pixel steps for dx and dy
    // For Neumann (no-flux) boundary conditions, texture wrap mode GL_CLAMP_TO_EDGE is assumed for samplers.
    // This makes sampling `cc - ii` or `cc + ii` at the boundaries correctly read the edge pixel.

    // read the current state from textures
    vec4 color1 = texture( inTexture1 , cc ) ;
    vec4 color2 = texture( inTexture2 , cc ) ;
    vec4 color3 = texture( inTexture3 , cc ) ;
    vec4 color4 = texture( inTexture4 , cc ) ;
    vec4 color5 = texture( inTexture5 , cc ) ;

    // Map texture channels to state variables
    float V = color1.r;
    float sRR = color1.g;
    float Nai = color1.b;
    float Ki = color1.a;

    float Cai = color2.r;
    float CaSS = color2.g;
    float CaSR = color2.b;
    // ISumCa is an output, not an input state variable.

    float sm = color3.r;
    float sh = color3.g;
    float sj = color3.b;
    float sxs = color3.a;

    float sd = color4.r;
    float sf = color4.g;
    float sf2 = color4.b;
    float sfcass = color4.a;

    float sr = color5.r;
    float ss = color5.g;
    float sxr1 = color5.b;
    float sxr2 = color5.a;

    // Intermediate constants and pre-calculations
    const float inverseVcF2 = 1.0 / (2.0 * Vc * FF);
    const float inverseVcF = 1.0 / (Vc * FF);
    const float inversevssF2 = 1.0 / (2.0 * Vss * FF);
    const float rtof = RR * TT / FF;
    const float fort = 1.0 / rtof;
    const float KmNai3 = pow(KmNai, 3.0);
    const float Nao3 = pow(Nao, 3.0);
    const float Gkrfactor = sqrt(Ko / 5.4);

    // Gating variables updates using backward Euler-like formula: s_new = s_inf - (s_inf - s_old) * exp(-dt/tau)
    // M-gate
    float AM = 1.0 / (1.0 + exp((-60.0 - V) / 5.0));
    float BM = 0.1 / (1.0 + exp((V + 35.0) / 5.0)) + 0.10 / (1.0 + exp((V - 50.0) / 200.0));
    float minft = 1.0 / (pow((1.0 + exp((-56.86 - V) / 9.03)), 2.0));
    float tau_M = AM * BM;
    float exptaumt = exp(-dt / tau_M);
    sm = minft - (minft - sm) * exptaumt;

    // H-gate
    float hinft = 1.0 / (pow((1.0 + exp((V + 71.55) / 7.43)), 2.0));
    float AH = (V >= -40.0) ? 0.0 : 0.057 * exp(-(V + 80.0) / 6.8);
    float BH = (V >= -40.0) ? (0.77 / (0.13 * (1.0 + exp(-(V + 10.66) / 11.1)))) : (2.7 * exp(0.079 * V) + 3.1e5 * exp(0.3485 * V));
    float tau_H = 1.0 / (AH + BH);
    float exptauht = exp(-dt / tau_H);
    sh = hinft - (hinft - sh) * exptauht;

    // J-gate
    float AJ = (V >= -40.0) ? 0.0 : ((-2.5428e4 * exp(0.2444 * V) - 6.948e-6 * exp(-0.04391 * V)) * (V + 37.78)) / (1.0 + exp(0.311 * (V + 79.23)));
    float BJ = (V >= -40.0) ? (0.6 * exp(0.057 * V) / (1.0 + exp(-0.1 * (V + 32.0)))) : (0.02424 * exp(-0.01052 * V) / (1.0 + exp(-0.1378 * (V + 40.14))));
    float tau_J = 1.0 / (AJ + BJ);
    float exptaujt = exp(-dt / tau_J);
    sj = hinft - (hinft - sj) * exptaujt; // Note: sj uses hinft as specified in the equations

    // Xs-gate
    float xsinft = 1.0 / (1.0 + exp((-5.0 - V) / 14.0));
    float Axs = 1400.0 / sqrt(1.0 + exp((5.0 - V) / 6.0));
    float Bxs = 1.0 / (1.0 + exp((V - 35.0) / 15.0));
    float tau_Xs = Axs * Bxs + 80.0;
    float exptauxst = exp(-dt / tau_Xs);
    sxs = xsinft - (xsinft - sxs) * exptauxst;

    // D-gate
    float dinft = 1.0 / (1.0 + exp((-8.0 - V) / 7.5));
    float Ad = 1.4 / (1.0 + exp((-35.0 - V) / 13.0)) + 0.25;
    float Bd = 1.4 / (1.0 + exp((V + 5.0) / 5.0));
    float Cd = 1.0 / (1.0 + exp((50.0 - V) / 20.0));
    float tau_D = Ad * Bd + Cd;
    float exptaudt = exp(-dt / tau_D);
    sd = dinft - (dinft - sd) * exptaudt;

    // F-gate
    float finft = 1.0 / (1.0 + exp((V + 20.0) / 7.0));
    float Af = 1102.5 * exp(-pow((V + 27.0), 2.0) / 225.0);
    float Bf = 200.0 / (1.0 + exp((13.0 - V) / 10.0));
    float Cf = 180.0 / (1.0 + exp((V + 30.0) / 10.0)) + 20.0;
    float tau_F = Af + Bf + Cf;
    float exptauft = exp(-dt / tau_F);
    sf = finft - (finft - sf) * exptauft;

    // F2-gate
    float f2inft = 0.67 / (1.0 + exp((V + 35.0) / 7.0)) + 0.33;
    float Af2 = 600.0 * exp(-pow((V + 25.0), 2.0) / 49.0);
    float Bf2 = 31.0 / (1.0 + exp((25.0 - V) / 10.0));
    float Cf2 = 16.0 / (1.0 + exp((V + 30.0) / 10.0));
    float tau_F2 = Af2 + Bf2 + Cf2;
    float exptauf2t = exp(-dt / tau_F2);
    sf2 = f2inft - (f2inft - sf2) * exptauf2t;

    // Fcass-gate
    float fcassinft = 0.6 / (1.0 + pow((CaSS / 0.05), 2.0)) + 0.4;
    float tau_fcass = 80.0 / (1.0 + pow((CaSS / 0.05), 2.0)) + 2.0;
    float exptaufcasst = exp(-dt / tau_fcass);
    float exptaufcassinf = exp(-dt / 2.0);
    const float casshi = 1.0;
    float FCaSS_INF_val = (CaSS >= casshi) ? 0.4 : fcassinft;
    float exptaufcass_val = (CaSS >= casshi) ? exptaufcassinf : exptaufcasst;
    sfcass = FCaSS_INF_val - (FCaSS_INF_val - sfcass) * exptaufcass_val;

    // R-gate
    float rinft = 1.0 / (1.0 + exp((20.0 - V) / 6.0));
    float tau_R = 9.5 * exp(-pow((V + 40.0), 2.0) / 1800.0) + 0.8;
    float exptaurt = exp(-dt / tau_R);
    sr = rinft - (rinft - sr) * exptaurt;

    // S-gate
    float sinft = 1.0 / (1.0 + exp((V + 20.0) / 5.0));
    float tau_S = 85.0 * exp(-pow((V + 45.0), 2.0) / 320.0) + 5.0 / (1.0 + exp((V - 20.0) / 5.0)) + 3.0;
    float exptaust = exp(-dt / tau_S);
    ss = sinft - (sinft - ss) * exptaust;

    // Xr1-gate
    float xr1inft = 1.0 / (1.0 + exp((-26.0 - V) / 7.0));
    float axr1 = 450.0 / (1.0 + exp((-45.0 - V) / 10.0));
    float bxr1 = 6.0 / (1.0 + exp((V + 30.0) / 11.5));
    float tau_Xr1 = axr1 * bxr1;
    float exptauxr1t = exp(-dt / tau_Xr1);
    sxr1 = xr1inft - (xr1inft - sxr1) * exptauxr1t;

    // Xr2-gate
    float xr2inft = 1.0 / (1.0 + exp((V + 88.0) / 24.0));
    float axr2 = 3.0 / (1.0 + exp((-60.0 - V) / 20.0));
    float bxr2 = 1.12 / (1.0 + exp((V - 60.0) / 20.0));
    float tau_Xr2 = axr2 * bxr2;
    float exptauxr2t = exp(-dt / tau_Xr2);
    sxr2 = xr2inft - (xr2inft - sxr2) * exptauxr2t;

    // Reversal Potentials
    float Ek = rtof * log(Ko / Ki);
    float Ena = rtof * log(Nao / Nai);
    float Eks = rtof * log((Ko + pKNa * Nao) / (Ki + pKNa * Nai));
    float Eca = 0.5 * rtof * log(Cao / Cai);

    // Currents
    float INa = GNa * pow(sm, 3.0) * sh * sj * (V - Ena);
    float IKr = Gkr * Gkrfactor * sxr1 * sxr2 * (V - Ek);
    float IKs = Gks * pow(sxs, 2.0) * (V - Eks);
    float Ito = Gto * sr * ss * (V - Ek);

    float vmek = V - Ek;
    float Ak1 = 0.1 / (1.0 + exp(0.06 * (vmek - 200.0)));
    float Bk1 = (3.0 * exp(0.0002 * (vmek + 100.0)) + exp(0.1 * (vmek - 10.0))) / (1.0 + exp(-0.5 * vmek));
    float ik1coefft = (GK1 * Ak1) / (Ak1 + Bk1);
    float IK1 = ik1coefft * (V - Ek);

    float ipkcoefft = GpK / (1.0 + exp((25.0 - V) / 5.98));
    float IpK = ipkcoefft * (V - Ek);
    float IbNa = GbNa * (V - Ena);

    float inakcoefft = (1.0 / (1.0 + 0.1245 * exp(-0.1 * V * fort) + 0.0353 * exp(-V * fort))) * knak * (Ko / (Ko + KmK));
    float INaK = inakcoefft * (Nai / (Nai + KmNa));

    float temp = exp((n - 1.0) * V * fort);
    float temp2 = knaca / ((KmNai3 + Nao3) * (KmCa + Cao) * (1.0 + ksat * temp));
    float inaca1t = temp2 * exp(n * V * fort) * Cao;
    float inaca2t = temp2 * temp * Nao3 * alphanaca;
    float INaCa = inaca1t * pow(Nai, 3.0) - inaca2t * Cai;

    const float Istim = 0.0;

    float ical1t, ical2t;
    const float V_DIFF_THRESHOLD = 1e-4; // For the conditional branch of ICaL calculation
    if (abs(V - 15.0) < V_DIFF_THRESHOLD) {
        float temp_ical_small_val = exp(2.0 * V_DIFF_THRESHOLD * fort);
        ical1t = GCaL * 4.0 * V_DIFF_THRESHOLD * (FF * fort) * (0.25 * temp_ical_small_val / (temp_ical_small_val - 1.0));
        ical2t = GCaL * 4.0 * V_DIFF_THRESHOLD * (FF * fort) * (Cao / (temp_ical_small_val - 1.0));
    } else {
        float temp_ical = exp(2.0 * (V - 15.0) * fort);
        ical1t = GCaL * 4.0 * (V - 15.0) * (FF * fort) * (0.25 * temp_ical / (temp_ical - 1.0));
        ical2t = GCaL * 4.0 * (V - 15.0) * (FF * fort) * (Cao / (temp_ical - 1.0));
    }
    
    float ICaL = sd * sf * sf2 * sfcass * (ical1t * CaSS - ical2t);
    float IpCa = (GpCa * Cai) / (KpCa + Cai);
    float IbCa = GbCa * (V - Eca);

    // SR dynamics
    float kCaSR = maxsr - (maxsr - minsr) / (1.0 + pow((EC / CaSR), 2.0));
    float k1 = k1prime / kCaSR;
    float k2 = k2prime * kCaSR;
    float dRR_val = k4 * (1.0 - sRR) - k2 * CaSS * sRR;
    float sRR_new = sRR + dt * dRR_val;

    float sOO = (k1 * pow(CaSS, 2.0) * sRR_new) / (k3 + k1 * pow(CaSS, 2.0));
    float Irel = Vrel * sOO * (CaSR - CaSS);
    float Ileak = Vleak * (CaSR - Cai);
    float Iup = Vmaxup / (1.0 + pow((Kup / Cai), 2.0));
    float Ixfer = Vxfer * (CaSS - Cai);

    // Ion concentrations updates
    float dNai = -(INa + IbNa + 3.0 * INaK + 3.0 * INaCa) * inverseVcF * CAPACITANCE;
    float Nai_new = Nai + dt * dNai;

    float dKi = -(Istim + IK1 + Ito + IKr + IKs - 2.0 * INaK + IpK) * inverseVcF * CAPACITANCE;
    float Ki_new = Ki + dt * dKi;

    // Calcium Buffering and updates using quadratic solutions
    // CaSR
    float CaCSQN = (Bufsr * CaSR) / (CaSR + Kbufsr);
    float dCaSR_term = dt * (Iup - Irel - Ileak);
    float bjsr = Bufsr - CaCSQN - dCaSR_term - CaSR + Kbufsr;
    float cjsr = Kbufsr * (CaCSQN + dCaSR_term + CaSR);
    float CaSR_new = (sqrt(bjsr * bjsr + 4.0 * cjsr) - bjsr) / 2.0;

    // CaSS
    float CaSSBuf = (Bufss * CaSS) / (CaSS + Kbufss);
    float dCaSS_term = dt * (-Ixfer * (Vc / Vss) + Irel * (Vsr / Vss) - ICaL * inversevssF2 * CAPACITANCE);
    float bcss = Bufss - CaSSBuf - dCaSS_term - CaSS + Kbufss;
    float ccss = Kbufss * (CaSSBuf + dCaSS_term + CaSS);
    float CaSS_new = (sqrt(bcss * bcss + 4.0 * ccss) - bcss) / 2.0;

    // Cai
    float CaBuf = (Bufc * Cai) / (Cai + Kbufc);
    float dCai_term = dt * (-(IbCa + IpCa - 2.0 * INaCa) * inverseVcF2 * CAPACITANCE - (Iup - Ileak) * (Vsr / Vc) + Ixfer);
    float bc_ca = Bufc - CaBuf - dCai_term - Cai + Kbufc; // Renamed to avoid conflict with `in vec2 cc`
    float cc_ca = Kbufc * (CaBuf + dCai_term + Cai);
    float Cai_new = (sqrt(bc_ca * bc_ca + 4.0 * cc_ca) - bc_ca) / 2.0;

    // Sum Currents for Voltage PDE
    float ISumNaK = INa + IbNa + INaK + IK1 + IKr + IKs + IpK + Ito;
    float ISumCa = ICaL + IpCa + IbCa;

    // Voltage Update (PDE part)
    // Sample V from neighboring pixels for Laplacian
    float V_left = texture(inTexture1, cc - ii).r;
    float V_right = texture(inTexture1, cc + ii).r;
    float V_up = texture(inTexture1, cc - jj).r;
    float V_down = texture(inTexture1, cc + jj).r;

    float d2V_dx2 = (V_left + V_right - 2.0 * V) / (dx * dx);
    float d2V_dy2 = (V_up + V_down - 2.0 * V) / (dy * dy);
    float laplacian_V = d2V_dx2 + d2V_dy2;

    float dV_dt = diffCoef * laplacian_V - (ISumCa + ISumNaK + INaCa);
    float V_new = V + dV_dt * dt;

    // Output updated state variables to corresponding textures
    ocolor1 = vec4(V_new, sRR_new, Nai_new, Ki_new);
    ocolor2 = vec4(Cai_new, CaSS_new, CaSR_new, ISumCa);
    ocolor3 = vec4(sm, sh, sj, sxs);
    ocolor4 = vec4(sd, sf, sf2, sfcass);
    ocolor5 = vec4(sr, ss, sxr1, sxr2);
    return ;
}