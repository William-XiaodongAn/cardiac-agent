precision highp float;
precision highp int;

uniform sampler2D   inTexture ;
uniform float       dt, dx, dy;

in vec2 cc, pixPos ;

layout (location = 0) out vec4 ocolor ;

#define u       color.r
const float beta = 0.1;

void main() {
    vec2  size  = vec2(textureSize(inTexture, 0)) ;

    vec2 ii = vec2(1.,0.)/size ;
    vec2 jj = vec2(0.,1.)/size ;

    // read the color of the pixel
    vec4 color = texture( inTexture , cc ) ;

    // compute the right neighbor position
    vec2 rightPos = fract( cc + ii );
    vec4 u_right = texture( inTexture, rightPos );

    // compute spatial derivative
    float du_dx = (u_right.r - color.r) / dx;

    // compute delta_u
    float delta_u = -beta * dt * du_dx;

    // update the color
    vec4 new_color = color;
    new_color.r = color.r + delta_u;

    ocolor = new_color;
}