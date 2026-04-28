precision highp float;
precision highp int;

uniform sampler2D inTexture;
uniform float dt, dx, dy;

in vec2 cc, pixPos;
layout (location = 0) out vec4 ocolor;

#define u color.r
const float nu = 1.0;

void main() {
    vec2 size = vec2(textureSize(inTexture, 0));
    vec2 ii = vec2(1.0, 0.0) / size;
    vec2 jj = vec2(0.0, 1.0) / size;

    vec4 color = texture(inTexture, cc);

    vec2 prev = fract(cc - ii);
    vec2 next = fract(cc + ii);

    vec4 colPrev = texture(inTexture, prev);
    vec4 colNext = texture(inTexture, next);
    float u_prev = colPrev.r;
    float u_curr = color.r;
    float u_next = colNext.r;

    float f_prev = 0.5 * u_prev * u_prev;
    float f_next = 0.5 * u_next * u_next;

    float conv = (f_next - f_prev) / dx;
    float diff = (u_next - 2.0 * u_curr + u_prev) / (dx * dx);

    float u_new = u_curr + dt * (-conv + nu * diff);

    ocolor = vec4(u_new, 0.0, 0.0, 1.0);
}