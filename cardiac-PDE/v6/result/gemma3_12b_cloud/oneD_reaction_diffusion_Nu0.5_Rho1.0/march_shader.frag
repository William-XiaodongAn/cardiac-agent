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

    vec2 ii = vec2(1.,0.)/size ;
    vec2 jj = vec2(0.,1.)/size ;

    // read the color of the pixel
    vec4 color = texture( inTexture , cc ) ;

    // use fract for periodic condition
    vec2 prevX = fract(cc - ii);
    vec2 nextX = fract(cc + ii);
    vec2 prevY = fract(cc - jj);
    vec2 nextY = fract(cc + jj);

    float u_curr = color.r;
    float u_prev_x = texture(inTexture, prevX).r;
    float u_next_x = texture(inTexture, nextX).r;
    float u_prev_y = texture(inTexture, prevY).r;
    float u_next_y = texture(inTexture, nextY).r;

    float du_dt = nu * ( (u_next_x - 2.0 * u_curr + u_prev_x) / (dx * dx) + (u_next_y - 2.0 * u_curr + u_prev_y) / (dy * dy) ) - rho * u_curr * (1.0 - u_curr);

    float u_new = u_curr + dt * du_dt;
    u_new = clamp(u_new, 0.0, 1.0);

    ocolor = vec4(u_new, 0.0, 0.0, 1.0);
    return ;
}, boundary condition Periodic and special notes None