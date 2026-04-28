precision highp float ;
precision highp int ;

uniform sampler2D   inTexture ;
uniform float       dt, dx, dy;

in vec2 cc, pixPos ;

layout (location = 0) out vec4 ocolor ;

#define u       color.r
#define v       color.g

const float D_u = 0.001;
const float D_v = 0.005;
const float k   = 0.005;

void main() {
    vec2 size = vec2(textureSize(inTexture, 0));
    vec2 ii = vec2(1.,0.)/size;
    vec2 jj = vec2(0.,1.)/size;

    vec4 color = texture(inTexture , cc);
    float u_val = color.r;
    float v_val = color.g;

    // Neumann (no-flux) boundary: clamp coordinates
    vec2 ccL = clamp(cc - ii, 0.0, 1.0);
    vec2 ccR = clamp(cc + ii, 0.0, 1.0);
    vec2 ccD = clamp(cc - jj, 0.0, 1.0);
    vec2 ccU = clamp(cc + jj, 0.0, 1.0);

    // Sample neighbors for u
    float uL = texture(inTexture, ccL).r;
    float uR = texture(inTexture, ccR).r;
    float uD = texture(inTexture, ccD).r;
    float uU = texture(inTexture, ccU).r;

    // Sample neighbors for v
    float vL = texture(inTexture, ccL).g;
    float vR = texture(inTexture, ccR).g;
    float vD = texture(inTexture, ccD).g;
    float vU = texture(inTexture, ccU).g;

    // Laplacian
    float lapU = (uL - 2.0*u_val + uR)/(dx*dx) + (uD - 2.0*u_val + uU)/(dy*dy);
    float lapV = (vL - 2.0*v_val + vR)/(dx*dx) + (vD - 2.0*v_val + vU)/(dy*dy);

    // Time derivatives
    float du = D_u * lapU + u_val - u_val*u_val*u_val - k - v_val;
    float dv = D_v * lapV + u_val - v_val;

    // Euler update
    float u_new = u_val + dt * du;
    float v_new = v_val + dt * dv;

    ocolor = vec4(u_new, v_new, 0.0, 1.0);
    return;
}