/**
 * @license RequireJS Image Plugin <https://gist.github.com/821476>
 * @author Miller Medeiros
 * @Modified by Abouzar Kaboudian
 * @DATE    : Mon 31 Jul 2017 10:18:26 AM EDT
 * @PLACE   : CHAOS LAB AT GEORGIA INSTITUTE OF TECHNOLOGY
 * Released under the MIT License <http://www.opensource.org/licenses/mit-license.php>
 */
(function(){
    define({
        load : function(name, req, onLoad, config){
            var img;
            if(config.isBuild){
                onLoad(null); //avoid errors on the optimizer since it can't inline image files.
            }else{
                img = new Image();
                img.onload = function(evt){
                    onLoad(img);
                    delete img.onload; //release memory - suggested by John Hann
                };
                img.src = require.toUrl(name);
            }
        },
    });
}());
