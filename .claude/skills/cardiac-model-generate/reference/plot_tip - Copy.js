// S1-S2 Initialization Function Reference
<script id='init' type='shader'>#version 300 es
precision highp float ;
precision highp int ;

in vec2 cc, pixPos ;

layout (location = 0) out vec4 color1 ;
layout (location = 1) out vec4 color2 ;

// Main body of the shader
void main() {
    vec4 color = vec4(0.) ;
    
    color.r = 0. ;
	color.g = 1. ;
	color.b = 1. ;

    // added lines for S1-S2 initialization
    if ( cc.x < 0.1 ){
        color.r = 1. ;
    }    
    // added lines for S1-S2 initialization

	color1 = color ;
    color2 = color ;


    return ;
}
</script>

// added lines for S1-S2 initialization

<script id='initS1S2' type='shader'>#version 300 es
precision highp float ;
precision highp int ;

in vec2 cc, pixPos ;

layout (location = 0) out vec4 color1 ;
layout (location = 1) out vec4 color2 ;

// Main body of the shader
void main() {
    vec4 color = vec4(0.) ;
    
    color.r = 0. ;
	color.g = 1. ;
	color.b = 1. ;

    // added lines for S1-S2 initialization
    if ( cc.x < 0.1 ){
        color.r = 1. ;
    }    
    // added lines for S1-S2 initialization

	color1 = color ;
    color2 = color ;


    return ;
}
</script>


var turn_red_first = false;
var turn_red_second = false;
var measurePoint = fcolor[525312];
function S1S2Init(){
    if (!turn_red_first && measurePoint[0.5 * env.width | 0][0.5 * env.height | 0][0] > 0.9){
        turn_red_first = true;
        env.s1s2_time = env.time + 300.0;
    }
    if (turn_red_first && !turn_red_second && env.time >= env.s1s2_time){
        turn_red_second = true;
        env.initS1S2 = true;
        initS1S2.render() ;
    }
}
// added lines for S1-S2 initialization

// Usage in run() function:
// Example:
/*
function run(){
    if (env.running){
        for(var i = 0 ; i<env.skip ; i++){
            march() ;
            S1S2Init();
            env.usgn.update(env.time) ;
        }
    }
    splot.render() ;
    plot.render() ;
    requestAnimationFrame(run) ;
}
*/