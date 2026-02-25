<script id='march' type='shader'>
#version 300 es
precision highp float ;
precision highp int ;

uniform sampler2D   inTexture ;
uniform float       dt, Lx, Ly;

in vec2 cc, pixPos ;

layout (location = 0) out vec4 ocolor ;

#define x1       color.r
#define x2       color.g
#define x3       color.b

// Main body of the shader
void main() {
    vec2  size  = vec2(textureSize(inTexture, 0)) ;
    float dx    = Lx/size.x ;
    float dy    = Ly/size.y ;

    vec2 ii = vec2(1.,0.)/size ;
    vec2 jj = vec2(0.,1.)/size ;

    // read the color of the pixel .......................................
    vec4 color = texture( inTexture , cc ) ;

    // Standard Laplacian calculation for x1
    float laplacian = (
        texture(inTexture, cc + ii).r + 
        texture(inTexture, cc - ii).r + 
        texture(inTexture, cc + jj).r + 
        texture(inTexture, cc - jj).r - 
        4.0 * x1
    ) / (dx*dx) ;

    // Parameter Assignments ---------------------------
    //float para = value;


    // Parameter Assignments ---------------------------


    // PDEs ---------------------------


    // PDEs ---------------------------

    ocolor = color ;
    return ;
}
</script>