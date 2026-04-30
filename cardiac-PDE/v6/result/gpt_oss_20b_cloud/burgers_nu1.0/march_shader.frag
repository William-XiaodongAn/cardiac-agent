precision highp float ;
precision highp int ;

uniform sampler2D   inTexture ;
uniform float       dt, dx, dy;

in vec2 cc, pixPos ;

layout (location = 0) out vec4 ocolor ;

#define u       color.r
const float nu = 1.0;

// helper function for periodic sampling
float getUOffset( vec2 offset )
{
    return texture( inTexture , fract( cc + offset ) ).r ;
}

void main() {
    vec2  size  = vec2( textureSize( inTexture, 0 ) ) ;

    vec2 ii = vec2(1.,0.) / size ;
    vec2 jj = vec2(0.,1.) / size ;

    // read the color of the pixel
    vec4 color = texture( inTexture , cc ) ;

    // periodic BC in x direction
    float u_left  = getUOffset( -ii ) ;
    float u_right = getUOffset(  ii ) ;
    float u_self  = color.r ;

    // advection term ∂x(u²/2) ≈ (u_right² - u_left²)/(4*dx)
    float adv_term = ( u_right*u_right - u_left*u_left ) / (4.0*dx) ;

    // diffusion term (nu/pi)*∂²u/∂x² ≈ (nu/pi)*(u_left - 2*u_self + u_right)/dx²
    float diff_term = ( ( nu / 3.1415926 ) *
                         ( u_left - 2.0*u_self + u_right ) ) / (dx*dx) ;

    // update equation u_new = u_self - dt*adv_term + dt*diff_term
    float u_new = u_self + dt * ( diff_term - adv_term ) ;

    ocolor = vec4( u_new, color.g, color.b, color.a ) ;
    return ;
}
