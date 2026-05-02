precision highp float ;
precision highp int ;

uniform sampler2D   inTexture ;
uniform float       dt, dx, dy;

in vec2 cc, pixPos ;

layout (location = 0) out vec4 ocolor ;

#define u       color.r
    const float nu = 0.001;

// Helper function to get texture value with periodic boundary conditions
vec4 samplePeriodic(vec2 coord) {
    return texture(inTexture, fract(coord));
}

// Main body of the shader
void main() {
    // dx is already provided by the uniform, so we don't need to derive it from size
    // For 1D PDE on a 2D texture, we assume the x-dimension is the relevant one, and y is constant (or 0)
    // We'll use texture coordinates [0,1] for x.

    // read the color of the pixel at current position
    vec4 color = texture(inTexture, cc);

    // Get values from neighboring pixels using periodic boundary conditions
    vec2  size  = vec2(textureSize(inTexture, 0)) ; // To calculate pixel offset
    vec2 ii = vec2(1.,0.)/size ; // Offset for one pixel in x-direction

    vec4 prevX_color = samplePeriodic(cc - ii);
    vec4 nextX_color = samplePeriodic(cc + ii);
    vec4 prev2X_color = samplePeriodic(cc - 2.0 * ii);
    vec4 next2X_color = samplePeriodic(cc + 2.0 * ii);

    float u_prevX = prevX_color.r;
    float u_nextX = nextX_color.r;
    float u_prev2X = prev2X_color.r;
    float u_next2X = next2X_color.r;
    float u_curr = u;

    // Convection term: ∂(u^2/2)/∂x
    // Using a 5-point WENO (or similar high-order upwind) scheme for convection, or simpler scheme for first pass.
    // For simplicity and common practice in shaders, let's start with a central difference for the flux derivative.
    // F(u) = u^2/2
    // ∂F/∂x ≈ (F(u_nextX) - F(u_prevX)) / (2 * dx)
    // Or for stability, an upwind scheme for the non-linear flux.
    // Let's use a simple first-order upwind for the non-linear term.
    // If u > 0, use backward difference (u_curr - u_prevX)/dx
    // If u < 0, use forward difference (u_nextX - u_curr)/dx
    // This is for ∂u/∂x. For ∂(u^2/2)/∂x, we need to consider the sign of u.
    // A more robust approach for Burgers: F(u) = u^2/2. Use Lax-Friedrichs type flux or Godunov.
    // For a basic implementation, a central difference for the flux F(u) = u^2/2:
    // float F_nextX = 0.5 * u_nextX * u_nextX;
    // float F_prevX = 0.5 * u_prevX * u_prevX;
    // float dF_dx = (F_nextX - F_prevX) / (2.0 * dx);

    // Let's use a 3-point central difference for the flux derivative:
    float dF_dx = (0.5 * u_nextX * u_nextX - 0.5 * u_prevX * u_prevX) / (2.0 * dx);

    // Diffusion term: (nu/PI) * ∂^2 u / ∂x^2
    // Using a 3-point central difference for the second derivative:
    // ∂^2 u / ∂x^2 ≈ (u_nextX - 2*u_curr + u_prevX) / dx^2
    float d2u_dx2 = (u_nextX - 2.0 * u_curr + u_prevX) / (dx * dx);

    // Calculate the right-hand side of the PDE
    float dudt = -dF_dx + (nu / 3.1415926) * d2u_dx2;

    // Explicit Euler time integration
    float new_u = u_curr + dt * dudt;

    ocolor = vec4(new_u, color.g, color.b, color.a); // Update only the 'u' component
    return ;
}