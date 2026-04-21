precision highp float;
precision highp int;

uniform sampler2D inTexture;
uniform float dt, dx, dy;
uniform float D_u, D_v, k;

in vec2 cc, pixPos;

layout (location = 0) out vec4 ocolor;

#define u       color.r
#define v       color.g

void main() {
    vec2 size = textureSize(inTexture, 0);
    vec2 ii = vec2(1.,0.)/size;
    vec2 jj = vec2(0.,1.)/size;

    vec4 color = texture(inTexture, cc);
    float u_old = color.r;
    float v_old = color.g;

    float laplacian_u = 0.0;
    float u_right = texture(inTexture, cc + ii).r;
    float u_left = texture(inTexture, cc - ii).r;
    laplacian_u += (u_right + u_left - 2.0 * u_old) / (dx*dx);

    float u_top = texture(inTexture, cc - jj).r;
    float u_bottom = texture(inTexture, cc + jj).r;
    laplacian_u += (u_top + u_bottom - 2.0 * u_old) / (dy*dy);

    float laplacian_v = 0.0;
    float v_right = texture(inTexture, cc + ii).g;
    float v_left = texture(inTexture, cc - ii).g;
    laplacian_v += (v_right + v_left - 2.0 * v_old) / (dx*dx);

    float v_top = texture(inTexture, cc - jj).g;
    float v_bottom = texture(inTexture, cc + jj).g;
    laplacian_v += (v_top + v_bottom - 2.0 * v_old) / (dy*dy);

    float rhs_u = D_u * laplacian_u + u_old - u_old*u_old*u_old - k - v_old;
    float rhs_v = D_v * laplacian_v + u_old - v_old;

    float u_new = u_old + dt * rhs_u;
    float v_new = v_old + dt * rhs_v;

    ocolor.r = u_new;
    ocolor.g = v_new;
}