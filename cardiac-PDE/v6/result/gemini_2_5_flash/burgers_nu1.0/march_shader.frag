precision highp float ;
precision highp int ;

uniform sampler2D   inTexture ;
uniform float       dt, dx, dy;

in vec2 cc, pixPos ;

layout (location = 0) out vec4 ocolor ;

#define u       color.r
    const float nu = 1.0;
// your codes here for helper function

// your codes here for helper function

// Main body of the shader
void main() {
    vec2  size  = vec2(textureSize(inTexture, 0)) ;

    vec2 ii = vec2(1.,0.)/size ;
    // vec2 jj = vec2(0.,1.)/size ; // Not used for 1D PDE

    // read the color of the pixel at current position cc
    vec4 color = texture( inTexture , cc ) ;
    float u_i = u; // u at current position (u_i)

    // Read u values from neighbors using periodic boundary conditions
    // u_{i-1} from the left neighbor
    vec4 color_prev = texture(inTexture, fract(cc - ii));
    float u_prev = color_prev.r;

    // u_{i+1} from the right neighbor
    vec4 color_next = texture(inTexture, fract(cc + ii));
    float u_next = color_next.r;

    // Calculate the advection term: ∂_x (u^2 / 2)
    // Using central difference for ∂_x
    float F_u_prev = 0.5 * u_prev * u_prev; // F(u_{i-1}) = u_{i-1}^2 / 2
    float F_u_next = 0.5 * u_next * u_next; // F(u_{i+1}) = u_{i+1}^2 / 2
    float advection_term = (F_u_next - F_u_prev) / (2.0 * dx);

    // Calculate the diffusion term: ν / 3.1415926 * ∂_{xx} u
    // Using central difference for ∂_{xx}
    const float PI = 3.1415926;
    float diffusion_factor = nu / PI;
    float laplacian_u = (u_next - 2.0 * u_i + u_prev) / (dx * dx);
    float diffusion_term = diffusion_factor * laplacian_u;

    // Explicit Euler time integration:
    // u_new = u_i + dt * ( - ∂_x (u^2 / 2) + ν/π * ∂_{xx} u )
    float u_new = u_i - dt * advection_term + dt * diffusion_term;

    // Store the updated value in the output color's red channel
    ocolor = vec4(u_new, color.gba);
    return ;
}