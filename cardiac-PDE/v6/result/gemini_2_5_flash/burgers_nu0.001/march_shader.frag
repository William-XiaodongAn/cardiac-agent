precision highp float ;
precision highp int ;

uniform sampler2D   inTexture ;
uniform float       dt, dx, dy;

in vec2 cc, pixPos ;

layout (location = 0) out vec4 ocolor ;

#define u       color.r
    const float nu = 0.001;
// your codes here for helper function

// your codes here for helper function

// Main body of the shader
void main() {
    vec2  size  = vec2(textureSize(inTexture, 0)) ;

    vec2 ii = vec2(1.0, 0.0) / size;

    // read the color of the pixel
    vec4 color = texture( inTexture , cc ) ;
    float u_curr = u; // u_i^n

    // use fract for periodic condition
    vec2 prevX_coord = fract(cc - ii); // Coordinate for u_{i-1}
    vec2 nextX_coord = fract(cc + ii); // Coordinate for u_{i+1}

    // Read neighbor values
    float u_prevX = texture(inTexture, prevX_coord).r; // u_{i-1}^n
    float u_nextX = texture(inTexture, nextX_coord).r; // u_{i+1}^n

    // your codes here (do not define helper function)

    // Calculate Advection Term: - d/dx (u^2 / 2)
    // F(u) = u^2 / 2
    float F_prevX = u_prevX * u_prevX / 2.0;
    float F_nextX = u_nextX * u_nextX / 2.0;
    float dF_dx = (F_nextX - F_prevX) / (2.0 * dx);
    float advection_term = -dF_dx;

    // Calculate Diffusion Term: (nu / pi) * d^2/dx^2 u
    // d^2u/dx^2 = (u_{i+1} - 2u_i + u_{i-1}) / (dx^2)
    float d2u_dx2 = (u_nextX - 2.0 * u_curr + u_prevX) / (dx * dx);
    const float PI = 3.14159265359;
    float diffusion_term = (nu / PI) * d2u_dx2;

    // Update u using Forward Euler
    float u_new = u_curr + dt * (advection_term + diffusion_term);

    // your codes here (do not define helper function)

    ocolor = vec4(u_new, 0.0, 0.0, 1.0) ;
}