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

    // ii and jj represent the step in texture coordinates for one pixel in x and y directions
    vec2 ii = vec2(1.,0.)/size ;
    vec2 jj = vec2(0.,1.)/size ;

    // read the color of the current pixel (u, v)
    vec4 color = texture( inTexture , cc ) ;

    // --- Read neighboring pixel values for Laplacian calculation ---
    // Using fract() for periodic boundary conditions
    vec2 prevX_coord = fract(cc - ii);
    vec2 nextX_coord = fract(cc + ii);
    vec2 prevY_coord = fract(cc - jj);
    vec2 nextY_coord = fract(cc + jj);

    // Read u and v from neighboring pixels
    float u_prevX = texture(inTexture, prevX_coord).r;
    float u_nextX = texture(inTexture, nextX_coord).r;
    float u_prevY = texture(inTexture, prevY_coord).r;
    float u_nextY = texture(inTexture, nextY_coord).r;

    float v_prevX = texture(inTexture, prevX_coord).g;
    float v_nextX = texture(inTexture, nextX_coord).g;
    float v_prevY = texture(inTexture, prevY_coord).g;
    float v_nextY = texture(inTexture, nextY_coord).g;

    // --- Calculate Laplacian using central finite differences ---
    // (d^2 u / dx^2) = (u(x+dx,y) - 2u(x,y) + u(x-dx,y)) / dx^2
    // (d^2 u / dy^2) = (u(x,y+dy) - 2u(x,y) + u(x,y-dy)) / dy^2
    float laplacian_u = (u_nextX - 2.0 * u + u_prevX) / (dx * dx) +
                        (u_nextY - 2.0 * u + u_prevY) / (dy * dy);

    float laplacian_v = (v_nextX - 2.0 * v + v_prevX) / (dx * dx) +
                        (v_nextY - 2.0 * v + v_prevY) / (dy * dy);

    // --- Calculate reaction terms ---
    // R_u = u - u^3 - k - v
    // R_v = u - v
    float reaction_u = u - u * u * u - k - v;
    float reaction_v = u - v;

    // --- Calculate time derivatives (du/dt, dv/dt) ---
    // du/dt = D_u * (laplacian_u) + R_u
    // dv/dt = D_v * (laplacian_v) + R_v
    float du_dt = D_u * laplacian_u + reaction_u;
    float dv_dt = D_v * laplacian_v + reaction_v;

    // --- Euler integration to update u and v ---
    // u_new = u_current + dt * (du/dt)
    // v_new = v_current + dt * (dv/dt)
    float u_new = u + dt * du_dt;
    float v_new = v + dt * dv_dt;

    // --- Output the new u and v values ---
    // Store u_new in the red channel and v_new in the green channel
    ocolor = vec4(u_new, v_new, 0.0, 1.0) ;
    return ;
}