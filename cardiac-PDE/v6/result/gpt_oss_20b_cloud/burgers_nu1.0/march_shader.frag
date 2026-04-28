precision highp float ;
precision highp int ;

uniform sampler2D   inTexture ;
uniform float       dt, dx, dy;

in vec2 cc, pixPos ;

layout (location = 0) out vec4 ocolor ;

#define u       color.r
const float nu = 1.0;

// Main body of the shader
void main() {
    vec4 color = texture( inTexture , cc ) ;
    vec2  size  = vec2(textureSize(inTexture, 0)) ;
    vec2 ii = vec2(1.,0.)/size ;
    vec2 jj = vec2(0.,1.)/size ;

    vec4 left  = texture( inTexture , fract(cc - ii) );
    vec4 right = texture( inTexture , fract(cc + ii) );

    float u_left  = left.r;
    float u_right = right.r;

    float conv = -0.5 * (u_right*u_right - u_left*u_left) / (2.0 * dx);
    float diff = nu / 3.14159265359 * (u_right - 2.0*u + u_left) / (dx * dx);

    float u_new = u + dt * (conv + diff);

    ocolor = vec4(u_new, 0.0, 0.0, 1.0);
    return ;
}