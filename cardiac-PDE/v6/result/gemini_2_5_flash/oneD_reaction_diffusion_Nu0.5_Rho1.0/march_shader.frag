precision highp float ;
precision highp int ;

uniform sampler2D   inTexture ;
uniform float       dt, dx, dy;

in vec2 cc, pixPos ;

layout (location = 0) out vec4 ocolor ;

#define u       color.r
    const float nu = 0.5;
    const float rho = 1.0;
// your codes here for helper function

// your codes here for helper function

// Main body of the shader
void main() {
    vec2  size  = vec2(textureSize(inTexture, 0)) ;

    // For 1D simulation, we only care about the x-dimension
    // ii represents a step of 1 pixel in the x-direction
    vec2 ii = vec2(1.,0.)/size ;
    // jj would be for the y-direction, not used in 1D
    // vec2 jj = vec2(0.,1.)/size ;

    // read the color of the current pixel (u at current position and time)
    vec4 color = texture( inTexture , cc ) ;

    // --- Diffusion Term (Explicit Euler) ---
    // Read neighbor values with periodic boundary conditions
    float u_prevX = texture(inTexture, fract(cc - ii)).r;
    float u_nextX = texture(inTexture, fract(cc + ii)).r;

    // Calculate the second spatial derivative (Laplacian for 1D)
    float laplacian_u = (u_nextX - 2.0 * u + u_prevX) / (dx * dx);

    // Contribution from the diffusion term
    float du_diffusion = nu * laplacian_u;

    // Update u based on diffusion term over dt
    float u_intermediate = u + dt * du_diffusion;

    // --- Reaction Term (Piecewise-Exact Solution for Logistic Growth) ---
    // The reaction term is rho * u * (1 - u).
    // The exact solution for du/dt = rho * u * (1 - u) is:
    // u(t+dt) = u(t) * exp(rho * dt) / (1 - u(t) + u(t) * exp(rho * dt))
    // We use u_intermediate as u(t) for this step (operator splitting)

    float u0_reaction = u_intermediate;
    float exp_rho_dt = exp(rho * dt);

    float u_new_reaction_term_num = u0_reaction * exp_rho_dt;
    float u_new_reaction_term_den = 1.0 - u0_reaction + u0_reaction * exp_rho_dt;

    // Avoid division by zero and handle potential numerical issues for u0_reaction near 0 or 1
    float u_final_val;
    if (abs(u_new_reaction_term_den) < 1e-9) { // Denominator is close to zero
        u_final_val = sign(u0_reaction); // Will be 0 or 1 if u0_reaction is 0 or 1
    } else {
        u_final_val = u_new_reaction_term_num / u_new_reaction_term_den;
    }

    // Clamp the final value to [0,1] just in case of minor numerical errors
    u_final_val = clamp(u_final_val, 0.0, 1.0);

    // Output the new value of u (stored in the red channel)
    ocolor = vec4(u_final_val, 0.0, 0.0, 1.0) ;
    return ;
}