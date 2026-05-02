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

    const float Ko = 5.4;
    const float Cao = 2.0;
    const float Nao = 140.0;
    const float Vc = 0.016404;
    const float Vsr = 0.001094;
    const float Vss = 5.468e-05;
    const float Bufc = 0.2;
    const float Kbufc = 0.001;
    const float Bufsr = 10.0;
    const float Kbufsr = 0.3;
    const float Bufss = 0.4;
    const float Kbufss = 0.00025;
    const float Vmaxup = 0.006375;
    const float Kup = 0.00025;
    const float Vrel = 0.102;
    const float k3 = 0.06;
    const float k4 = 0.005;
    const float k1prime = 0.15;
    const float k2prime = 0.045;
    const float EC = 1.5;
    const float maxsr = 2.5;
    const float minsr = 1.0;
    const float Vleak = 0.00036;
    const float Vxfer = 0.0038;
    const float RR = 8314.3;
    const float FF = 96486.7;
    const float TT = 310.0;
    const float CAPACITANCE = 0.185;
    const float Gks = 0.392;
    const float Gto = 0.294;
    const float Gkr = 0.153;
    const float pKNa = 0.03;
    const float GK1 = 5.405;
    const float alphanaca = 1.0;
    const float GNa = 14.838;
    const float GbNa = 0.00029;
    const float KmK = 1.0;
    const float KmNa = 40.0;
    const float knak = 2.724;
    const float GCaL = 3.98e-05;
    const float GbCa = 0.000592;
    const float knaca = 1000.0;
    const float KmNai = 87.5;
    const float KmCa = 1.38;
    const float ksat = 0.1;
    const float n = 0.35;
    const float GpCa = 0.1238;
    const float KpCa = 0.0005;
    const float GpK = 0.0146;
    const float diffCoef = 0.001;

// Helper function to compute Laplacian with Neumann (no-flux) BC
float laplacian(sampler2D tex, vec2 uv, vec2 ii, vec2 jj, float dx, float dy)
{
    // clamp coordinates to edge for Neumann BC
    vec2 uvXMinus = clamp(uv - ii, vec2(0.0), vec2(1.0));
    vec2 uvXPlus  = clamp(uv + ii, vec2(0.0), vec2(1.0));
    vec2 uvYMinus = clamp(uv - jj, vec2(0.0), vec2(1.0));
    vec2 uvYPlus  = clamp(uv + jj, vec2(0.0), vec2(1.0));

    float vCenter = texture(tex, uv).r;

    float lap = 0.0;
    lap += (texture(tex, uvXMinus).r + texture(tex, uvXPlus).r - 2.0 * vCenter) / (dx * dx);
    lap += (texture(tex, uvYMinus).r + texture(tex, uvYPlus).r - 2.0 * vCenter) / (dy * dy);
    return lap;
}

void main() {
    vec2  size  = vec2(textureSize(inTexture1, 0)) ;

    vec2 ii = vec2(1.,0.)/size ;
    vec2 jj = vec2(0.,1.)/size ;

    // Read the current values
    vec4 color1 = texture( inTexture1 , cc ) ;
    vec4 color2 = texture( inTexture2 , cc ) ;
    vec4 color3 = texture( inTexture3 , cc ) ;
    vec4 color4 = texture( inTexture4 , cc ) ;
    vec4 color5 = texture( inTexture5 , cc ) ;

    // Compute Laplacians for each variable
    float lap1 = laplacian(inTexture1, cc, ii, jj, dx, dy);
    float lap2 = laplacian(inTexture2, cc, ii, jj, dx, dy);
    float lap3 = laplacian(inTexture3, cc, ii, jj, dx, dy);
    float lap4 = laplacian(inTexture4, cc, ii, jj, dx, dy);
    float lap5 = laplacian(inTexture5, cc, ii, jj, dx, dy);

    // Simple reaction terms (placeholder: no reaction) 
    // More complex dynamics can be inserted here using provided constants.
    float reaction1 = 0.0;
    float reaction2 = 0.0;
    float reaction3 = 0.0;
    float reaction4 = 0.0;
    float reaction5 = 0.0;

    // Update each variable with diffusion
    vec4 newColor1 = color1;
    vec4 newColor2 = color2;
    vec4 newColor3 = color3;
    vec4 newColor4 = color4;
    vec4 newColor5 = color5;

    newColor1.r += dt * (diffCoef * lap1 + reaction1);
    newColor2.r += dt * (diffCoef * lap2 + reaction2);
    newColor3.r += dt * (diffCoef * lap3 + reaction3);
    newColor4.r += dt * (diffCoef * lap4 + reaction4);
    newColor5.r += dt * (diffCoef * lap5 + reaction5);

    // Preserve other color channels
    ocolor1 = newColor1;
    ocolor2 = newColor2;
    ocolor3 = newColor3;
    ocolor4 = newColor4;
    ocolor5 = newColor5;
}
