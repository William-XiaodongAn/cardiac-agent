precision highp float;
precision highp int;

uniform sampler2D   inTexture ;
uniform float       dt, dx, dy;

in vec2 cc, pixPos ;

layout (location = 0) out vec4 ocolor ;

#define u       color.r
#define v       color.g
#define w       color.b

const float D = 0.001;
const float C_m = 1.0;
const float tau_pv = 7.99;
const float tau_v1 = 9.8;
const float tau_v2 = 312.5;
const float tau_pw = 870.0;
const float tau_mw = 41.0;
const float tau_0 = 12.5;
const float tau_r = 33.83;
const float tau_si = 29.0;
const float k = 10.0;
const float V_csi = 0.861;
const float V_c = 0.13;
const float V_v = 0.04;
const float tau_d = 0.5714;

// Helper functions
float H(float x) {
    return x >= 0.0 ? 1.0 : 0.0;
}

float tau_mv_func(float u_val) {
    return u_val < V_v ? tau_v1 : tau_v2;
}

float I_fi_func(float u_val, float v_val) {
    return -v_val * H(u_val - V_c) * (u_val - V_c) * (1.0 - u_val) / tau_d;
}

float I_so_func(float u_val) {
    return (u_val * (1.0 - H(u_val - V_c))) / tau_0 + (H(u_val - V_c)) / tau_r;
}

float I_si_func(float u_val, float w_val) {
    return -w_val * (1.0 + tanh(k * (u_val - V_csi))) / (2.0 * tau_si);
}

void main() {
    vec2 size = vec2(textureSize(inTexture, 0));
    vec2 ix = vec2(1.0, 0.0) / size;
    vec2 iy = vec2(0.0, 1.0) / size;

    vec4 color = texture(inTexture, cc);

    // Neumann (zero-flux) boundary: use clamped coordinates
    vec4 up   = texture(inTexture, clamp(cc + iy, vec2(0.0), vec2(1.0)));
    vec4 down = texture(inTexture, clamp(cc - iy, vec2(0.0), vec2(1.0)));
    vec4 left = texture(inTexture, clamp(cc - ix, vec2(0.0), vec2(1.0)));
    vec4 right= texture(inTexture, clamp(cc + ix, vec2(0.0), vec2(1.0)));

    // Laplacian
    float lap = ((left.r + right.r - 2.0*u) / (dx * dx)) +
                ((up.r   + down.r - 2.0*u) / (dy * dy));

    // Currents
    float I_fi = I_fi_func(u, v);
    float I_so = I_so_func(u);
    float I_si = I_si_func(u, w);

    // Time derivatives
    float du_dt = D * lap - (I_fi + I_so + I_si) / C_m;

    float tau_mv = tau_mv_func(u);
    float dv_dt = (u < V_c) ? (1.0 - v) / tau_mv : (-v) / tau_pv;

    float dw_dt = (u < V_c) ? (1.0 - w) / tau_mw : (-w) / tau_pw;

    // Euler integration
    float u_new = u + dt * du_dt;
    float v_new = v + dt * dv_dt;
    float w_new = w + dt * dw_dt;

    ocolor = vec4(u_new, v_new, w_new, 1.0);
    return;
}