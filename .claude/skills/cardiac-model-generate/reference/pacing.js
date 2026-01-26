// Pacing Function Reference
// Add this function after the march() function definition

function pacing(period){
    if (env.time % period < env.dt) {
        click.uniforms.clickPosition.value = [0.1, 0.1] ;
        click.render() ;
        clickCopy.render() ;
    }
}

// Usage in run() function:
// Place pacing(500) after march() inside the loop
// Example:
/*
function run(){
    if (env.running){
        for(var i = 0 ; i<env.skip ; i++){
            march() ;
            pacing(500) ;  // Paces every 500ms at position (0.1, 0.1)
            env.usgn.update(env.time) ;
        }
    }
    splot.render() ;
    plot.render() ;
    requestAnimationFrame(run) ;
}
*/
