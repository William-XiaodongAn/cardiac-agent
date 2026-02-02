// Save Voltage Function Reference
// Add this function after the pacing() function definition

var voltageSaved = false;

function saveVoltage(saveTime) {
    if (env.time >= saveTime && !voltageSaved) {
        var canvas2 = document.getElementById('canvas_2');
        
        // 1. Create a temporary canvas of the same size
        var tempCanvas = document.createElement('canvas');
        tempCanvas.width = canvas2.width;
        tempCanvas.height = canvas2.height;
        var tempCtx = tempCanvas.getContext('2d');

        // 2. Fill the temporary canvas with white
        tempCtx.fillStyle = 'white';
        tempCtx.fillRect(0, 0, tempCanvas.width, tempCanvas.height);

        // 3. Draw your original canvas content on top of the white background
        tempCtx.drawImage(canvas2, 0, 0);

        // 4. Save the temporary canvas instead
        var link = document.createElement('a');
        link.download = 'voltage_trace_' + saveTime + 'ms.png';
        link.href = tempCanvas.toDataURL('image/png'); // Explicitly set PNG
        link.click();

        voltageSaved = true;
        console.log('Voltage trace saved at ' + saveTime + 'ms with white background');
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
