
precision highp float;
precision highp int;

uniform sampler2D   inTexture;
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


// Helper function for Heaviside step function
float H(float x) {
    return step(x, 0.0);
}

// Helper function to calculate the derivative of u with respect to time
void dudt_laplacian() {
    vec2 ii = vec2(1., 0.) / size;
    vec2 jj = vec2(0., 1.) / size;

    // Read the color of the pixel
    vec4 color = texture(inTexture, cc);

    // Standard Laplacian calculation
    float laplacian = (
        texture(inTexture, cc + ii).r +
        texture(inTexture, cc - ii).r +
        texture(inTexture, cc + jj).r +
        texture(inTexture, cc - jj).r -
        4.0 * u
    ) / (dx*dx);

    dudt = D * laplacian;
}

// Helper function to calculate the derivative of v with respect to time
void dudt_v() {
    float v1 = tau_v1 * pow(1. - v, tau_v2);
    float v2 = tau_v2 * pow(v, tau_v2);
    
    float I_fi = -v * H(u - V_c) * (u - V_c) * (1.0 - u) / tau_d;
    float I_so = u * (1.0 - H(u - V_c)) / tau_0 + H(u - V_c) / tau_r;

    dudt = v1 + v2 + I_fi + I_so;
}

// Helper function to calculate the derivative of w with respect to time
void dudt_w() {
    float w1 = tau_mw * pow(1.0 - w, tau_mw);
    float w2 = tau_pw * pow(w, tau_mw);

    float I_si = -w * (1.0 + tanh(K * (u - V_csi))) / (2.0 * tau_si);

    dudt = w1 + w2 + I_si;
}

// Main body of the shader
void main() {
    vec2  size  = vec2(textureSize(inTexture, 0));
    
    // Calculate the derivative of u with respect to time using Laplacian
    dudt_laplacian();

    // Calculate the derivative of v with respect to time
    dudt_v();

    // Calculate the derivative of w with respect to time
    dudt_w();

    ocolor = vec4(u, v, w, 1.0);
}
```

This code implements a simple finite difference solver for a system of partial differential equations (PDEs) using WebGL shaders. The PDEs include advection-diffusion equations for `u`, `v`, and `w`, along with reaction terms based on Heaviside step functions and other conditions.