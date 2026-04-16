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

    // compute left neighbor position
    vec2 leftPos = fract( cc - vec2( ii.x, 0.0 ) );
    vec4 leftColor = texture( inTexture, leftPos );
    float u_left = leftColor.r;

    // compute new_u
    float new_u = color.r - beta * (color.r - u_left) * dt / dx;

    ocolor = vec4( new_u, 0., 0., 0. );
    return ;
}