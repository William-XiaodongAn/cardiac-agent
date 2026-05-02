/*========================================================================
 * Configure Require.js
 *========================================================================
 */
var require = {
    /*  The following is required 
        for URL busting and avoiding cache! */
    urlArgs: "bust=" + (new Date()).getTime(),
    baseUrl: './',
         // Default load path for js files
    shim: {
             // --- Use shim to mix together all THREE.js subcomponents
             'threeCore': { exports: 'THREE' },
             'detector': { exports: 'Detector' },
         },
         // Third party code lives in js/lib
    paths: {
           // --- start THREE sub-components
        three: 'libs/three',
        threeCore: 'libs/three.min',
        // Require.js plugins
        text: 'libs/text',
        shader: 'libs/shader', /* looks in the ./shaders/ directory */
        image:  'libs/image',
    }
};
