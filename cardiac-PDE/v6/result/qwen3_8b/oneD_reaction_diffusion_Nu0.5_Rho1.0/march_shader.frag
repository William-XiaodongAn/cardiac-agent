precision highp float;
precision highp int;

uniform sampler2D   inTexture ;
uniform float       dt, dx, dy;

in vec2 cc, pixPos ;

layout (location = 0) out vec4 ocolor ;

#define u       color.r
const float nu = 0.5;
const float rho = 1.0;

void main() {
    vec2 size = textureSize(inTexture, 0);
    vec2 ii = vec2(1.0, 0.0) / size;
    vec2 jj = vec2(0.0, 1.0) / size;

    vec4 color = texture(inTexture, cc);

    // Compute neighbors for x-direction
    vec2 left_x = fract(cc - ii);
    vec2 right_x = fract(cc + ii);

    // Compute neighbors for y-direction
    vec2 left_y = fract(cc - jj);
    vec2 right_y = fract(cc + jj);

    // Sample the neighbors
    vec4 u_left_x = texture(inTexture, vec2(left_x.x, cc.y));
    vec4 u_right_x = texture(inTexture, vec2(right_x.x, cc.y));
    vec4 u_left_y = texture(inTexture, vec2(cc.x, left_y.y));
    vec4 u_right_y = texture(inTexture, vec2(cc.x, right_y.y));

    // Compute second derivatives
    float dx2 = (u_right_x.r + u_left_x.r - 2.0 * color.r) / (dx * dx);
    float dy2 = (u_right_y.r + u_left_y.r - 2.0 * color.r) / (dy * dy);

    float laplacian = dx2 + dy2;

    // Compute new u
    float new_u = color.r + dt * (nu * laplacian + rho * color.r * (1.0 - color.r));

    ocolor = vec4(new_u, 0.0, 0.0, 1.0);
}