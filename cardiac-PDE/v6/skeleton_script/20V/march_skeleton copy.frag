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

Ko = 5.4;
Cao = 2.0;
Nao = 140.0;
Vc = 0.016404;
Vsr = 0.001094;
Vss = 0.00005468;
Bufc = 0.2;
Kbufc = 0.001;
Bufsr = 10.0;
Kbufsr = 0.3;
Bufss = 0.4;
Kbufss = 0.00025;
Vmaxup = 0.006375;
Kup = 0.00025;
Vrel = 0.102;
k3 = 0.060;
k4 = 0.005;
k1prime = 0.15;
k2prime = 0.045;
EC = 1.5;
maxsr = 2.5;
minsr = 1.0;
Vleak = 0.00036;
Vxfer = 0.0038;
RR = 8314.3;
FF = 96486.7;
TT = 310.0
CAPACITANCE = 0.185;
Gks = 0.392;
Gto = 0.294;
Gkr = 0.153;
pKNa = 0.03;
GK1 = 5.405;
alphanaca = 2.5;
GNa = 14.838;
GbNa = 0.00029;
KmK = 1.0;
KmNa = 40.0;
knak = 2.724;
GCaL = 0.00003980;
GbCa = 0.000592;
knaca = 1000.0;
KmNai = 87.5;
KmCa = 1.38;
ksat = 0.1;
n = 0.35;
GpCa = 0.1238;
KpCa = 0.0005;
GpK = 0.0146;

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

    ocolor = color ;
    return ;
}