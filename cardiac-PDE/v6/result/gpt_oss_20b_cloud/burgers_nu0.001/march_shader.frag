precision highp float ;
precision highp int ;

uniform sampler2D   inTexture ;
uniform float       dt, dx, dy;

in vec2 cc, pixPos ;

layout (location = 0) out vec4 ocolor ;

#define u       color.r
const float nu = 0.001;

void main() {
    vec2  size  = vec2(textureSize(inTexture, 0)) ;
    vec2 ii = vec2(1.0,0.0)/size ;
    vec2 jj = vec2(0.0,1.0)/size ;

    // read the current value
    vec4 color = texture( inTexture , cc ) ;
    float u_cur = color.r ;

    // periodic neighbours using fract
    vec2 prevX = fract(cc - ii);
    vec2 nextX = fract(cc + ii);

    float u_prev = texture(inTexture, prevX).r ;
    float u_next = texture(inTexture, nextX).r ;

    // convective derivative ∂_x(u^2/2)
    float conv = (u_next*u_next - u_prev*u_prev) / (2.0*dx) ;

    // viscous term ν ∂_{xx} u
    float visc = nu * (u_next - 2.0*u_cur + u_prev) / (dx*dx) ;

    // update
    float u_new = u_cur - dt * conv + dt * visc ;

    ocolor = vec4(u_new, 0.0, 0.0, 1.0) ;
    return ;
}