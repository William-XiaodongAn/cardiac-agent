precision highp float ;
precision highp int ;

uniform sampler2D   inTexture ;
uniform float       dt, dx, dy;

in vec2 cc, pixPos ;

layout (location = 0) out vec4 ocolor ;

#define u       color.r
    const float nu = 0.001;
// your codes here for helper function
float f_u(float val_u) {
    return val_u * val_u / 2.0;
}
// your codes here for helper function

// Main body of the shader
void main() {
    vec2  size  = vec2(textureSize(inTexture, 0)) ;

    vec2 ii = vec2(1.,0.)/size ;
    // vec2 jj = vec2(0.,1.)/size ; // Not used for 1D PDE

    // read the color of the pixel
    vec4 color = texture( inTexture , cc ) ;

    // use fract for periodic condition
    vec2 prevX_coord = fract(cc - ii);
    vec2 nextX_coord = fract(cc + ii);
    // your codes here (do not define helper function)
    float u_c = u; // u at current pixel (i)

    // Read neighboring values
    vec4 color_prevX = texture( inTexture , prevX_coord ) ;
    float u_pX = color_prevX.r; // u at previous pixel (i-1)

    vec4 color_nextX = texture( inTexture , nextX_coord ) ;
    float u_nX = color_nextX.r; // u at next pixel (i+1)

    // Calculate the advection term: -d(u^2/2)/dx
    // Using central difference for d(f(u))/dx
    float df_dx = (f_u(u_nX) - f_u(u_pX)) / (2.0 * dx);

    // Calculate the diffusion term: (nu/pi) * d^2u/dx^2
    // Using central difference for d^2u/dx^2
    const float PI_INV = 1.0 / 3.1415926; // Precompute 1/pi
    float d2u_dx2 = (u_nX - 2.0 * u_c + u_pX) / (dx * dx);
    float diffusion_term = (nu * PI_INV) * d2u_dx2;
    // your codes here (do not define helper function)

    // Update u using explicit Euler time integration
    float u_new = u_c + dt * (-df_dx + diffusion_term);

    // Assign the new value to the output color's red channel
    // Keep green and blue channels as they were, assuming they are not used for u
    ocolor = vec4(u_new, color.g, color.b, color.a) ;
    return ;
}