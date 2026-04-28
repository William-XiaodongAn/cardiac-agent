precision highp float;
precision highp int;

uniform sampler2D   inTexture ;
uniform float       dt, dx, dy;

in vec2 cc, pixPos ;

layout (location = 0) out vec4 ocolor ;

#define u       color.r
const float beta = 0.1;

void main() {
    vec2 size = vec2(textureSize(inTexture, 0));
    vec2 ii = vec2(1.0, 0.0) / size;   // step in x
    vec2 jj = vec2(0.0, 1.0) / size;   // step in y

    vec4 color = texture(inTexture, cc);

    // use periodic boundary conditions: upwind difference
    vec2 prevX = fract(cc - ii);
    vec4 prevColor = texture(inTexture, prevX);

    float du_dx = (color.r - prevColor.r) / dx;
    float u_new  = color.r - dt * beta * du_dx;

    ocolor = vec4(u_new, color.g, color.b, color.a);
    return;
}