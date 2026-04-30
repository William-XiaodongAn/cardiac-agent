precision highp float ;
precision highp int ;

uniform sampler2D   inTexture ;
uniform float       dt, dx, dy;

in vec2 cc, pixPos ;

layout (location = 0) out vec4 ocolor ;

#define u       color.r
#define v       color.g
    const float D_u = 0.001;
    const float D_v = 0.005;
    const float k = 0.005;
// your codes here for helper function

// your codes here for helper function

// Main body of the shader
void main() {
    vec2  size  = vec2(textureSize(inTexture, 0)) ;

    // ii and jj represent the normalized step size to move one pixel in x and y directions
    vec2 ii = vec2(1.,0.)/size ;
    vec2 jj = vec2(0.,1.)/size ;

    // Read the current pixel's color (u and v values)
    vec4 current_color = texture( inTexture , cc ) ;
    float u_curr = current_color.r;
    float v_curr = current_color.g;

    // Sample neighbor pixels. These samples might be from outside the texture if at a boundary,
    // in which case the values will be corrected for Neumann conditions.
    vec4 color_L = texture(inTexture, cc - ii); // Left neighbor
    vec4 color_R = texture(inTexture, cc + ii); // Right neighbor
    vec4 color_D = texture(inTexture, cc - jj); // Down neighbor
    vec4 color_U = texture(inTexture, cc + jj); // Up neighbor

    // Extract u and v components from neighbors
    float u_L = color_L.r;
    float u_R = color_R.r;
    float u_D = color_D.r;
    float u_U = color_U.r;

    float v_L = color_L.g;
    float v_R = color_R.g;
    float v_D = color_D.g;
    float v_U = color_U.g;

    // Apply Neumann boundary conditions (no-flux) using integer pixel coordinates
    // pixPos contains the integer coordinates of the current pixel (0 to size-1)
    if (pixPos.x == 0.0) { // At left boundary (first column)
        u_L = u_R;
        v_L = v_R;
    }
    if (pixPos.x == size.x - 1.0) { // At right boundary (last column)
        u_R = u_L;
        v_R = v_L;
    }
    if (pixPos.y == 0.0) { // At bottom boundary (first row)
        u_D = u_U;
        v_D = v_U;
    }
    if (pixPos.y == size.y - 1.0) { // At top boundary (last row)
        u_U = u_D;
        v_U = v_D;
    }

    // Calculate the Laplacian (second spatial derivative) for u and v
    // using central finite differences.
    float laplacian_u = (u_L - 2.0 * u_curr + u_R) / (dx * dx) +
                        (u_D - 2.0 * u_curr + u_U) / (dy * dy);

    float laplacian_v = (v_L - 2.0 * v_curr + v_R) / (dx * dx) +
                        (v_D - 2.0 * v_curr + v_U) / (dy * dy);

    // Calculate the reaction terms for u and v
    float reaction_u = u_curr - u_curr * u_curr * u_curr - k - v_curr;
    float reaction_v = u_curr - v_curr;

    // Calculate the time derivatives (du/dt and dv/dt)
    float d_u_dt = D_u * laplacian_u + reaction_u;
    float d_v_dt = D_v * laplacian_v + reaction_v;

    // Update u and v using explicit Euler method
    float u_new = u_curr + dt * d_u_dt;
    float v_new = v_curr + dt * d_v_dt;

    // Output the new u and v values to the output color buffer
    ocolor = vec4(u_new, v_new, current_color.b, current_color.a);
    return ;
}