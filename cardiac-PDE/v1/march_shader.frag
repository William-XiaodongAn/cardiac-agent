precision highp float;
precision highp int;

uniform sampler2D   inTexture ;
uniform float       dt, D, dx, dy;

in vec2 cc, pixPos ;

layout (location = 0) out vec4 ocolor ;

#define u       color.r
#define v       color.g
#define w       color.b

const float tau_pv = 7.99;
const float tau_v1 = 9.8;
const float tau_v2 = 312.5;
const float tau_pw = 870.0;
const float tau_mw = 41.0;
const float tau_d  = 0.5714;
const float tau_0  = 12.5;
const float tau_r  = 33.83;
const float tau_si = 29.0;
const float K      = 10.0;
const float V_csi  = 0.861;
const float V_c = 0.13; 
const float V_v = 0.04;
const float C_m    = 1.0;

void main() {
    vec2  size  = vec2(textureSize(inTexture, 0)) ;

    vec2 ii = vec2(1.,0.)/size ;
    vec2 jj = vec2(0.,1.)/size ;

    // read the color of the pixel
    vec4 color = texture( inTexture , cc ) ;

    // Standard Laplacian calculation
    float laplacian = (
        texture(inTexture, cc + ii).r + 
        texture(inTexture, cc - ii).r + 
        texture(inTexture, cc + jj).r + 
        texture(inTexture, cc - jj).r - 
        4.0 * u
    ) / (dx*dx) ;

    float dudt = D*laplacian ;

    // Compute current terms for u
    float H_u = step(V_c, u);

    float term1 = -v * H_u * (u - V_c) * (1.0 - u) / tau_d;
    float term2 = (u * (1.0 - H_u)) / tau_0 + (H_u) / tau_r;
    float term3 = -w * (1.0 + tanh(K * (u - V_csi))) / (2.0 * tau_si);

    float current = (term1 + term2 + term3) / C_m;

    dudt = D * laplacian - current;

    // Compute dv/dt
    float dvdt = (1.0 - v) * (1.0 - H_u) / tau_v1 + (-v) * H_u / tau_pv;

    // Compute dw/dt
    float dwdt = (1.0 - w) * (1.0 - H_u) / tau_mw + (-w) * H_u / tau_pw;

    // Update the color
    ocolor.r = u + dudt * dt;
    ocolor.g = v + dvdt * dt;
    ocolor.b = w + dwdt * dt;
}