precision highp float;
precision highp int;

uniform sampler2D   inTexture ;
uniform float       dt, dx, dy;

in vec2 cc, pixPos ;

layout (location = 0) out vec4 ocolor ;

#define u       color.r
    const float beta = 0.1;

vec2 periodicPos(vec2 pos, float step) {
    return vec2(fract(pos.x - step), pos.y);
}

vec2 periodicPos(vec2 pos, float step) {
    return vec2(fract(pos.x + step), pos.y);
}

void main() {
    vec2  size  = vec2(textureSize(inTexture, 0)) ;

    vec2 ii = vec2(1.,0.)/size ;
    vec2 jj = vec2(0.,1.)/size ;

    // read the color of the pixel
    vec4 color = texture( inTexture , cc ) ;

    // Compute left neighbor position
    vec2 leftPos = periodicPos(cc, dx);
    vec4 leftColor = texture(inTexture, leftPos);

    // Compute new value
    float u_current = color.r;
    float u_left = leftColor.r;
    float u_new = u_current - beta * dt / dx * (u_current - u_left);

    ocolor.r = u_new;
    return ;
}