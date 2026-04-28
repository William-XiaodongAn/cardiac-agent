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

// helper function for periodic/Neumann boundary sampling
vec4 sampleClamp(vec2 offset) {
    return texture(inTexture, clamp(cc + offset, 0.0, 1.0));
}

void main() {
    vec2  size  = vec2(textureSize(inTexture, 0));
    vec2 ii = vec2(1.,0.)/size ;
    vec2 jj = vec2(0.,1.)/size ;

    // read the color of the pixel
    vec4 color = texture(inTexture , cc ) ;

    // compute neighbor samples with Neumann boundary condition (clamp)
    vec4 left  = sampleClamp(-ii);
    vec4 right = sampleClamp(ii);
    vec4 bottom = sampleClamp(-jj);
    vec4 top    = sampleClamp(jj);

    // extract current values
    float uCurr = color.r;
    float vCurr = color.g;

    // discrete Laplacians
    float lapU = (left.r + right.r - 2.0*uCurr) / (dx*dx) + (bottom.r + top.r - 2.0*uCurr) / (dy*dy);
    float lapV = (left.g + right.g - 2.0*vCurr) / (dx*dx) + (bottom.g + top.g - 2.0*vCurr) / (dy*dy);

    // Euler time stepping
    float uNew = uCurr + dt * (D_u * lapU + uCurr - uCurr*uCurr*uCurr - k - vCurr);
    float vNew = vCurr + dt * (D_v * lapV + uCurr - vCurr);

    ocolor = vec4(uNew, vNew, 0.0, 1.0);
    return;
}