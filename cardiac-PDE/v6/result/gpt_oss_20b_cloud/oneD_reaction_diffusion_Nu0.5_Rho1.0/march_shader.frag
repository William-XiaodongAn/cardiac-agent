precision highp float ;
precision highp int ;

uniform sampler2D   inTexture ;
uniform float       dt, dx, dy;

in vec2 cc, pixPos ;

layout (location = 0) out vec4 ocolor ;

#define u       color.r
const float nu = 0.5;
const float rho = 1.0;

// Helper function to sample with periodic boundary conditions
float getU(sampler2D tex, vec2 coord) {
    return texture(tex, fract(coord)).r;
}

// Helper function to compute the 2D Laplacian
float laplacian2D(float u, float ul, float ur, float ud, float uu, float dx, float dy) {
    return (ul + ur - 2.0 * u) / (dx * dx) + (ud + uu - 2.0 * u) / (dy * dy);
}

void main() {
    vec2 size = vec2(textureSize(inTexture, 0));
    vec2 ii = vec2(1.,0.)/size;
    vec2 jj = vec2(0.,1.)/size;

    vec4 color = texture(inTexture , cc);

    float u0 = color.r;

    float ul = getU(inTexture, cc - ii); // left
    float ur = getU(inTexture, cc + ii); // right
    float ud = getU(inTexture, cc - jj); // down
    float uu = getU(inTexture, cc + jj); // up

    float lap = laplacian2D(u0, ul, ur, ud, uu, dx, dy);
    float reaction = rho * u0 * (1.0 - u0);

    float newu = u0 + dt * (nu * lap + reaction);
    newu = clamp(newu, 0.0, 1.0);

    ocolor = vec4(newu, newu, newu, 1.0);
    return ;
}