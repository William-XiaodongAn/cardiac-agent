precision highp float;
precision highp int;

uniform sampler2D   inTexture ;
uniform float       dt, dx, dy;

in vec2 cc, pixPos ;

layout (location = 0) out vec4 ocolor ;

#define u       color.r
const float nu = 1.0;

void main() {
    vec2 size = vec2(textureSize(inTexture, 0));
    vec2 ii = vec2(1.0, 0.0) / size;
    vec2 jj = vec2(0.0, 1.0) / size;

    vec2 left_pos = vec2(fract(cc.x - dx), 0.0);
    vec2 right_pos = vec2(fract(cc.x + dx), 0.0);

    vec4 color = texture(inTexture, cc);
    float u = color.r;

    vec4 u_left = texture(inTexture, left_pos);
    vec4 u_right = texture(inTexture, right_pos);

    float d2u = (u_right.r - 2.0 * u + u_left.r) / (dx * dx);
    float d1u = (u_right.r - u_left.r) / (2.0 * dx);
    float adv_term = u * d1u;

    float rhs = (1.0 / 3.1415926) * d2u - adv_term;

    float new_u = u + dt * rhs;

    ocolor = vec4(new_u, 0.0, 0.0, 1.0);
}