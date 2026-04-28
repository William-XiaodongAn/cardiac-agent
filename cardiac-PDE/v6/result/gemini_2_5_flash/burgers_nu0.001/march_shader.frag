precision highp float ;
precision highp int ;

uniform sampler2D   inTexture ;
uniform float       dt, dx, dy;

in vec2 cc, pixPos ;

layout (location = 0) out vec4 ocolor ;

#define u       color.r
    const float nu = 0.001;
// your codes here for helper function
// Helper function to get the 'u' component (red channel) from the texture at a given coordinate.
// It applies 'fract' to the coordinate, ensuring periodic boundary conditions.
float getU_val(vec2 coord) {
    return texture(inTexture, fract(coord)).r;
}

// Main body of the shader
void main() {
    vec2  size  = vec2(textureSize(inTexture, 0)) ;

    // ii represents the texture coordinate step for one pixel in the x-direction.
    vec2 ii = vec2(1.,0.)/size ;
    // jj represents the texture coordinate step for one pixel in the y-direction.
    // For this 1D PDE (Burgers' equation in x), jj is not directly used for spatial derivatives.
    vec2 jj = vec2(0.,1.)/size ;

    // read the color of the pixel at the current coordinate 'cc'.
    // The #define u color.r means that 'u' will refer to the red channel of this 'color' variable.
    vec4 color = texture( inTexture , cc ) ;

    // your codes here (do not define helper function)
    // Get the current 'u' value at this pixel location.
    float u_current = u; // Using the #define u color.r here.

    // Get 'u' values from the left and right neighboring pixels using the helper function.
    // The 'fract' function within getU_val handles periodic boundary conditions.
    float u_left = getU_val(cc - ii); // u at j-1
    float u_right = getU_val(cc + ii); // u at j+1

    // Calculate the advection term for Burgers' equation: -d/dx (u^2/2)
    // We use a central difference scheme for the flux F(u) = u^2/2.
    // Term: -(F(u_right) - F(u_left)) / (2 * dx)
    float F_right = 0.5 * u_right * u_right;
    float F_left = 0.5 * u_left * u_left;
    float advection_term = -(F_right - F_left) / (2.0 * dx);

    // Calculate the diffusion term: nu * d^2/dx^2 (u)
    // We use a central difference scheme for the second spatial derivative.
    // Term: nu * (u_right - 2*u_current + u_left) / dx^2
    float diffusion_term = nu * (u_right - 2.0 * u_current + u_left) / (dx * dx);

    // Update 'u' using the explicit Euler time integration scheme.
    // u_new = u_current + dt * (advection_term + diffusion_term)
    float u_new = u_current + dt * (advection_term + diffusion_term);

    // Store the newly computed 'u_new' value into the red channel of the output color.
    // The other channels (green, blue, alpha) are typically set to default values (0.0, 0.0, 1.0)
    // as only the red channel is used for the 1D simulation state.
    ocolor = vec4(u_new, 0.0, 0.0, 1.0);
    return ;
}