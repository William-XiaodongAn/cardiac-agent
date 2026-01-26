// Save Voltage Function Reference
// Add this function after the pacing() function definition

var voltageSaved = false;

function saveVoltage(saveTime){
    if (env.time >= saveTime && !voltageSaved) {
        var canvas2 = document.getElementById('canvas_2');
        var link = document.createElement('a');
        link.download = 'voltage_trace_' + saveTime + 'ms.png';
        link.href = canvas2.toDataURL();
        link.click();
        voltageSaved = true;
        console.log('Voltage trace saved at ' + saveTime + 'ms');
    }
}

// Usage in run() function:
// Place saveVoltage(1000) after pacing() inside the loop
// Example:
/*
var voltageSaved = false;  // Add this at top with other variables

function run(){
    if (env.running){
        for(var i = 0 ; i<env.skip ; i++){
            march() ;
            pacing(500) ;
            saveVoltage(1000) ;  // Saves canvas_2 at 1000ms
            env.usgn.update(env.time) ;
        }
    }
    splot.render() ;
    plot.render() ;
    requestAnimationFrame(run) ;
}
*/
