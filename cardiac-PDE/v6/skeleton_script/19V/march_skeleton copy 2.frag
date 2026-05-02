precision highp float;
precision highp int;

uniform sampler2D inTexture1;
uniform sampler2D inTexture2;
uniform sampler2D inTexture3;
uniform sampler2D inTexture4;
uniform sampler2D inTexture5;
uniform float dt, dx, dy;

in vec2 cc, pixPos;
layout (location = 0) out vec4 ocolor1;
layout (location = 1) out vec4 ocolor2;
layout (location = 2) out vec4 ocolor3;
layout (location = 3) out vec4 ocolor4;
layout (location = 4) out vec4 ocolor5;

#define V color1.r
#define sm color1.g
#define sh color1.b
#define sj color1.a

#define sxs color2.r
#define sd color2.g
#define sf color2.b
#define sf2 color2.a

#define sfcass color3.r
#define sr color3.g
#define ss color3.b
#define sxr1 color3.a

#define sxr2 color4.r
#define Ki color4.g
#define Nai color4.b
#define Cai color4.a

#define CaSR color5.r
#define CaSS color5.g
#define sRR color5.b

void main() {
vec2 size = vec2(textureSize(inTexture1, 0));
vec2 ii = vec2(1.0, 0.0) / size;
vec2 jj = vec2(0.0, 1.0) / size;

vec4 color1 = texture(inTexture1, cc);
vec4 color2 = texture(inTexture2, cc);
vec4 color3 = texture(inTexture3, cc);
vec4 color4 = texture(inTexture4, cc);
vec4 color5 = texture(inTexture5, cc);

// Physical Constants
float Ko = 5.4;
float Cao = 2.0;
float Nao = 140.0;
float Vc = 0.016404;
float Vsr = 0.001094;
float Vss = 0.00005468;
float Bufc = 0.2;
float Kbufc = 0.001;
float Bufsr = 10.0;
float Kbufsr = 0.3;
float Bufss = 0.4;
float Kbufss = 0.00025;
float Vmaxup = 0.006375;
float Kup = 0.00025;
float Vrel = 0.102;
float k3 = 0.060;
float k4 = 0.005;
float k1prime = 0.15;
float k2prime = 0.045;
float EC = 1.5;
float maxsr = 2.5;
float minsr = 1.0;
float Vleak = 0.00036;
float Vxfer = 0.0038;
float RR = 8314.3;
float FF = 96486.7;
float TT = 310.0;
float CAPACITANCE = 0.185;
float Gks = 0.392;
float Gto = 0.294;
float Gkr = 0.153;
float pKNa = 0.03;
float GK1 = 5.405;
float alphanaca = 2.5;
float GNa = 14.838;
float GbNa = 0.00029;
float KmK = 1.0;
float KmNa = 40.0;
float knak = 2.724;
float GCaL = 0.00003980;
float GbCa = 0.000592;
float knaca = 1000.0;
float KmNai = 87.5;
float KmCa = 1.38;
float ksat = 0.1;
float n = 0.35;
float GpCa = 0.1238;
float KpCa = 0.0005;
float GpK = 0.0146;
float diffCoef = 0.00154;

// Derived Constants
float inverseVcF = 1.0 / (Vc * FF);
float inverseVcF2 = 1.0 / (2.0 * Vc * FF);
float inversevssF2 = 1.0 / (2.0 * Vss * FF);
float rtof = (RR * TT) / FF;
float fort = 1.0 / rtof;
float KmNai3 = pow(KmNai, 3.0);
float Nao3 = pow(Nao, 3.0);
float Gkrfactor = sqrt(Ko / 5.4);

// Gating - INa
float AM = 1.0 / (1.0 + exp((-60.0 - V) / 5.0));
float BM = 0.1 / (1.0 + exp((V + 35.0) / 5.0)) + 0.10 / (1.0 + exp((V - 50.0) / 200.0));
float tau_M = AM * BM;
float minft = 1.0 / pow(1.0 + exp((-56.86 - V) / 9.03), 2.0);
sm = minft - (minft - sm) * exp(-dt / tau_M);

float AH = (V >= -40.0) ? 0.0 : 0.057 * exp(-(V + 80.0) / 6.8);
float BH = (V >= -40.0) ? 0.77 / (0.13 * (1.0 + exp(-(V + 10.66) / 11.1))) : 2.7 * exp(0.079 * V) + 3.1e5 * exp(0.3485 * V);
float tau_H = 1.0 / (AH + BH);
float hinft = 1.0 / pow(1.0 + exp((V + 71.55) / 7.43), 2.0);
sh = hinft - (hinft - sh) * exp(-dt / tau_H);

float AJ = (V >= -40.0) ? 0.0 : ((-25428.0 * exp(0.2444 * V) - 6.948e-6 * exp(-0.04391 * V)) * (V + 37.78)) / (1.0 + exp(0.311 * (V + 79.23)));
float BJ = (V >= -40.0) ? (0.6 * exp(0.057 * V)) / (1.0 + exp(-0.1 * (V + 32.0))) : (0.02424 * exp(-0.01052 * V)) / (1.0 + exp(-0.1378 * (V + 40.14)));
float tau_J = 1.0 / (AJ + BJ);
sj = hinft - (hinft - sj) * exp(-dt / tau_J);

// Gating - IKs, ICaL
float xsinft = 1.0 / (1.0 + exp((-5.0 - V) / 14.0));
float tau_Xs = (1400.0 / sqrt(1.0 + exp((5.0 - V) / 6.0))) * (1.0 / (1.0 + exp((V - 35.0) / 15.0))) + 80.0;
sxs = xsinft - (xsinft - sxs) * exp(-dt / tau_Xs);

float dinft = 1.0 / (1.0 + exp((-8.0 - V) / 7.5));
float tau_D = (1.4 / (1.0 + exp((-35.0 - V) / 13.0)) + 0.25) * (1.4 / (1.0 + exp((V + 5.0) / 5.0))) + 1.0 / (1.0 + exp((50.0 - V) / 20.0));
sd = dinft - (dinft - sd) * exp(-dt / tau_D);

float finft = 1.0 / (1.0 + exp((V + 20.0) / 7.0));
float tau_F = 1102.5 * exp(-pow(V + 27.0, 2.0) / 225.0) + 200.0 / (1.0 + exp((13.0 - V) / 10.0)) + 180.0 / (1.0 + exp((V + 30.0) / 10.0)) + 20.0;
sf = finft - (finft - sf) * exp(-dt / tau_F);

float f2inft = 0.67 / (1.0 + exp((V + 35.0) / 7.0)) + 0.33;
float tau_F2 = 600.0 * exp(-pow(V + 25.0, 2.0) / 49.0) + 31.0 / (1.0 + exp((25.0 - V) / 10.0)) + 16.0 / (1.0 + exp((V + 30.0) / 10.0));
sf2 = f2inft - (f2inft - sf2) * exp(-dt / tau_F2);

float fcassinft = 0.6 / (1.0 + pow(CaSS / 0.05, 2.0)) + 0.4;
float tau_fcass = 80.0 / (1.0 + pow(CaSS / 0.05, 2.0)) + 2.0;
float FCaSS_INF = (CaSS >= 1.0) ? 0.4 : fcassinft;
float exptaufcass = (CaSS >= 1.0) ? exp(-dt / 2.0) : exp(-dt / tau_fcass);
sfcass = FCaSS_INF - (FCaSS_INF - sfcass) * exptaufcass;

// Gating - Ito, IKr
float rinft = 1.0 / (1.0 + exp((20.0 - V) / 6.0));
float sinft = 1.0 / (1.0 + exp((V + 20.0) / 5.0));
float tau_R = 9.5 * exp(-pow(V + 40.0, 2.0) / 1800.0) + 0.8;
float tau_S = 85.0 * exp(-pow(V + 45.0, 2.0) / 320.0) + 5.0 / (1.0 + exp((V - 20.0) / 5.0)) + 3.0;
sr = rinft - (rinft - sr) * exp(-dt / tau_R);
ss = sinft - (sinft - ss) * exp(-dt / tau_S);

float xr1inft = 1.0 / (1.0 + exp((-26.0 - V) / 7.0));
float tau_Xr1 = (450.0 / (1.0 + exp((-45.0 - V) / 10.0))) * (6.0 / (1.0 + exp((V + 30.0) / 11.5)));
sxr1 = xr1inft - (xr1inft - sxr1) * exp(-dt / tau_Xr1);

float xr2inft = 1.0 / (1.0 + exp((V + 88.0) / 24.0));
float tau_Xr2 = (3.0 / (1.0 + exp((-60.0 - V) / 20.0))) * (1.12 / (1.0 + exp((V - 60.0) / 20.0)));
sxr2 = xr2inft - (xr2inft - sxr2) * exp(-dt / tau_Xr2);

// Currents
float Ek = rtof * log(Ko / Ki);
float Ena = rtof * log(Nao / Nai);
float Eks = rtof * log((Ko + pKNa * Nao) / (Ki + pKNa * Nai));
float Eca = 0.5 * rtof * log(Cao / Cai);

float INa = GNa * pow(sm, 3.0) * sh * sj * (V - Ena);
float IKr = Gkr * Gkrfactor * sxr1 * sxr2 * (V - Ek);
float IKs = Gks * pow(sxs, 2.0) * (V - Eks);
float Ito = Gto * sr * ss * (V - Ek);

float vmek = V - Ek;
float Ak1 = 0.1 / (1.0 + exp(0.06 * (vmek - 200.0)));
float Bk1 = (3.0 * exp(0.0002 * (vmek + 100.0)) + exp(0.1 * (vmek - 10.0))) / (1.0 + exp(-0.5 * vmek));
float IK1 = (GK1 * Ak1 / (Ak1 + Bk1)) * vmek;

float IpK = (GpK / (1.0 + exp((25.0 - V) / 5.98))) * (V - Ek);
float IbNa = GbNa * (V - Ena);
float INaK = (knak / (1.0 + 0.1245 * exp(-0.1 * V * fort) + 0.0353 * exp(-V * fort))) * (Ko / (Ko + KmK)) * (Nai / (Nai + KmNa));

float temp_naca = exp((n - 1.0) * V * fort);
float temp2_naca = knaca / ((KmNai3 + Nao3) * (KmCa + Cao) * (1.0 + ksat * temp_naca));
float INaCa = temp2_naca * (exp(n * V * fort) * Cao * pow(Nai, 3.0) - temp_naca * Nao3 * alphanaca * Cai);

float dNai = -(INa + IbNa + 3.0 * INaK + 3.0 * INaCa) * inverseVcF * CAPACITANCE;
Nai += dt * dNai;
float dKi = -(IK1 + Ito + IKr + IKs - 2.0 * INaK + IpK) * inverseVcF * CAPACITANCE;
Ki += dt * dKi;

float temp_ical = exp(2.0 * (V - 15.0) * fort);
float ical1t, ical2t;
if (abs(V - 15.0) < 1.0e-4) {
    ical1t = GCaL * 4.0e-4 * (FF * fort) * (0.25 * exp(2.0e-4 * fort)) / (exp(2.0e-4 * fort) - 1.0);
    ical2t = GCaL * 4.0e-4 * (FF * fort) * Cao / (exp(2.0e-4 * fort) - 1.0);
} else {
    ical1t = GCaL * 4.0 * (V - 15.0) * (FF * fort) * (0.25 * temp_ical) / (temp_ical - 1.0);
    ical2t = GCaL * 4.0 * (V - 15.0) * (FF * fort) * Cao / (temp_ical - 1.0);
}
float ICaL = sd * sf * sf2 * sfcass * (ical1t * CaSS - ical2t);
float IpCa = (GpCa * Cai) / (KpCa + Cai);
float IbCa = GbCa * (V - Eca);

// Calcium Dynamics
float kCaSR = maxsr - (maxsr - minsr) / (1.0 + pow(EC / CaSR, 2.0));
float k1 = k1prime / kCaSR;
float k2 = k2prime * kCaSR;
float dRR = k4 * (1.0 - sRR) - k2 * CaSS * sRR;
sRR += dt * dRR;
float sOO = (k1 * pow(CaSS, 2.0) * sRR) / (k3 + k1 * pow(CaSS, 2.0));
float Irel = Vrel * sOO * (CaSR - CaSS);
float Ileak = Vleak * (CaSR - Cai);
float Iup = Vmaxup / (1.0 + pow(Kup / Cai, 2.0));
float Ixfer = Vxfer * (CaSS - Cai);

float CaCSQN = (Bufsr * CaSR) / (CaSR + Kbufsr);
float dCaSR_raw = (Iup - Irel - Ileak);
float bjsr = Bufsr - CaCSQN - dt * dCaSR_raw - CaSR + Kbufsr;
float cjsr = Kbufsr * (CaCSQN + dt * dCaSR_raw + CaSR);
CaSR = (sqrt(bjsr * bjsr + 4.0 * cjsr) - bjsr) / 2.0;

float CaSSBuf = (Bufss * CaSS) / (CaSS + Kbufss);
float dCaSS_raw = (-Ixfer * (Vc / Vss) + Irel * (Vsr / Vss) - ICaL * inversevssF2 * CAPACITANCE);
float bcss = Bufss - CaSSBuf - dt * dCaSS_raw - CaSS + Kbufss;
float ccss = Kbufss * (CaSSBuf + dt * dCaSS_raw + CaSS);
CaSS = (sqrt(bcss * bcss + 4.0 * ccss) - bcss) / 2.0;

float CaBuf = (Bufc * Cai) / (Cai + Kbufc);
float dCai_raw = (-(IbCa + IpCa - 2.0 * INaCa) * inverseVcF2 * CAPACITANCE - (Iup - Ileak) * (Vsr / Vc) + Ixfer);
float bc = Bufc - CaBuf - dt * dCai_raw - Cai + Kbufc;
float cc_val = Kbufc * (CaBuf + dt * dCai_raw + Cai);
Cai = (sqrt(bc * bc + 4.0 * cc_val) - bc) / 2.0;

// PDE: Voltage Diffusion (Neumann BC)
vec2 pX = cc - ii; if(pX.x < 0.0) pX = cc + ii;
vec2 nX = cc + ii; if(nX.x > 1.0) nX = cc - ii;
vec2 pY = cc - jj; if(pY.y < 0.0) pY = cc + jj;
vec2 nY = cc + jj; if(nY.y > 1.0) nY = cc - jj;

// Corner points for 9-point stencil
vec2 pXpY = pX - jj; if(pXpY.y < 0.0) pXpY = pX + jj;
vec2 pXnY = pX + jj; if(pXnY.y > 1.0) pXnY = pX - jj;
vec2 nXpY = nX - jj; if(nXpY.y < 0.0) nXpY = nX + jj;
vec2 nXnY = nX + jj; if(nXnY.y > 1.0) nXnY = nX - jj;

float vL = texture(inTexture1, pX).r;
float vR = texture(inTexture1, nX).r;
float vU = texture(inTexture1, nY).r;
float vD = texture(inTexture1, pY).r;

float vLU = texture(inTexture1, pXpY).r;
float vLD = texture(inTexture1, pXnY).r;
float vRU = texture(inTexture1, nXpY).r;
float vRD = texture(inTexture1, nXnY).r;

float cddx = 1.0 / (dx * dx);
float cddy = 1.0 / (dy * dy);
float gamma = 1.0 / 3.0;

float dVlt2dt = (1.0 - gamma) * ((vR - 2.0 * V + vL) * cddx + (vU - 2.0 * V + vD) * cddy)
              + gamma * 0.5 * (vRU + vRD + vLU + vLD - 4.0 * V) * (cddx + cddy);

float I_sum = INa + IbNa + INaK + IK1 + IKr + IKs + IpK + Ito + ICaL + IpCa + IbCa + INaCa;
V += dt * (dVlt2dt * diffCoef - I_sum);

ocolor1 = vec4(V, sm, sh, sj);
ocolor2 = vec4(sxs, sd, sf, sf2);
ocolor3 = vec4(sfcass, sr, ss, sxr1);
ocolor4 = vec4(sxr2, Ki, Nai, Cai);
ocolor5 = vec4(CaSR, CaSS, sRR, 1.0);}