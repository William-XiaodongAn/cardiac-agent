precision highp float;
precision highp int;

uniform sampler2D inTexture;
uniform float dt, dx, dy;

in vec2 cc, pixPos;

layout (location = 0) out vec4 ocolor;

#define u color.r
const float beta = 0.1;

// Helper function: read value from texture with periodic wrap
float sampleU(vec2 texCoord, vec2 offset) {
    vec2 wrapped = fract(texCoord + offset);
    return texture(inTexture, wrapped).r;
}

void main() {
    vec4 color = texture(inTexture, cc);
    float u_curr = color.r;

    vec2 texSize = vec2(textureSize(inTexture, 0));
    vec2 ii = vec2(1.0, 0.0) / texSize; 
    // left neighbor (i-1)
    float u_left = sampleU(cc, -ii);

    // explicit upwind discretisation: u^{n+1} = u^n - dt*beta*(u_i - u_{i-1})/dx
    float u_new = u_curr - dt * beta * (u_curr - u_left) / dx;

    color.r = u_new;
    ocolor = color;
}