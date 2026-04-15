precision highp float;
precision highp int;

uniform sampler2D inTexture;
uniform float dt, dx, dy;

in vec2 cc, pixPos;

layout (location = 0) out vec4 ocolor;

#define u color.r
const float beta = 0.1;

// your codes here for helper function

// your codes here for helper function

// Main body of the shader
void main() {
    vec2 size = vec2(textureSize(inTexture, 0)) ;

    vec2 ii = vec2(1.,0.)/size ;
    vec2 jj = vec2(0.,1.)/size ;

    // read the color of the pixel
    vec4 color = texture( inTexture , cc ) ;


    // your codes here (do not define helper function)
    vec2 nextX = cc + ii;
    vec4 nextColor = texture(inTexture, nextX);
    float u_next = nextColor.r;
    float du_dx = (u_next - u) / dx;
    float du_dt = beta * du_dx;
    float u_new = u + dt * du_dt;
    ocolor.r = u_new;
    // your codes here (do not define helper function)

    // ocolor = color ;
    return ;
}