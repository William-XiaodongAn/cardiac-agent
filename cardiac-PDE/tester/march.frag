#version 300 es
precision highp float ;
precision highp int ;

uniform sampler2D   inTexture ;
uniform float       dt, diffCoef, currtime, dx, dy,Temp;

in vec2 cc, pixPos ;

layout (location = 0) out vec4 ocolor ;

#define u       color.r
#define v       color.g
#define w       color.b

// Main body of the shader
void main() {
    vec2  size  = vec2(textureSize(inTexture, 0)) ;

    vec2 ii = vec2(1.,0.)/size ;
    vec2 jj = vec2(0.,1.)/size ;

    // read the color of the pixel .......................................
    vec4 color = texture( inTexture , cc ) ;

    // Standard Laplacian calculation (Replaces the LR/UD/E-field map logic)
    float laplacian = (
        texture(inTexture, cc + ii).r + 
        texture(inTexture, cc - ii).r + 
        texture(inTexture, cc + jj).r + 
        texture(inTexture, cc - jj).r - 
        4.0 * u
    ) / (dx*dx) ;

    float dudt = diffCoef*laplacian ;

    // Original 3V Model Constants and Logic ---------------------------
    float tau_pv=7.99;
    float tau_v1=9.8;
    float tau_v2=312.5;
    float tau_pw=870.0;
    float tau_mw=41.0;
    float tau_d=0.5714;
    float tau_0=12.5;
    float tau_r=33.83;
    float tau_si=29.0;
    float K=10.0;
    float V_csi=0.861;
    float V_c=0.13;
    float V_v=0.04;
    float C_m=1.0;

    float T0=37.0;
    float q10v=1.5;
    float q10w=2.45;
    float betafi=0.065;
    float betaso=0.008;
    float betasi=0.008;
    float phiv = pow(q10v,(Temp-T0)/10.0);
    float phiw = pow(q10w,(Temp-T0)/10.0);
    float etafi = 1.0+betafi*(Temp-T0);
    float etaso = 1.0+betaso*(Temp-T0);
    float etasi = 1.0+betasi*(Temp-T0);

    float p = step(V_c, u) ;
    float q = step(V_v, u) ;

    float tau_mv = (1.0-q)*tau_v1   +  q*tau_v2 ;
    float tn = tanh(K*(u-V_csi));

    //Rush-Larsen for gating variables
    v = (1.0-p)*(1.0-(1.0-v)*exp(-phiv*dt/tau_mv)) + p*v*exp(-phiv*dt/tau_pv);
    w = (1.0-p)*(1.0-(1.0-w)*exp(-phiw*dt/tau_mw)) + p*w*exp(-phiw*dt/tau_pw);

    float Ifi  = etafi*(-v*p*(u - V_c)*(1.0-u)/tau_d) ;
    float Iso  = etaso*(u*(1.0  - p )/tau_0 + p/tau_r) ;
    float Isi  = etasi*(-w*(1.0  + tn) /(2.0*tau_si)) ;

    dudt  -= (Ifi+Iso+Isi)/C_m ;

    u += dt*dudt;

    ocolor = color ;
    return ;
}