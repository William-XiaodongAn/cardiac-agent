precision highp float ;
precision highp int ;

uniform sampler2D   inTexture ;
uniform float       dt, dx, dy;

in vec2 cc, pixPos ;

layout (location = 0) out vec4 ocolor ;

#define u       color.r
const float nu = 0.001;
const float PI = 3.1415926;

// helper function to fetch neighboring values with periodic boundaries
float getU(in vec2 offset) {
    return texture(inTexture, fract(cc + offset)).r;
}

void main() {
    vec2  size  = vec2(textureSize(inTexture, 0));
    vec2 ii = vec2(1.,0.)/size ;
    vec2 jj = vec2(0.,1.)/size ;

    vec4 color = texture( inTexture , cc );

    float u_cur  = getU(vec2(0.0));
    float u_prev = getU(-ii);
    float u_next = getU(+ii);

    float flux = (u_next*u_next - u_prev*u_prev) / (2.0*dx);
    float lap  = (u_next - 2.0*u_cur + u_prev) / (dx*dx);

    float u_new = u_cur + dt * ( -0.5*flux + (nu/PI)*lap );

    ocolor = vec4(u_new, color.g, color.b, color.a);
    return ;
}