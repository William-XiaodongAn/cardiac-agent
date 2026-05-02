precision highp float ;
precision highp int ;

uniform sampler2D   inTexture1 ;
uniform sampler2D   inTexture2 ;
uniform sampler2D   inTexture3 ;
uniform sampler2D   inTexture4 ;
uniform sampler2D   inTexture5 ;

uniform float       dt, dx, dy;

in vec2 cc, pixPos ;

layout (location = 0) out vec4 ocolor1 ;
layout (location = 1) out vec4 ocolor2 ;
layout (location = 2) out vec4 ocolor3 ;
layout (location = 3) out vec4 ocolor4 ;
layout (location = 4) out vec4 ocolor5 ;

#define r1       color1.r
#define g1       color1.g
#define b1       color1.b
#define a1       color1.a

#define r2       color2.r
#define g2       color2.g
#define b2       color2.b
#define a2       color2.a

#define r3       color3.r
#define g3       color3.g
#define b3       color3.b
#define a3       color3.a

#define r4       color4.r
#define g4       color4.g
#define b4       color4.b
#define a4       color4.a

#define r5       color5.r
#define g5       color5.g
#define b5       color5.b
#define a5       color5.a

{{PARAMETER_VALUES}}
// your codes here for helper function

// your codes here for helper function

// Main body of the shader
void main() {
    vec2  size  = vec2(textureSize(inTexture1, 0)) ;

    vec2 ii = vec2(1.,0.)/size ;
    vec2 jj = vec2(0.,1.)/size ;

    // read the color of the pixel
    vec4 color1 = texture( inTexture1 , cc ) ;
    vec4 color2 = texture( inTexture2 , cc ) ;
    vec4 color3 = texture( inTexture3 , cc ) ;
    vec4 color4 = texture( inTexture4 , cc ) ;
    vec4 color5 = texture( inTexture5 , cc ) ;

    // use fract for periodic condition
    // for example: vec2 prevX = fract(cc - ii);
    // Neumann (no-flux) boundary conditions in default
    // for example: vec2 prevX = cc - ii;
    // your codes here (do not define helper function)

    // your codes here (do not define helper function)

    ocolor1 = color1 ;
    ocolor2 = color2 ;
    ocolor3 = color3 ;
    ocolor4 = color4 ;
    ocolor5 = color5 ;
    return ;
}