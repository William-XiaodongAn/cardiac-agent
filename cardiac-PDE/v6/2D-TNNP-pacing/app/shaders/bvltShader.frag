#version 300 es
/*@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
 * bvltShader
 *
 * PROGRAMMER   :   ABOUZAR KABOUDIAN
 * DATE         :   Thu 07 Sep 2017 08:36:02 PM EDT 
 * PLACE        :   Chaos Lab @ GaTech, Atlanta, GA
 *@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
 */
#include precision.glsl

in vec2        pixPos ;

uniform sampler2D   map ;
uniform float       ry ;


layout (location=0) out vec4 FragColor ;

/*=========================================================================
 * main
 *=========================================================================
 */
void main(){
    vec4 val = texture( map, pixPos ) ;
    float V = val.r ;
    if ( pixPos.y < ry ){
        V = 10. ;
    } ;
    val.r = V ;
    FragColor = val ;
    return ;
}
