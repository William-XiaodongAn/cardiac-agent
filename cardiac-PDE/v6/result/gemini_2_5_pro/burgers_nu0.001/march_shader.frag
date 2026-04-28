
precision highp float ;
precision highp int ;

uniform sampler2D   inTexture ;
uniform float       dt, dx, dy;

in vec2 cc, pixPos ;

layout (location = 0) out vec4 ocolor ;

#define u       color.r
    const float nu = 0.001;
// Helper function to calculate the convective term d/dx(u^2/2)
// This is approximated using a second-order central difference scheme for the flux F(u) = u^2/2.
// This term models the non-linear wave propagation (advection) behavior of the fluid.
float convectiveTerm(float u_plus, float u_minus) {
    // Calculate the flux at the right (i+1) and left (i-1) neighbor points
    float flux_plus  = 0.5 * u_plus * u_plus;
    float flux_minus = 0.5 * u_minus * u_minus;
    
    // Approximate the derivative dF/dx as (F_{i+1} - F_{i-1}) / (2 * dx)
    return (flux_plus - flux_minus) / (2.0 * dx);
}

// Helper function to calculate the viscous (diffusion) term nu * d^2u/dx^2
// This is approximated using a second-order central difference for the second derivative.
// This term models the dissipation of energy, smoothing out sharp gradients and preventing shock formation.
float viscousTerm(float u_plus, float u_current, float u_minus) {
    // Approximate d^2u/dx^2 as (u_{i+1} - 2*u_i + u_{i-1}) / dx^2
    float d2u_dx2 = (u_plus - 2.0 * u_current + u_minus) / (dx * dx);
    
    // Return the full viscous term
    return nu * d2u_dx2;
}

// Main body of the shader
void main() {
    vec2  size  = vec2(textureSize(inTexture, 0)) ;

    // Define the step vector for one pixel in the x-direction in texture coordinates.
    // This represents the spatial discretization step.
    vec2 ii = vec2(1.,0.)/size ;
    vec2 jj = vec2(0.,1.)/size ;

    // Read the color of the current pixel, which holds the value of u at grid point i.
    vec4 color = texture( inTexture , cc ) ;

    // Use fract for periodic boundary conditions.
    // This wraps the texture coordinates, so sampling beyond the edge wraps to the opposite side.
    // Fetch the state 'u' from the neighboring pixels to the right (i+1) and left (i-1).
    vec4 color_plus  = texture(inTexture, fract(cc + ii));
    vec4 color_minus = texture(inTexture, fract(cc - ii));

    // Extract the scalar field 'u' from the red channel of the fetched colors.
    float u_c = u;              // u at current point i
    float u_p = color_plus.r;   // u at right point i+1
    float u_m = color_minus.r;  // u at left point i-1

    // Calculate the spatial derivatives using the helper functions.
    // The PDE is du/dt = -convection + diffusion.
    float conv = convectiveTerm(u_p, u_m);
    float diff = viscousTerm(u_p, u_c, u_m);

    // Update the solution in time using the explicit Forward Euler method.
    // u_new = u_current + dt * (du/dt)
    float u_new = u_c + dt * (diff - conv);

    // Write the new value of u to the output color's red channel.
    // Preserve the other channels (g, b, a) from the original texture.
    ocolor = vec4(u_new, color.gba);
    return ;
}
