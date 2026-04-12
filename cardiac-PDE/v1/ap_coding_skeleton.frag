#version 300 es
precision highp float;
precision highp int;

uniform sampler2D   inTexture;
uniform float       dt, D, dx, dy;

in vec2 cc, pixPos;

layout (location = 0) out vec4 ocolor;

// State variables packed into texture channels:
//   R = u  (transmembrane potential, normalized ~0..1)
//   G = v  (recovery variable)
//   B = unused (set to 0)
#define u   color.r
#define v   color.g

// Aliev-Panfilov model parameters
const float a     = 0.1;    // excitation threshold
const float k     = 8.0;    // scaling factor for reaction term
const float eps_0 = 0.01;   // base recovery rate
const float mu1   = 0.07;   // recovery coupling (numerator)
const float mu2   = 0.3;    // recovery coupling (denominator)

// your codes here for helper functions (e.g. eps(u,v))

void main() {
    vec2 size = vec2(textureSize(inTexture, 0));
    vec2 ii = vec2(1., 0.) / size;
    vec2 jj = vec2(0., 1.) / size;

    // Read current state
    vec4 color = texture(inTexture, cc);

    // ----------------------------------------------------------------
    // Neumann (no-flux) boundary: clamp coordinates so edge pixels
    // read from their nearest interior neighbour, giving zero gradient.
    // ----------------------------------------------------------------
    vec2 cc_px = cc * size;                         // pixel coords
    vec2 cc_l  = max(cc_px - vec2(1., 0.), vec2(0.)) / size;
    vec2 cc_r  = min(cc_px + vec2(1., 0.), size - 1.) / size;
    vec2 cc_d  = max(cc_px - vec2(0., 1.), vec2(0.)) / size;
    vec2 cc_u2 = min(cc_px + vec2(0., 1.), size - 1.) / size;

    // 4-point Laplacian with Neumann BCs
    float laplacian = (
        texture(inTexture, cc_r ).r +
        texture(inTexture, cc_l ).r +
        texture(inTexture, cc_u2).r +
        texture(inTexture, cc_d ).r -
        4.0 * u
    ) / (dx * dx);

    // du/dt = D*∇²u + reaction_u
    float dudt = D * laplacian;

    // your codes here — reaction term for u:
    //   f(u,v) = -k*u*(u-a)*(u-1) - u*v
    // your codes here — eps(u,v) and dv/dt:
    //   eps(u,v) = eps_0 + mu1*v/(mu2+u)
    //   g(u,v)   = eps(u,v)*(-v - k*u*(u-a-1))

    // your codes here — Euler update for u and v

    ocolor = vec4(u, v, 0.0, 1.0);
    return;
}
