// Plot Tip Function Reference
// Add this function after the march() function definition
TiptVisiblity = false ;
function plotTip(startTime,endTime){
    if (env.time >= startTime && env.time <= endTime && !TiptVisiblity) {
        TiptVisiblity = true ;
        plot.setTiptVisiblity(TiptVisiblity) ;
    } else {
        TiptVisiblity = false;
        plot.setTiptVisiblity(TiptVisiblity) ;
    }
}

// Usage in run() function:
// Place plotTip(500,2500) after march() inside the loop
// Example:
/*
function run(){
    if (env.running){
        for(var i = 0 ; i<env.skip ; i++){
            march() ;
            plotTip(500,2500) ;  // Show tip between 500ms and 2500ms
            env.usgn.update(env.time) ;
        }
    }
    splot.render() ;
    plot.render() ;
    requestAnimationFrame(run) ;
}
*/