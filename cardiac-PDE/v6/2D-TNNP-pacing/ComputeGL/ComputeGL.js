/*@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
 * ComputeGL.js :   library for computational work
 *
 * PROGRAMMER   :   ABOUZAR KABOUDIAN
 * DATE         :   Sat 12 Aug 2017 06:24:00 PM EDT
 * PLACE        :   Chaos Lab @ GaTech, Atlanta, GA
 *@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
 */
define([    'require',
            './libs/gl-matrix',
            './libs/dat.gui',
            /* Shaders */
            'shader!vertShader.vert',
            'shader!lvtxShader.vert',
            'shader!lfgmShader.frag',
            'shader!ipltShader.frag',
            'shader!histShader.frag',
            'shader!bgndShader.frag',
            'shader!dispShader.frag',
            'shader!dispPhasShader.frag',
            'shader!tiptShader.frag',
            'shader!tiptInitShader.frag',
            'shader!wA2bShader.frag',
            'shader!sctwShader.frag',
            'shader!lpvtShader.vert',

            /* volume ray caster shaders */
            'shader!vrc1VShader.vert',
            'shader!vrc1FShader.frag',
            'shader!vrc2VShader.vert',
            'shader!vrc2FShader.frag',
            'shader!vrcLgtShader.frag',
            'shader!vrcCrdShader.frag',
            'shader!vrcPCShader.frag',
            'shader!vrcClickCrdShader.frag',
            'shader!vrcClickVoxelCrdShader.frag',

            /* Colormaps */
            'image!./colormaps/chaoslab.png',
            'image!./colormaps/hotbrightbands.png',
            'image!./colormaps/brilliant.png',
            'image!./colormaps/oygb.png',
            'image!./colormaps/rainbowHotSpring.png',
            
            /* tica colormaps   */
            'image!./colormaps/tica/alpineColors.png',
            'image!./colormaps/tica/armyColors.png',
            'image!./colormaps/tica/atlanticColors.png',
            'image!./colormaps/tica/auroraColors.png',
            'image!./colormaps/tica/avacadoColors.png',
            'image!./colormaps/tica/beachColors.png',
            'image!./colormaps/tica/candyColors.png',
            'image!./colormaps/tica/cmykColors.png',
            'image!./colormaps/tica/deepSeaColors.png',
            'image!./colormaps/tica/fallColors.png',
            'image!./colormaps/tica/fruitPunchColors.png',
            'image!./colormaps/tica/islandColors.png',
            'image!./colormaps/tica/lakeColors.png',
            'image!./colormaps/tica/mintColors.png',
            'image!./colormaps/tica/neonColors.png',
            'image!./colormaps/tica/pearlColors.png',
            'image!./colormaps/tica/plumColors.png',
            'image!./colormaps/tica/roseColors.png',
            'image!./colormaps/tica/solarColors.png',
            'image!./colormaps/tica/southwestColors.png',
            'image!./colormaps/tica/starryNightColors.png',
            'image!./colormaps/tica/sunsetColors.png',
            'image!./colormaps/tica/thermometerColors.png',
            'image!./colormaps/tica/watermelonColors.png',
            'image!./colormaps/tica/brassTones.png',
            'image!./colormaps/tica/brownCyanTones.png',
            'image!./colormaps/tica/cherryTones.png',
            'image!./colormaps/tica/coffeeTones.png',
            'image!./colormaps/tica/fuchsiaTones.png',
            'image!./colormaps/tica/grayTones.png',
            'image!./colormaps/tica/greenPinkTones.png',
            'image!./colormaps/tica/pigeonTones.png',
            'image!./colormaps/tica/redBlueTones.png',
            'image!./colormaps/tica/rustTones.png',
            'image!./colormaps/tica/siennaTones.png',
            'image!./colormaps/tica/valentineTones.png',
            'image!./colormaps/tica/darkTerrain.png',
            'image!./colormaps/tica/greenBrownTerrain.png',
            'image!./colormaps/tica/lightTerrain.png',
            'image!./colormaps/tica/sandyTerrain.png',
            'image!./colormaps/tica/aquamarine.png',
            'image!./colormaps/tica/blueGreenYellow.png',
            'image!./colormaps/tica/brightBands.png',
            'image!./colormaps/tica/darkBands.png',
            'image!./colormaps/tica/darkRainbow.png',
            'image!./colormaps/tica/fuitPunch.png',
            'image!./colormaps/tica/lightTemperatureMap.png',
            'image!./colormaps/tica/pastel.png',
            'image!./colormaps/tica/rainbow.png',
            'image!./colormaps/tica/temperatureMap.png',            

            /* mat Colormaps    */
            'image!./colormaps/mat/autumn.png',
            'image!./colormaps/mat/blue.png',
            'image!./colormaps/mat/bone.png',
            'image!./colormaps/mat/colorcube.png',
            'image!./colormaps/mat/cool.png',
            'image!./colormaps/mat/copper.png',
            'image!./colormaps/mat/flag.png',
            'image!./colormaps/mat/gray.png',
            'image!./colormaps/mat/green.png',
            'image!./colormaps/mat/hot.png',
            'image!./colormaps/mat/hsv.png',
            'image!./colormaps/mat/jet.png',
            'image!./colormaps/mat/lines.png',
            'image!./colormaps/mat/parula.png',
            'image!./colormaps/mat/pink.png',
            'image!./colormaps/mat/prism.png',
            'image!./colormaps/mat/red.png',
            'image!./colormaps/mat/spring.png',
            'image!./colormaps/mat/summer.png',
            'image!./colormaps/mat/white.png',
            'image!./colormaps/mat/winter.png',
        ],
function(   require,
            glMatrix,
            GUI,
            /* Shaders */
            vertShader,
            lvtxShader,
            lfgmShader,
            ipltShader,
            histShader,
            bgndShader,
            dispShader,
            dispPhasShader,
            tiptShader,
            tiptInitShader,
            wA2bShader,
            sctwShader,
            lpvtShader,

            /* Volume Ray Caster Shaders */
            vrc1VShader,
            vrc1FShader,
            vrc2VShader,
            vrc2FShader,
            vrcLgtShader,
            vrcCrdShader,
            vrcPCShader,
            vrcClickCrdShader,
            vrcClickVoxelCrdShader,

            /* Colormaps        */
            chaoslab,
            hotbrightbands,
            brilliant,
            oygb,
            rainbowHotSpring,

            /* tica colormaps   */
            alpineColors,
            armyColors,
            atlanticColors,
            auroraColors,
            avacadoColors,
            beachColors,
            candyColors,
            cmykColors,
            deepSeaColors,
            fallColors,
            fruitPunchColors,
            islandColors,
            lakeColors,
            mintColors,
            neonColors,
            pearlColors,
            plumColors,
            roseColors,
            solarColors,
            southwestColors,
            starryNightColors,
            sunsetColors,
            thermometerColors,
            watermelonColors,
            brassTones,
            brownCyanTones,
            cherryTones,
            coffeeTones,
            fuchsiaTones,
            grayTones,
            greenPinkTones,
            pigeonTones,
            redBlueTones,
            rustTones,
            siennaTones,
            valentineTones,
            darkTerrain,
            greenBrownTerrain,
            lightTerrain,
            sandyTerrain,
            aquamarine,
            blueGreenYellow,
            brightBands,
            darkBands,
            darkRainbow,
            fuitPunch,
            lightTemperatureMap,
            pastel,
            rainbow,
            temperatureMap,

            /* mat colormaps    */
            autumn,
            blue,
            bone,
            colorcube,
            cool,
            copper,
            flag,
            gray,
            green,
            hot,
            hsv,
            jet,
            lines,
            parula,
            pink,
            prism,
            red,
            spring,
            summer,
            white,
            winter
            ){
/*========================================================================
 * version and update info
 *========================================================================
 */
var version = 'V2.7.01' ;
var updateTime = 'Mon 07 May 2018 05:33:07 PM EDT' ;

var log         = console.log ;
var warn        = console.warn ;

/*========================================================================
 * glMatrix variable import
 *========================================================================
 */
var mat2        = glMatrix.mat2 ;
var mat2d       = glMatrix.mat2d ;
var mat3        = glMatrix.mat3 ;
var mat4        = glMatrix.mat4 ;
var quat        = glMatrix.quat ;
var vec2        = glMatrix.vec2 ;
var vec3        = glMatrix.vec3 ;
var vec4        = glMatrix.vec4 ;

/*========================================================================
 * readOption
 *========================================================================
 */
function readOption(option, defaultValue, warning){
    if (option != undefined){
        return option ;
    }else{
        if (warning != undefined ){
            warn(warning) ;
            log('Warning was issued by "'+
                arguments.callee.caller.name+'"') ;
        }
        return defaultValue ;
    }
}

var readOptions = readOption ;

/*========================================================================
 * toUpperCase
 *========================================================================
 */
function toUpperCase(str){
    if ( str != undefined ){
        return str.toUpperCase() ;
    }else{
        return undefined ;
    }
}

/*========================================================================
 * readGlOption
 *========================================================================
 */
function readGlOption(str, defaultValue, warning ){
    if (str != undefined ){
        return gl[str.toUpperCase()] ;
    }else{
        if (warning != undefined ){
            warn(warning) ;
            log('Warning was issued by "'+
                arguments.callee.caller.name+'"') ;
        }
        return defaultValue ;
    }
}


/*========================================================================
 * OrbitalCameraControl
 *========================================================================
 */
function OrbitalCameraControl ( mViewMatrix,
                                mRadius = 5,
                                mListenerTarget = window,
                                opts={}) {
    const ANGLE_LIMIT = (Math.PI/2 - 0.01);
    const getCursorPos = function (e) {
        if(e.touches) {
            return {
                x:e.touches[0].pageX,
                y:e.touches[0].pageY
            };
        } else {
            return {
                x:e.clientX,
                y:e.clientY
            };
        }
    };

    this.up = vec3.fromValues(0,1,0) ;

    this._mtxTarget = mViewMatrix;
    this._radius = mRadius;
    this._targetRadius = mRadius;
    this._listenerTarget = mListenerTarget;
    this._isDown = false;
    this._rotation = mat4.create();
    this.center = vec3.create();

    this.easing = .5;
    this.senstivity = 1.0;
    this.senstivityRotation = .5;

    this._isLocked = false;
    this._isZoomLocked = false;
    this._rx = 0.0;
    this._trx = 0;
    this._ry = 0.0;
    this._try = 0;

    this._prevx = readOption( opts.prevx, 0 ) ;
    this._prevy = readOption( opts.prevy, 0 ) ;
    this.up     = readOption( opts.up, vec3.fromValues(0,1,0)) ;

    this._quat = quat.create();
    this._vec = vec3.create();
    this._mtx = mat4.create();


    this._mouseDown = {
        x:0,
        y:0
    };

    this._mouse = {
	x:0,
	y:0
    };



    this._init = function() {
        this._listenerTarget.addEventListener('mousedown',
                (e) => this._onDown(e));
        this._listenerTarget.addEventListener('mouseup',
                () => this._onUp());
        this._listenerTarget.addEventListener('mousemove',
                (e) => this._onMove(e));

        this._listenerTarget.addEventListener('touchstart',
                (e) => this._onDown(e));
        this._listenerTarget.addEventListener('touchend',
                () => this._onUp());
        this._listenerTarget.addEventListener('touchmove',
                (e) => this._onMove(e));

        this._listenerTarget.addEventListener('mousewheel',
                (e) => this._onWheel(e));
        this._listenerTarget.addEventListener('DOMMouseScroll',
                (e) => this._onWheel(e));
    }

    this._init();

    this.lock = function(mValue) {
        this._isLocked = mValue;
    }


    this.lockZoom = function(mValue) {
        this._isZoomLocked = mValue;
    }


    this._onWheel = function(e) {
        if ( e.ctrlKey || e.shiftKey || (e.which ==3)){
            return ;
        }
        if(this._isZoomLocked) {
            return;
        }
        const w = e.wheelDelta;
        const d = e.detail;
        let value = 0;
        if (d) {
            if (w) {
                value = w / d / 40 * d > 0 ? 1 : -1;
            } else {
                value = -d / 3;
            }
        } else {
            value = w / 120;
        }

        this._targetRadius += (-value * 2 * this.senstivity);
        if(this._targetRadius < 0.01) {
            this._targetRadius = 0.01;
        }
    }

    this._onDown = function(e) {
        if ( e.ctrlKey || e.shiftKey || (e.which ==3)){
            return ;
        }
        if(this._isLocked) {	return;	}
        this._isDown = true;

        this._mouseDown = getCursorPos(e);
        this._mouse = getCursorPos(e);

        this._prevx = this._trx = this._rx;
        this._prevy = this._try = this._ry;
    }

    this._onMove = function(e) {
        if (  e.ctrlKey || e.shiftKey || (e.which ==3) ){
            return ;
        }
        if(this._isLocked) {	return;	}
        if(!this._isDown)	{	return;	}
        this._mouse = getCursorPos(e);
    }

    this._onUp = function() {
        if(this._isLocked) {	return;	}
        this._isDown = false;
    }

/*-------------------------------------------------------------------------
 * update the mViewMatrix
 *-------------------------------------------------------------------------
 */
    this.update = function() {
        const dx = this._mouse.x - this._mouseDown.x;
        const dy = this._mouse.y - this._mouseDown.y;

        const senstivity = 0.02 * this.senstivityRotation;
        this._try = this._prevy - dx * senstivity;
        this._trx = this._prevx - dy * senstivity;

        this._trx = Math.max(this._trx,-ANGLE_LIMIT) ;
        this._trx = Math.min(this._trx, ANGLE_LIMIT) ;

        this._rx += (this._trx - this._rx) * this.easing ;
        this._ry += (this._try - this._ry) * this.easing ;
        this._radius += (this._targetRadius - this._radius) * this.easing;

        quat.identity(this._quat);
        quat.rotateY(this._quat, this._quat, this._ry);
        quat.rotateX(this._quat, this._quat, this._rx);

        vec3.set(this._vec, 0, 0, this._radius);
        vec3.transformQuat(this._vec, this._vec, this._quat);

        mat4.identity(this._mtx);
        mat4.lookAt(this._mtx, this._vec, this.center, this.up);

        if(this._mtxTarget) {
            mat4.copy(this._mtxTarget, this._mtx);
        }
    }
}

/*========================================================================
 * sourceDisp   :   used for displaying source with line numbers for
 *                  debugging purposes
 *========================================================================
 */
function sourceDisp(source){
    var lines = source.split('\n') ;

    for(var i=0; i<lines.length; i++){
        var j=  i+1 ;
        console.log(j.toString()+'\t',lines[i]);
    }
}

/*========================================================================
 * defined
 *========================================================================
 */
function defined(v){
    if (v != undefined ){
        return true ;
    }else{
        return false ;
    }
}

/*========================================================================
 * Create a computeGl context
 *========================================================================
 */
function ComputeGL(options={}){
    log('ComputeGL ', version );
    log('Updated on',updateTime) ;
    log('Copyright of Dr. A. Kaboudian!') ;
    this.canvas = document.createElement('canvas') ;
    this.width = 512 ;
    this.height = 512 ;
    this.extensions = {} ;
    this.dispCanvas = undefined ;

    this.width  = readOption(options.width, 512 ) ;
    this.height = readOption(options.height, 512 ) ;
    this.dispCanvas = readOption(options.canvas, this.canvas ) ;

    this.canvas.width = this.width ;
    this.canvas.height = this.height ;

    this.gl = this.canvas.getContext("webgl2") ;
    if (!this.gl){
        return ;
    }
    var gl = this.gl ;

    this.supportedExtensions = this.gl.getSupportedExtensions() ;
    gl.getExtension('EXT_color_buffer_float') ;
    gl.getExtension('OES_texture_float_linear') ;
    for(var i=0 ; i < this.supportedExtensions.length; i++ ){
            var ext = this.supportedExtensions[i] ;
            this.extensions[ext] = this.gl.getExtension(ext) ;
    }
}

var cgl = new ComputeGL();
var gl  = cgl.gl ;
gl.lastClickTime = -1e10 ;

/*========================================================================
 * createShader
 *========================================================================
 */
function createShader(type, source) {
    var shader = gl.createShader(type);
    gl.shaderSource(shader, source);
    gl.compileShader(shader);
    var success = gl.getShaderParameter(shader, gl.COMPILE_STATUS);
    var shaderInfoLog = gl.getShaderInfoLog(shader) ;
    if (shaderInfoLog.length > 0. ){
        sourceDisp(source) ;
        log(shaderInfoLog);  // eslint-disable-line
    }
    if (success) {
        return shader;
    }

    gl.deleteShader(shader);
    return undefined;
}

/*========================================================================
 * createProgram
 *========================================================================
 */
function createProgram(vertexShader, fragmentShader) {
    var program = gl.createProgram();
    gl.attachShader(program, vertexShader);
    gl.attachShader(program, fragmentShader);
    gl.linkProgram(program);
    var success = gl.getProgramParameter(program, gl.LINK_STATUS);
    if (success) {
        return program;
    }

    log(gl.getProgramInfoLog(program));  // eslint-disable-line
    gl.deleteProgram(program);
    return undefined;
}

/*========================================================================
 * FloatRenderTarget
 *========================================================================
 */
function FloatRenderTarget (w, h , options={}){
    this.gl         = cgl.gl ;
    this.texture    = gl.createTexture() ;
    this.width      = w ;
    this.height     = h ;

    this.data       = readOption(   options.data ,
                                    null                ) ;
    this.wrapS      = readGlOption( options.wrapS ,
                                    gl.CLAMP_TO_EDGE    ) ;
    this.wrapT      = readGlOption( options.wrapT ,
                                    gl.CLAMP_TO_EDGE    ) ;
    this.minFilter  = readGlOption( options.minFilter,
                                    gl.NEAREST          ) ;
    this.magFilter  = readGlOption( options.magFilter,
                                    gl.NEAREST          ) ;

/*------------------------------------------------------------------------
 * bind and set texture
 *------------------------------------------------------------------------
 */

    gl.bindTexture(     gl.TEXTURE_2D, this.texture     ) ;

    gl.texParameteri(   gl.TEXTURE_2D,
                        gl.TEXTURE_WRAP_S,
                        this.wrapS                      ) ;

    gl.texParameteri(   gl.TEXTURE_2D,
                        gl.TEXTURE_WRAP_T,
                        this.wrapT                      ) ;

    gl.texParameteri(   gl.TEXTURE_2D,
                        gl.TEXTURE_MIN_FILTER,
                        this.minFilter                  ) ;

    gl.texParameteri(   gl.TEXTURE_2D,
                        gl.TEXTURE_MAG_FILTER,
                        this.magFilter                  ) ;

    gl.texImage2D(      gl.TEXTURE_2D, 0 ,
                        gl.RGBA32F,
                        this.width, this.height, 0,
                        gl.RGBA,
                        gl.FLOAT,
                        this.data                       ) ;

    gl.bindTexture(     gl.TEXTURE_2D, null             ) ;

/*------------------------------------------------------------------------
 * setWrapS
 *------------------------------------------------------------------------
 */
    this.setWrapS = function(wrapS){
        this.wrapS = readGlOption(wrapS, this.wrapS ) ;
        gl.bindTexture(     gl.TEXTURE_2D, this.texture ) ;
        gl.texParameteri(   gl.TEXTURE_2D,
                            gl.TEXTURE_WRAP_S,
                            this.wrapS                  ) ;
        gl.bindTexture(     gl.TEXTURE_2D, null         ) ;
    }

/*------------------------------------------------------------------------
 * setWrapT
 *------------------------------------------------------------------------
 */
    this.setWrapT   = function(wrapT){
        this.wrapT = readGlOption(wrapT, this.wrapT ) ;
        gl.bindTexture(     gl.TEXTURE_2D, this.texture ) ;
        gl.texParameteri(   gl.TEXTURE_2D,
                            gl.TEXTURE_WRAP_T,
                            this.wrapT                  ) ;
        gl.bindTexture(     gl.TEXTURE_2D, null         ) ;
        return ;
    }

/*------------------------------------------------------------------------
 * setMinFilter
 *------------------------------------------------------------------------
 */
    this.setMinFilter = function(minFilter){
        this.minFilter = readOption(minFilter, this.minFilter ) ;
        gl.bindTexture(     gl.TEXTURE_2D, this.texture ) ;
        gl.texParameteri(   gl.TEXTURE_2D,
                            gl.TEXTURE_MIN_FILTER,
                            this.minFilter              ) ;
        gl.bindTexture(     gl.TEXTURE_2D, null         ) ;

    }

/*------------------------------------------------------------------------
 * setMagFilter
 *------------------------------------------------------------------------
 */
    this.setMagFilter = function(magFilter){
        this.magFilter = readOption(magFilter, this.magFilter ) ;
        gl.bindTexture(     gl.TEXTURE_2D, this.texture ) ;
        gl.texParameteri(   gl.TEXTURE_2D,
                            gl.TEXTURE_MAG_FILTER,
                            this.magFilter              ) ;
        gl.bindTexture(     gl.TEXTURE_2D, null         ) ;

    }

/*-------------------------------------------------------------------------
 * resize the target to new width and height
 *-------------------------------------------------------------------------
 */
    this.resize  = function( width, height ){
        var target = {} ;
        target.texture = this.texture ;
        target.width   = this.width ;
        target.height  = this.height ;
        this.temp = new FloatRenderTarget( this.width, this.height) ;
        copyTexture(target, this.temp ) ;

        this.width = width ;
        this.height = height ;
        gl.bindTexture(gl.TEXTURE_2D, this.texture) ;
        gl.texImage2D(  gl.TEXTURE_2D, 0 , gl.RGBA32F,
                        this.width,
                        this.height, 0, gl.RGBA, gl.FLOAT, null ) ;
        copyTexture(this.temp, target ) ;
    }

/*------------------------------------------------------------------------
 * updateData
 *------------------------------------------------------------------------
 */
    this.updateData = function( newData ){
        gl.bindTexture(gl.TEXTURE_2D, this.texture) ;

        this.data = readOption( newData, this.data ) ;
        gl.texImage2D( gl.TEXTURE_2D, 0 , gl.RGBA32F,
                    this.width, this.height, 0, gl.RGBA, gl.FLOAT,
                    this.data    ) ;
        gl.bindTexture(gl.TEXTURE_2D, null) ;
    }
}

/*========================================================================
 * ImageTexture
 *========================================================================
 */
function ImageTexture(Img){
    if ( Img.used ){
        log( 'Image is used once and cannot be re-used in the library. '
            +'Consider using the data from previous import, or '
            +'re-importing the image as a different resource!'  ) ;
        return null ;
    }

    Img.used = true ;

    this.width = Img.width ;
    this.height = Img.height ;
    this.image = Img ;
    this.cgl = cgl ;

    this.texture = gl.createTexture() ;
    gl.bindTexture(gl.TEXTURE_2D, this.texture) ;
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE );
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE );
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST   );
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST   );
    gl.pixelStorei( gl.UNPACK_FLIP_Y_WEBGL, true) ;
    gl.texImage2D(  gl.TEXTURE_2D, 0 , gl.RGBA32F,
                    this.width, this.height, 0, gl.RGBA, gl.FLOAT,
                    this.image ) ;

    gl.bindTexture(gl.TEXTURE_2D, null) ;

}

/*========================================================================
 * CanvasTexture( canvas )
 *========================================================================
 */
function CanvasTexture(canvas ){
    this.canvas = canvas ;
    this.cgl    = cgl ;
    this.width  = canvas.width ;
    this.height = canvas.height ;

    this.texture = gl.createTexture() ;
    gl.bindTexture(gl.TEXTURE_2D, this.texture) ;
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE );
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE );
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST   );
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST   );
    gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, true) ;
    gl.texImage2D( gl.TEXTURE_2D, 0 , gl.RGBA32F,
                    this.width, this.height, 0, gl.RGBA, gl.FLOAT,
                    this.canvas ) ;

    gl.bindTexture(gl.TEXTURE_2D, null) ;

/*------------------------------------------------------------------------
 * update
 *------------------------------------------------------------------------
 */
    this.update = function(){
        this.width = this.canvas.width ;
        this.height = this.canvas.height ;
        gl.bindTexture(gl.TEXTURE_2D, this.texture) ;
        gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, true) ;
        gl.texImage2D(  gl.TEXTURE_2D, 0 , gl.RGBA32F,
                        this.width, this.height, 0, gl.RGBA, gl.FLOAT,
                        this.canvas ) ;
        gl.bindTexture(gl.TEXTURE_2D, null) ;
    }
}



/*========================================================================
 * TableTexture
 *========================================================================
 */
function TableTexture( t, w, h=1, options ={} ){
    this.cgl = cgl ;
    this.width = w ;
    this.height = h ;
    this.size = this.width*this.height ;
    this.originalTable = t ;
    this.table = new Float32Array(t) ;

    this.minFilter  = readGlOption(options.minFilter, gl.LINEAR         ) ;
    this.magFilter  = readGlOption(options.magFilter, gl.LINEAR         ) ;
    this.wrapS      = readGlOption(options.wrapS    , gl.CLAMP_TO_EDGE  ) ;
    this.wrapT      = readGlOption(options.wrapT    , gl.CLAMP_TO_EDGE  ) ;

/*------------------------------------------------------------------------
 * Creating the texture
 *------------------------------------------------------------------------
 */
    this.texture = gl.createTexture() ;

    gl.bindTexture(     gl.TEXTURE_2D,
                        this.texture            ) ;

    gl.texParameteri(   gl.TEXTURE_2D,
                        gl.TEXTURE_WRAP_S,
                        this.wrapS              ) ;

    gl.texParameteri(   gl.TEXTURE_2D,
                        gl.TEXTURE_WRAP_T,
                        this.wrapT              ) ;

    gl.texParameteri(   gl.TEXTURE_2D,
                        gl.TEXTURE_MIN_FILTER,
                        this.minFilter          ) ;

    gl.texParameteri(   gl.TEXTURE_2D,
                        gl.TEXTURE_MAG_FILTER,
                        this.magFilter          );

    gl.texImage2D(      gl.TEXTURE_2D,
                        0 ,
                        gl.RGBA32F,
                        this.width,
                        this.height,
                        0,
                        gl.RGBA,
                        gl.FLOAT,
                        this.table              ) ;

    gl.bindTexture(     gl.TEXTURE_2D,
                        null                    ) ;

/*------------------------------------------------------------------------
 * setWrapS
 *------------------------------------------------------------------------
 */
    this.setWrapS = function(wrapS){
        this.wrapS = readGlOption(wrapS, this.wrapS ) ;
        gl.bindTexture(     gl.TEXTURE_2D, this.texture ) ;
        gl.texParameteri(   gl.TEXTURE_2D,
                            gl.TEXTURE_WRAP_S,
                            this.wrapS                  ) ;
        gl.bindTexture(     gl.TEXTURE_2D, null         ) ;
    }

/*------------------------------------------------------------------------
 * setWrapT
 *------------------------------------------------------------------------
 */
    this.setWrapT   = function(wrapT){
        this.wrapT = readGlOption(wrapT, this.wrapT ) ;
        gl.bindTexture(     gl.TEXTURE_2D, this.texture ) ;
        gl.texParameteri(   gl.TEXTURE_2D,
                            gl.TEXTURE_WRAP_T,
                            this.wrapT                  ) ;
        gl.bindTexture(     gl.TEXTURE_2D, null         ) ;
        return ;
    }

/*------------------------------------------------------------------------
 * setMinFilter
 *------------------------------------------------------------------------
 */
    this.setMinFilter = function(minFilter){
        this.minFilter = readOption(minFilter, this.minFilter ) ;
        gl.bindTexture(     gl.TEXTURE_2D, this.texture ) ;
        gl.texParameteri(   gl.TEXTURE_2D,
                            gl.TEXTURE_MIN_FILTER,
                            this.minFilter              ) ;
        gl.bindTexture(     gl.TEXTURE_2D, null         ) ;

    }

/*------------------------------------------------------------------------
 * setMagFilter
 *------------------------------------------------------------------------
 */
    this.setMagFilter = function(magFilter){
        this.magFilter = readOption(magFilter, this.magFilter ) ;
        gl.bindTexture(     gl.TEXTURE_2D, this.texture ) ;
        gl.texParameteri(   gl.TEXTURE_2D,
                            gl.TEXTURE_MAG_FILTER,
                            this.magFilter              ) ;
        gl.bindTexture(     gl.TEXTURE_2D, null         ) ;

    }

/*------------------------------------------------------------------------
 * updating the table
 *------------------------------------------------------------------------
 */
    this.update = function(utab){
        if (utab != undefined){
            this.originalTable = utab ;
            this.table = new Float32Array(utab) ;
        }else{
            this.table = new Float32Array(this.originalTable) ;
        }
        gl.bindTexture(gl.TEXTURE_2D, this.texture) ;

        gl.texImage2D( gl.TEXTURE_2D, 0 , gl.RGBA32F,
        this.width, this.height, 0, gl.RGBA, gl.FLOAT, this.table ) ;
        gl.bindTexture(gl.TEXTURE_2D, null) ;
    }
}

/*========================================================================
 * Copy
 *========================================================================
 */
function Copy(srcTarget, destTarget){
    return new Solver( {
            vertexShader : vertShader.value ,
            fragmentShader: wA2bShader.value ,
            uniforms : {
                map : {
                    type        : 's' ,
                    value       : srcTarget ,
                    minFilter   : 'linear',
                    magFilter   : 'linear' ,
                } ,
            } ,
            renderTargets : {
                FragColor : {
                    location    : 0 ,
                    target      : destTarget
                } ,
            }
    } ) ;
}

/*========================================================================
 * SparseData
 *========================================================================
 */
function SparseData(image, options={}){

    if (image == undefined){
        log( 'You need to provide image source for compression!') ;
        return null ;
    }

    if ( image.used ){
        log( 'Image is used once and cannot be re-used in the library. '
            +'Consider using the data from previous import, or '
            +'re-importing the image as a different resource!'  ) ;
        return null ;
    }

    image.used = true ;

    this.image      = image ;
    this.width      = this.image.width ;
    this.height     = this.image.height ;
    this.threshold  = readOption(   options.threshold, 0            ) ;
    this.threshold  = readOption(   options.compressionThreshold,
                                    this.threshold                  ) ;
    this.compressionThresholdChannel
                    = readOption(   options.channel,    'r'         ) ;

    switch (this.compressionThresholdChannel){
        case 'r' :
            this.channel = 0 ;
            break ;
        case 'g' :
            this.channel = 1 ;
            break ;
        case 'b' :
            this.channel = 2 ;
            break ;
        case 'a' :
            this.channel = 3 ;
            break ;
        default :
            this.channel = 0 ;
            break ;
    }

    this.canvas         = document.createElement('canvas') ;
    this.canvas.width   = this.width ;
    this.canvas.height  = this.height ;
    this.context        = this.canvas.getContext('2d') ;

    this.context.drawImage( this.image,
                            0,0,
                            this.width, this.height         ) ;

    this.odt       =
        this.context.getImageData(  0,0,
                                    this.width,this.height  ).data ;

    var dat         = new Float32Array(this.width*this.height*4) ;
    this.data       = new Float32Array(this.width*this.height*4) ;
    this.compThresholdData = new Float32Array(this.width*this.height) ;


/*------------------------------------------------------------------------
 * converting data to float
 *------------------------------------------------------------------------
 */
    for(var i=0 ; i< (this.width*this.height*4) ; i++){
        dat[i] = this.odt[i]/255.0 ;
    }
    delete this.odt ;

/*------------------------------------------------------------------------
 * flip-y   :   imported images have their data along y-flliped
 *------------------------------------------------------------------------
 */
    for(var j=0 ; j<this.height ; j++){
        for (var i=0 ; i <this.width; i++){
            var indx    = i + j*this.width ;
            var nindx   = i + this.width*( this.height-1-j) ;
            for (var k=0 ; k<4 ; k++){
                this.data[nindx*4+k] = dat[indx*4+k] ;
            }
        }
    }

    delete dat ;

/*------------------------------------------------------------------------
 * count number of pixels above the compression threshold
 *------------------------------------------------------------------------
 */
    this.noAboveThreshold = 0 ;
    for(var j=0 ; j<this.height ; j++){
        for (var i=0 ; i <this.width; i++){
            var indx    = i + j*this.width ;
            this.compThresholdData[indx]
                    = this.data[indx*4 + this.channel] ;
            if (this.compThresholdData[indx]>this.threshold){
                    this.noAboveThreshold++ ;
            }
        }
    }

/*------------------------------------------------------------------------
 * allocating memory to data
 *------------------------------------------------------------------------
 */
    this.compressedSize    =
        Math.ceil( Math.sqrt( this.noAboveThreshold )) ;

    this.compressedTable =
        new Float32Array(this.compressedSize * this.compressedSize * 4 ) ;
    this.decompressionMapTable =
        new Float32Array(this.compressedSize * this.compressedSize * 4 ) ;
    this.compressionMapTable =
        new Float32Array(this.width * this.height * 4 ) ;

/*------------------------------------------------------------------------
 * compress data
 *------------------------------------------------------------------------
 */
    var num = 0 ;
    for(var j=0 ; j<this.height ; j++){
        for (var i=0 ; i <this.width; i++){
            var indx    = i + j*this.width ;
            if (this.compThresholdData[indx]>this.threshold){
                var jj  = Math.floor( num/this.compressedSize) ;
                var ii  = num - jj*this.compressedSize ;

                var x   = ii/this.compressedSize
                        + 0.5/this.compressedSize ;
                var y   = jj/this.compressedSize
                        + 0.5/this.compressedSize ;

                var nindx = ii + jj*this.compressedSize ;

                this.compressionMapTable[indx*4     ]   = x ;
                this.compressionMapTable[indx*4 + 1 ]   = y ;
                this.decompressionMapTable[nindx*4  ]   =
                    i/this.width + 0.5/this.width ;
                this.decompressionMapTable[nindx*4+1]   =
                    j/this.height+ 0.5/this.height ;

                for (var k = 0 ; k<4 ; k++){
                    this.compressedTable[nindx*4+k]
                        = this.data[indx*4+k] ;
                }
                num++ ;
            }else{
                this.compressionMapTable[indx*4     ]
                    = 1.-0.5/this.compressedSize ;
                this.compressionMapTable[indx*4 + 1 ]
                    = 1.-0.5/this.compressedSize ;
            }

        }
    }
    var ii = this.compressedSize -1 ;
    var jj = this.compressedSize -1 ;
    var nindx = ii + jj*this.compressedSize ;
    for (var k = 0 ; k<4 ; k++){
        this.compressedTable[nindx*4+k] = 0. ;
    }

/*------------------------------------------------------------------------
 * setting compressedData, compressionMap, decompressionMap textures
 *------------------------------------------------------------------------
 */
    this.full   = new TableTexture(
        this.data,
        this.width,
        this.height,
        {
            minFilter : 'nearest' ,
            magFilter : 'nearest'
        }
    ) ;

    this.sparse = new TableTexture(
        this.compressedTable,
        this.compressedSize ,
        this.compressedSize ,
        {
            minFilter : 'nearest' ,
            magFilter : 'nearest'
        }
    ) ;

    this.compressionMap     = new TableTexture(
        this.compressionMapTable,
        this.width,
        this.height ,
        {
            minFilter : 'nearest' ,
            magFilter : 'nearest'
        }
    ) ;

    this.decompressionMap   = new TableTexture(
        this.decompressionMapTable ,
        this.compressedSize ,
        this.compressedSize ,
        {
            minFilter : 'nearest' ,
            magFilter : 'nearest'
        }
    ) ;

/*------------------------------------------------------------------------
 * getCompressionRatio
 *------------------------------------------------------------------------
 */
    this.getCompressionRatio = function(){
        return (    this.compressedSize*this.compressedSize/
                    (this.width*this.height)                ) ;
    }

/*------------------------------------------------------------------------
 * getCompressionEfficiency
 *------------------------------------------------------------------------
 */
    this.getCompressionEfficiency = function(){
        return (    this.noAboveThreshold /
                    (this.compressedSize*this.compressedSize)   ) ;
    }


}



/*========================================================================
 * copyTexture
 *========================================================================
 */
function copyTexture(srcTarget, destTarget){
    var copy = new Copy( srcTarget, destTarget ) ;
    copy.render() ;
    copy.delete() ;
    return ;
}

/*========================================================================
 * Solver
 *========================================================================
 */
function Solver( options={} ){
    this.cgl = cgl ;
    this.gl = cgl.gl ;
    this.noRenderTargets = 0 ;
    this.noUniforms = 0 ;
    this.noTextureUniforms = 0 ;
    this.textureUniforms = {} ;
    this.uniforms = {} ;
    this.canvasTarget = false ;
    this.canvas = gl.canvas ;

    this.renderTargets = {} ;
    this.renderTargetNames = [] ;
    this.drawBuffers = [] ;
    this.framebuffer = null ;

    if (options == undefined ){
        delete this ;
        return ;
    }

/*------------------------------------------------------------------------
 * clear
 *------------------------------------------------------------------------
 */
    this.clear      = readOption(options.clear,         true        ) ;
    this.clearColor = readOption(options.clearColor,    [0,0,0,0]   ) ;

/*------------------------------------------------------------------------
 * vertexShader
 *------------------------------------------------------------------------
 */
    this.vertexShaderSrc = readOption( options.vertexShader, null   ) ;
    if ( this.vertexShaderSrc == null ){
        delete this ;
        return ;
    }
    this.vertexShader =
            createShader(gl.VERTEX_SHADER, this.vertexShaderSrc ) ;

/*------------------------------------------------------------------------
 * fragmentShader
 *------------------------------------------------------------------------
 */

    if ( options.fragmentShader != undefined ){
        this.fragmentShaderSrc = options.fragmentShader ;
        this.fragmentShader =
            createShader(gl.FRAGMENT_SHADER, this.fragmentShaderSrc ) ;
    }else{
        delete this ;
        return ;
    }
/*------------------------------------------------------------------------
 * depth and cullFacing
 *------------------------------------------------------------------------
 */
    this.cullFacing = readOption( options.cullFacing, false ) ;
    this.cullFace   = readGlOption( options.cullFace, gl.BACK ) ;
    this.depthTest  = readOption( options.depthTest, false ) ;

/*------------------------------------------------------------------------
 * Program
 *------------------------------------------------------------------------
 */
    this.prog =
        createProgram( this.vertexShader, this.fragmentShader ) ;
    gl.useProgram(this.prog) ;

/*------------------------------------------------------------------------
 * geometry
 *------------------------------------------------------------------------
 */
    this.geometry = {} ;
    this.geometry.vertices =  [
        1.,1.,0.,
        0.,1.,0.,
        1.,0.,0.,
        0.,0.,0.,
    ] ;
    this.geometry.noVertices= 4 ;
    this.geometry.noCoords  = 3 ;
    this.geometry.type      = gl.FLOAT ;
    this.geometry.normalize = false ;
    this.geometry.stride    = 0 ;
    this.geometry.offset    = 0 ;
    this.geometry.premitive = gl.TRIANGLE_STRIP ;
    this.geometry.width = 1 ;

    if ( options.geometry != undefined ){
        this.geometry.vertices =
            readOption( options.geometry.vertices, null ) ;
        if (this.geometry.vertices == null ){
            warn(       'Error: The passed geometry has no vertices! '
                    +   'No solver can be defined!'                 ) ;
            delete this ;
            return null ;
        }
        this.geometry.noCoords = readOptions(
            options.geometry.noCoords ,  3
        ) ;

        this.geometry.noVertices = readOptions(
            options.geometry.noVertices ,
            this.geometry.vertices.length
                    /this.geometry.noCoords
        ) ;
        this.geometry.normalize = readOption(
            options.geometry.normalize ,
            false
        ) ;
        this.geometry.premitive = readGlOption(
            options.geometry.premitive ,
            gl.TRIANGLE_STRIP
        ) ;
        this.geometry.width = readOption(
            options.geometry.width,
            1
        ) ;
    }

/*------------------------------------------------------------------------
 * Creating the position vector
 *------------------------------------------------------------------------
 */
    this.positionLoc = gl.getAttribLocation(this.prog, "position") ;
    this.positionBuffer = gl.createBuffer() ;
    gl.bindBuffer(
        gl.ARRAY_BUFFER,
        this.positionBuffer
    ) ;
    gl.bufferData(
        gl.ARRAY_BUFFER,
        new Float32Array(this.geometry.vertices),
        gl.STATIC_DRAW
    );
    this.vao = gl.createVertexArray() ;
    gl.bindVertexArray(this.vao) ;
    gl.enableVertexAttribArray(this.positionLoc) ;

    gl.vertexAttribPointer(
        this.positionLoc ,
        this.geometry.noCoords ,
        this.geometry.type ,
        this.geometry.normalize ,
        this.geometry.stride ,
        this.geometry.offset
    ) ;

    gl.bindBuffer(gl.ARRAY_BUFFER, null) ;
    gl.bindVertexArray(null) ;

/*------------------------------------------------------------------------
 * framebuffer
 *------------------------------------------------------------------------
 */
    /* creating framebuffers for renderTargetOutput */
    if ( options.targets != undefined ){
        options.renderTargets = options.targets  ;
    }

    if ( options.renderTargets != undefined ){
        this.framebuffer = gl.createFramebuffer() ;
        gl.bindFramebuffer(gl.DRAW_FRAMEBUFFER,this.framebuffer) ;
        for (var tName in options.renderTargets){
            this.noRenderTargets++ ;
            var rTarget = options.renderTargets[tName] ;
            this.renderTargetNames.push(tName) ;
            this.renderTargets[tName] = rTarget ;
            var loc = rTarget.location ;
            var tgt = rTarget.target ;

            this.drawBuffers.push(gl.COLOR_ATTACHMENT0+loc) ;

            gl.framebufferTexture2D(
                gl.DRAW_FRAMEBUFFER,
                gl.COLOR_ATTACHMENT0+loc,
                gl.TEXTURE_2D,
                tgt.texture,
                0
            ) ;

        }
        gl.drawBuffers(this.drawBuffers) ;

        var status = gl.checkFramebufferStatus(gl.DRAW_FRAMEBUFFER) ;
        if (status != gl.FRAMEBUFFER_COMPLETE) {
            console.log('fb status: ' + status);
        }
        gl.bindFramebuffer(gl.DRAW_FRAMEBUFFER,null) ;
    }

/*------------------------------------------------------------------------
 * Setting up uniforms
 *------------------------------------------------------------------------
 */
    if (options.uniforms != undefined ){
        for(var uname in options.uniforms ){
            var uniform = options.uniforms[uname] ;
            var value   = uniform.value ;
            var type = uniform.type ;
            this.noUniforms += 1 ;
            this.uniforms[uname] = {} ;
            this.uniforms[uname].value = value ;
            this.uniforms[uname].type  = type ;
            this.uniforms[uname].location =
            gl.getUniformLocation(this.prog, uname )  ;
            var location = this.uniforms[uname].location ;
            switch (type){
                case 't' :  /* texture */
                    var activeNumber =  this.noTextureUniforms ;
                    this.uniforms[uname].activeNumber = activeNumber ;
                    gl.uniform1i(
                        this.uniforms[uname].location ,
                        activeNumber
                    ) ;
                    gl.activeTexture(
                        gl.TEXTURE0+activeNumber
                    ) ;
                    gl.bindTexture(
                        gl.TEXTURE_2D,
                        this.uniforms[uname].value.texture
                    ) ;
                    this.noTextureUniforms += 1 ;
                    this.textureUniforms[uname] = this.uniforms[uname] ;
                    break ;
                case 's' :
                    var activeNumber =  this.noTextureUniforms ;
                    var sampler = gl.createSampler() ;

                    this.uniforms[uname].sampler    = sampler ;

                    this.uniforms[uname].wrapS      =
                        readGlOption(
                            uniform.wrapS,
                            gl.CLAMP_TO_EDGE )
                        ;
                    this.uniforms[uname].wrapT      =
                        readGlOption(
                            uniform.wrapT,
                            gl.CLAMP_TO_EDGE
                        ) ;
                    this.uniforms[uname].minFilter  =
                        readGlOption(
                            uniform.minFilter,
                            gl.NEAREST
                        ) ;
                    this.uniforms[uname].magFilter  =
                        readGlOption(
                            uniform.magFilter,
                            gl.NEAREST
                        ) ;

                    gl.samplerParameteri(
                        sampler,
                        gl.TEXTURE_MIN_FILTER,
                        this.uniforms[uname].minFilter
                    ) ;

                    gl.samplerParameteri(
                        sampler, gl.TEXTURE_MAG_FILTER,
                        this.uniforms[uname].magFilter
                    ) ;

                    gl.samplerParameteri(
                        sampler,
                        gl.TEXTURE_WRAP_S,
                        this.uniforms[uname].wrapS
                    ) ;

                    gl.samplerParameteri(
                        sampler,
                        gl.TEXTURE_WRAP_T,
                        this.uniforms[uname].wrapT
                    ) ;

                    this.uniforms[uname].activeNumber = activeNumber ;

                    gl.uniform1i(
                        this.uniforms[uname].location ,
                        activeNumber
                    ) ;
                    gl.activeTexture(
                        gl.TEXTURE0+activeNumber
                    ) ;
                    gl.bindTexture(
                        gl.TEXTURE_2D,
                        this.uniforms[uname].value.texture
                    ) ;
                    gl.bindSampler(
                            activeNumber,
                            sampler
                    ) ;

                    this.noTextureUniforms += 1 ;
                    this.textureUniforms[uname] = this.uniforms[uname] ;

                    break ;
                case 'b' :  /* boolean */
                    gl.uniform1i(
                        location ,
                        value
                    ) ;
                    break ;
                case 'i' :  /* integer */
                    gl.uniform1i(
                        location ,
                        value
                    ) ;
                    break ;

                case 'iv' : /* 1-dimensional integer array  */
                    gl.uniform1iv(
                        location ,
                        value
                    ) ;
                    break ;

                case 'i2' : /* 2-dimensional integer vector */
                    gl.uniform2i(
                        location ,
                        value[0],
                        value[1]
                    ) ;
                    break ;

                case 'i2v': /* 2-dimensional integer array  */
                    gl.uniform2iv(
                        location ,
                        value
                    ) ;
                    break ;

                case 'i3' : /* 3-dimensional integer vector */
                    gl.uniform3i(
                        location ,
                        value[0],
                        value[1],
                        value[2]
                    ) ;
                    break ;

                case 'i3v': /* 3-dimensional integer array  */
                    gl.uniform3iv(
                        location ,
                        value
                    ) ;
                    break ;

                case 'i4' :  /* 4-dimensional integer vector */
                    gl.uniform4i(
                        location ,
                        value[0],
                        value[1],
                        value[2],
                        value[3]
                    ) ;
                    break ;

                case 'i4v' : /* 4-dimensional integer array  */
                    gl.uniform4iv(
                        location ,
                        value
                    ) ;
                    break ;

                case 'f' :  /* float */
                    gl.uniform1f(
                        location ,
                        value
                    ) ;
                    break ;

                case 'fv' : /* 1-dimensional float array    */
                    gl.uniform1fv(
                        location,
                        value
                    ) ;
                    break ;

                case 'v2' : /* 2-dimensional float vector   */
                    gl.uniform2f(
                        location,
                        value[0],
                        value[1]
                    ) ;
                    break ;
                case 'f2' : /* 2-dimensional float vector   */
                    gl.uniform2f(
                        location,
                        value[0],
                        value[1]
                    ) ;
                    break ;

                case 'v2v' : /* 2-dimensional float array   */
                    gl.uniform2fv(
                        location ,
                        value
                    ) ;
                    break ;
                case 'f2v' : /* 2-dimensional float array   */
                    gl.uniform2fv(
                        location ,
                        value
                    ) ;
                    break ;

                case 'v3' : /* 3-dimensional float vector   */
                    gl.uniform3f(
                        location,
                        value[0],
                        value[1],
                        value[2]
                    ) ;
                    break ;
                case 'f3' : /* 3-dimensional float vector   */
                    gl.uniform3f(
                        location,
                        value[0],
                        value[1],
                        value[2]
                    ) ;
                    break ;

                case 'v3v': /* 3-dimensional float array    */
                    gl.uniform3fv(  location,   value               ) ;
                    break ;
                case 'f3v': /* 3-dimensional float array    */
                    gl.uniform3fv(  location,   value               ) ;
                    break ;

                case 'v4' : /* 4-dimensional float vector   */
                    gl.uniform4f(
                        location,
                        value[0],
                        value[1],
                        value[2],
                        value[3]
                    ) ;
                    break ;
                case 'f4' : /* 4-dimensional float vector   */
                    gl.uniform4f(
                        location,
                        value[0],
                        value[1],
                        value[2],
                        value[3]
                    ) ;
                    break ;

                case 'v4v': /* 4-dimensional float array    */
                    gl.uniform4fv(
                        location,
                        value
                    ) ;
                    break ;
                case 'f4v': /* 4-dimensional float array    */
                    gl.uniform4fv(
                        location,
                        value
                    ) ;
                    break ;

                case 'mat2': /* 2x2 floating point matrix   */
                    gl.uniformMatrix2fv(
                        location,
                        gl.FLASE,
                        value
                    ) ;
                    break ;

                case 'mat3': /* 3x3 floating point matrix   */
                    gl.uniformMatrix3fv(
                        location,
                        gl.FLASE,
                        value
                    ) ;
                    break ;

                case 'mat4': /* 4x4 floating point matrix   */
                    gl.uniformMatrix4fv(
                        location,
                        gl.FLASE,
                        value
                    ) ;
                    break ;
            }
        }
    }

/*------------------------------------------------------------------------
 * setUniform
 *------------------------------------------------------------------------
 */
    this.setUniform = function(uname, value ){
        gl.useProgram(this.prog) ;
        var uniform     = this.uniforms[uname] ;
        uniform.value = readOption(
            value,
            uniform.value
        ) ;
        value = uniform.value ;
        var location = this.uniforms[uname].location ;
        var type        = uniform.type ;
        switch (type){
            case 't' :  /* texture */
                gl.activeTexture(
                    gl.TEXTURE0+uniform.activeNumber) ;
                gl.bindTexture(
                    gl.TEXTURE_2D,
                    uniform.value.texture
                ) ;
                break ;
            case 's' :
                gl.uniform1i(
                    location ,
                    uniform.activeNumber
                ) ;
                gl.activeTexture(
                    gl.TEXTURE0+activeNumber
                ) ;
                gl.bindTexture(
                    gl.TEXTURE_2D,
                    uniform.value.texture
                ) ;
                gl.bindSampler(
                    uniform.activeNumber,
                    uniform.sampler
                ) ;
                break ;
            case 'b' :  /* boolean */
                    gl.uniform1i(
                        location ,
                        value
                    ) ;
                    break ;
                case 'i' :  /* integer */
                    gl.uniform1i(
                        location ,
                        value
                    ) ;
                    break ;

                case 'iv' : /* 1-dimensional integer array  */
                    gl.uniform1iv(
                        location ,
                        value
                    ) ;
                    break ;

                case 'i2' : /* 2-dimensional integer vector */
                    gl.uniform2i(
                        location ,
                        value[0],
                        value[1]
                    ) ;
                    break ;

                case 'i2v': /* 2-dimensional integer array  */
                    gl.uniform2iv(
                        location ,
                        value
                    ) ;
                    break ;

                case 'i3' : /* 3-dimensional integer vector */
                    gl.uniform3i(
                        location ,
                        value[0],
                        value[1],
                        value[2]
                    ) ;
                    break ;

                case 'i3v': /* 3-dimensional integer array  */
                    gl.uniform3iv(
                        location ,
                        value
                    ) ;
                    break ;

                case 'i4' :  /* 4-dimensional integer vector */
                    gl.uniform4i(
                        location ,
                        value[0],
                        value[1],
                        value[2],
                        value[3]
                    ) ;
                    break ;

                case 'i4v' : /* 4-dimensional integer array  */
                    gl.uniform4iv(
                        location ,
                        value
                    ) ;
                    break ;

                case 'f' :  /* float */
                    gl.uniform1f(
                        location ,
                        value
                    ) ;
                    break ;

                case 'fv' : /* 1-dimensional float array    */
                    gl.uniform1fv(
                        location,
                        value
                    ) ;
                    break ;

                case 'v2' : /* 2-dimensional float vector   */
                    gl.uniform2f(
                        location,
                        value[0],
                        value[1]
                    ) ;
                    break ;
                case 'f2' : /* 2-dimensional float vector   */
                    gl.uniform2f(
                        location,
                        value[0],
                        value[1]
                    ) ;
                    break ;

                case 'v2v' : /* 2-dimensional float array   */
                    gl.uniform2fv(
                        location ,
                        value
                    ) ;
                    break ;
                case 'f2v' : /* 2-dimensional float array   */
                    gl.uniform2fv(
                        location ,
                        value
                    ) ;
                    break ;

                case 'v3' : /* 3-dimensional float vector   */
                    gl.uniform3f(
                        location,
                        value[0],
                        value[1],
                        value[2]
                    ) ;
                    break ;
                case 'f3' : /* 3-dimensional float vector   */
                    gl.uniform3f(
                        location,
                        value[0],
                        value[1],
                        value[2]
                    ) ;
                    break ;

                case 'v3v': /* 3-dimensional float array    */
                    gl.uniform3fv(  location,   value               ) ;
                    break ;
                case 'f3v': /* 3-dimensional float array    */
                    gl.uniform3fv(  location,   value               ) ;
                    break ;

                case 'v4' : /* 4-dimensional float vector   */
                    gl.uniform4f(
                        location,
                        value[0],
                        value[1],
                        value[2],
                        value[3]
                    ) ;
                    break ;
                case 'f4' : /* 4-dimensional float vector   */
                    gl.uniform4f(
                        location,
                        value[0],
                        value[1],
                        value[2],
                        value[3]
                    ) ;
                    break ;

                case 'v4v': /* 4-dimensional float array    */
                    gl.uniform4fv(
                        location,
                        value
                    ) ;
                    break ;
                case 'f4v': /* 4-dimensional float array    */
                    gl.uniform4fv(
                        location,
                        value
                    ) ;
                    break ;

                case 'mat2': /* 2x2 floating point matrix   */
                    gl.uniformMatrix2fv(
                        location,
                        gl.FLASE,
                        value
                    ) ;
                    break ;

                case 'mat3': /* 3x3 floating point matrix   */
                    gl.uniformMatrix3fv(
                        location,
                        gl.FLASE,
                        value
                    ) ;
                    break ;

                case 'mat4': /* 4x4 floating point matrix   */
                    gl.uniformMatrix4fv(
                        location,
                        gl.FLASE,
                        value
                    ) ;
                    break ;
        }
    }

/*------------------------------------------------------------------------
 * setSamplerMinFilter
 *------------------------------------------------------------------------
 */
    this.setSamplerMinFilter = function( uname, minFilter ){
        var uniform = this.uniforms[uname] ;
        if (uniform == undefined) return ;
        uniform.minFilter = readGlOption( minFilter, gl.NEAREST ) ;

        this.setUniform(uname) ;
    }

/*------------------------------------------------------------------------
 * setSamplerMagFilter
 *------------------------------------------------------------------------
 */
    this.setSamplerMagFilter = function( uname, magFilter ){
        var uniform = this.uniforms[uname] ;
        if (uniform == undefined) return ;
        uniform.magFilter = readGlOption( magFilter, gl.NEAREST ) ;
        this.setUniform(uname) ;
    }

/*------------------------------------------------------------------------
 * setSamplerWrapS
 *------------------------------------------------------------------------
 */
    this.setSamplerWrapS = function( uname, wrapS ){
        var uniform = this.uniforms[uname] ;
        if (uniform == undefined ) return ;
        uniform.wrapS = readGlOption( wrapS, gl.CLAMP_TO_EDGE ) ;
        this.setUniform(uname) ;
    }

/*------------------------------------------------------------------------
 * setSamplerWrapT
 *------------------------------------------------------------------------
 */
    this.setSamplerWrapT = function( uname, wrapT ){
        var uniform = this.uniforms[uname] ;
        if (uniform == undefined ) return ;
        uniform.wrapT = readGlOption( wrapT, gl.CLAMP_TO_EDGE ) ;
        this.setUniform(uname) ;

        this.setUniform(uname) ;
    }

/*------------------------------------------------------------------------
 * setRenderTarget
 *------------------------------------------------------------------------
 */
    this.setRenderTarget= function(tName, target){
        this.renderTargets[tName].target = target ;
        var loc = this.renderTargets[tName].location ;
        gl.bindFramebuffer(
            gl.DRAW_FRAMEBUFFER,
            this.framebuffer
        ) ;
        gl.framebufferTexture2D(
            gl.DRAW_FRAMEBUFFER,
            gl.COLOR_ATTACHMENT0+loc,
            gl.TEXTURE_2D,
            this.renderTargets[tName].target.texture,
            0
        ) ;

        gl.bindFramebuffer(
            gl.DRAW_FRAMEBUFFER,
            null
        ) ;
    }

/*------------------------------------------------------------------------
 * canvas
 *------------------------------------------------------------------------
 */
    if (options.canvas != undefined ){
        this.canvas = options.canvas ;
        this.canvasTarget = true ;
        this.context = this.canvas.getContext('2d') ;
    }

    if ((this.canvasTarget == false)&&(this.framebuffer == null)){
        if (this.canvas != undefined ){
            this.context = this.canvas.getContext('2d') ;
        }
    }

/*------------------------------------------------------------------------
 * render
 *------------------------------------------------------------------------
 */
    this.render = function(renderOptions){
        gl.useProgram(this.prog) ;
        if ( this.depthTest ){
            gl.enable(gl.DEPTH_TEST);
            gl.clear(gl.DEPTH_BUFFER_BIT);
        }else{
            gl.disable(gl.DEPTH_TEST) ;
        }

        if ( this.cullFacing ){
            gl.enable(gl.CULL_FACE);
            gl.cullFace(this.cullFace);
        }else{
            gl.disable(gl.CULL_FACE) ;
        }
        if ( this.noTextureUniform < 1){
            gl.activeTexture( gl.TEXTURE0 ) ;
            gl.bindTexture( gl.TEXTURE_2D, null ) ;
        }else{
           // gl.enable( gl.TEXTURE_2D ) ;
        }

        /* binding textures and color attachments */
        for ( var tName in this.textureUniforms ){
            var activeNumber = this.textureUniforms[tName].activeNumber ;
            gl.activeTexture(
                gl.TEXTURE0+activeNumber
            ) ;
            gl.bindTexture(
                gl.TEXTURE_2D,
                this.textureUniforms[tName].value.texture
            );
            if (this.textureUniforms[tName].sampler){
                gl.bindSampler(
                    this.textureUniforms[tName].activeNumber,
                    this.textureUniforms[tName].sampler
                ) ;
            }
        }

        if ( this.noRenderTargets < 1 ){
            if ((this.canvas.width != gl.canvas.width)||
                (this.canvas.height != gl.canvas.height)){
                gl.canvas.width  = this.canvas.width ;
                gl.canvas.height = this.canvas.height ;
            }
            gl.viewport(0,0,this.canvas.width, this.canvas.height) ;
        }else{
            var tName = this.renderTargetNames[0] ;
            var target = this.renderTargets[tName].target ;
            gl.viewport(0,0,target.width,target.height) ;
        }
        gl.bindFramebuffer(gl.DRAW_FRAMEBUFFER, null);
        if (this.clear){
            gl.clearColor(
                this.clearColor[0],
                this.clearColor[1],
                this.clearColor[2],
                this.clearColor[3]
            );
            gl.clear(gl.COLOR_BUFFER_BIT);
        }

        if (this.noRenderTargets < 1){
            gl.bindFramebuffer(gl.DRAW_FRAMEBUFFER, null);

            if (this.clear){
                gl.clearColor(
                    this.clearColor[0],
                    this.clearColor[1],
                    this.clearColor[2],
                    this.clearColor[3]
                );
                gl.clear(gl.COLOR_BUFFER_BIT);
            }
        }else{
            gl.bindFramebuffer(gl.DRAW_FRAMEBUFFER, this.framebuffer ) ;
            for ( var tName in this.renderTargets ){
                var rTarget = this.renderTargets[tName] ;
                var loc = rTarget.location ;
                var tgt = rTarget.target ;
                gl.framebufferTexture2D(
                        gl.DRAW_FRAMEBUFFER,
                        gl.COLOR_ATTACHMENT0+loc,
                        gl.TEXTURE_2D,
                        tgt.texture, 0              ) ;
            }
            gl.drawBuffers(this.drawBuffers) ;
        }
        gl.bindVertexArray(this.vao) ;
        gl.lineWidth(this.geometry.width) ;
        gl.drawArrays(  this.geometry.premitive ,
                        this.geometry.offset ,
                        this.geometry.noVertices    );

        if ( this.canvasTarget ){
            if (this.clear){
                this.context.clearRect(
                    0,
                    0,
                    this.canvas.width,
                    this.canvas.height
                ) ;
            }
            this.context.drawImage(
                gl.canvas,
                0,
                0,
                this.canvas.width,
                this.canvas.height
            ) ;
        }
    }

/*------------------------------------------------------------------------
 * delete
 *------------------------------------------------------------------------
 */
    this.delete = function(){
        gl.deleteProgram(this.program) ;
        gl.deleteShader(this.vertexShader) ;
        gl.deleteShader(this.fragmentShader) ;
        gl.deleteBuffer(this.positionBuffer) ;
        gl.deleteFramebuffer(this.framebuffer) ;
        delete this ;
        return ;
    }

    return this ;
}

/*========================================================================
 * LineGeometry
 *========================================================================
 */
function LineGeometry(noPltPoints){
    var line = {} ;
    line.vertices = [] ;
    for (var i=0; i<noPltPoints ; i++ ){
        line.vertices.push( 0.5/noPltPoints+i/noPltPoints,0.5,0) ;
    }
    line.premitive = 'line_strip' ;
    line.noCoords = 3 ;
    line.width = 1 ;
    return line ;
}

/*========================================================================
 * UnitCubeGeometry     :   Constructor for a unit cube geometry
 *                          where x, y, and z line in [0,1]
 *========================================================================
 */
function UnitCubeGeometry(){
    this.vertices = [
        /* ~~~~~~~~~~~~~~~~ */
        /* Front PLANE      */
        /* ~~~~~~~~~~~~~~~~ */
        // 1F
        0,0,1,  // 1
        1,0,1,  // 2
        0,1,1,  // 4

        // 2F
        0,1,1,  // 4
        1,0,1,  // 2
        1,1,1,  // 3

        /* ~~~~~~~~~~~~~~~~ */
        /* RIGHT PLANE      */
        /* ~~~~~~~~~~~~~~~~ */
        // 3R
        1,1,1,  // 3
        1,0,1,  // 2
        1,1,0,  // 7

        // 4R
        1,1,0,  // 7
        1,0,1,  // 2
        1,0,0,  // 5

        /* ~~~~~~~~~~~~~~~~ */
        /* BOTTOM PLANE     */
        /* ~~~~~~~~~~~~~~~~ */
        // 5B
        1,0,0,  // 5
        1,0,1,  // 2
        0,0,0,  // 6

        // 6B
        0,0,0,  // 6
        1,0,1,  // 2
        0,0,1,  // 1

        /* ~~~~~~~~~~~~~~~~ */
        /* LEFT PLANE       */
        /* ~~~~~~~~~~~~~~~~ */
        // 7L
        0,0,1,  // 1
        0,1,1,  // 4
        0,0,0,  // 6

        // 8L
        0,0,0,  // 6
        0,1,1,  // 4
        0,1,0,  // 8

        /* ~~~~~~~~~~~~~~~~ */
        /* TOP PLANE        */
        /* ~~~~~~~~~~~~~~~~ */
        // 9T
        0,1,0,  // 8
        0,1,1,  // 4
        1,1,1,  // 3

        // 10T
        1,1,1,  // 3
        1,1,0,  // 7
        0,1,0,  // 8

        /* ~~~~~~~~~~~~~~~~ */
        /* BACK PLANE       */
        /* ~~~~~~~~~~~~~~~~ */
        // 11B
        0,1,0,  // 8
        1,1,0,  // 7
        0,0,0,  // 6

        // 12B
        0,0,0,  // 6
        1,1,0,  // 7
        1,0,0,  // 5
    ] ;

    this.noCoords = 3 ;
    this.premitive = 'triangles' ;
}


/*========================================================================
 * Get Channel Multiplier
 *========================================================================
 */
function getChannelMultiplier(cnl){
    var mltplier = [0,0,0,0] ;
    switch (cnl){
        case 'r':
            mltplier[0]=1 ;
            break ;
        case 'g':
            mltplier[1]=1 ;
            break ;
        case 'b':
            mltplier[2]=1 ;
            break ;
        case 'a':
            mltplier[3]=1 ;
            break ;
        default:
            mltplier[0]=1 ;
            break ;
    }
    return mltplier  ;
}

/*========================================================================
 * Signal       : signal structure
 * renderer     : renderer to be used to render the signal
 * camera       : computational camera to be used
 * SampleTarget : target to be sampled
 * noPltPoints  : number of the points on the signal curve
 *
 * options      :
 *      -   channel         : r,g,b,a
 *      -   probePosition   : position of the probe
 *      -   timeWindow      : timeWindow to be plotted
 *      -   minValue        : minimum value on the vertical axis
 *      -   maxValue        : maximum value on the vertical axis
 *      -   restValue       : rest value of the signal
 *      -   color           : color of the curve to be plotted
 *      -   visiblity       : "true" or "false"
 *      -   linewidth       : linewidth of the signal
 *      -   callback        : callback function
 *========================================================================
 */
function Signal(SampleTarget,noPltPoints=512,options={}){

/*------------------------------------------------------------------------
 * Initial values
 *------------------------------------------------------------------------
 */
    this.cgl        = cgl ;
    this.sample     = SampleTarget ;
    this.noPltPoints= noPltPoints ;
    this.pltTime    = 0. ;
    this.lineGeom   = LineGeometry(this.noPltPoints) ;

    /* reading options */
    this.minValue   = readOption(options.minValue,  0               ) ;
    this.maxValue   = readOption(options.maxValue,  1               ) ;
    this.restValue  = readOption(options.restValue, 0               ) ;
    this.timeWindow = readOption(options.timeWindow,1000            ) ;
    this.linewidth  = readOption(options.linewidth, 1               ) ;
    this.probePosition = readOption( options.probePosition, [0.5,0.5]) ;
    this.color      = readOption(options.color,     [0,0,0]         ) ;
    this.channel    = readOption(options.channel,   'r'             ) ;
    this.visible    = readOption(options.visible,   true            ) ;
    this.callback   = readOption(options.callback, function(){}     ) ;


    this.lineGeom.width = this.linewidth ;
    this.channelMultiplier = getChannelMultiplier(this.channel) ;

/*------------------------------------------------------------------------
 * renderTargets
 *------------------------------------------------------------------------
 */
    this.ccrr = new FloatRenderTarget( this.noPltPoints, 1 ) ;
    this.cprv = new FloatRenderTarget( this.noPltPoints, 1 ) ;

/*------------------------------------------------------------------------
 * hist
 *------------------------------------------------------------------------
 */
    this.hist = new Solver(     {
        uniforms: {
            probePosition : { type: "v2", value: this.probePosition     } ,
            surf    : { type: 't',  value: this.sample                  } ,
            curv    : { type: 't',  value: this.ccrr                    } ,
            shift   : { type: "f",  value: 0.025                        } ,
            channel : { type: "v4", value: this.channelMultiplier       } ,
        } ,
        vertexShader:   vertShader.value,
        fragmentShader: histShader.value,
        renderTargets:
            {
                ourColor : { location : 0 , target : this.cprv   } ,
            }
    } ) ;

/*------------------------------------------------------------------------
 * scaleTimeWindow
 *------------------------------------------------------------------------
 */
    this.scaleTimeWindow = new Solver( {
            vertexShader    : vertShader.value ,
            fragmentShader  : sctwShader.value ,
            uniforms        : {
                map         : { type : 't', value : this.ccrr       } ,
                oldWindow   : { type: 'f', value : this.timeWindow  } ,
                newWindow   : { type: 'f', value : this.timeWindow  } ,
            } ,
            renderTargets   : {
                FragColor   : { location : 0 , target : this.cprv   } ,
            } ,
            clear   : true ,
    } ) ;


/*------------------------------------------------------------------------
 * wA2b
 *------------------------------------------------------------------------
 */
    this.wA2b = new Solver(   {
        uniforms:{
            map: { type: 't', value: this.cprv }
        },
        vertexShader  : vertShader.value,
        fragmentShader: wA2bShader.value,
        renderTargets:{
            outColor : { location :0, target : this.ccrr }
        }
    } ) ;

/*------------------------------------------------------------------------
 * iplt
 *------------------------------------------------------------------------
 */
    this.iplt = new Solver(   {
        uniforms: {
            restValue: {type: 'f', value: this.restValue }
        },
        vertexShader    : vertShader.value,
        fragmentShader  : ipltShader.value,
        renderTargets   : {
            FragColor1  : { location : 0, target : this.cprv     } ,
            FragColor2  : { location : 1, target : this.ccrr     } ,
        }
    } ) ;

/*------------------------------------------------------------------------
 * line : signal line
 *------------------------------------------------------------------------
 */
    this.line = new Solver({
            vertexShader    : lvtxShader.value,
            fragmentShader  : lfgmShader.value,
            uniforms    : {
                minValue:   { type: 'f',  value: this.minValue      } ,
                maxValue:   { type: 'f',  value: this.maxValue      } ,
                map     :   { type: 't',  value: this.ccrr          } ,
                color   :   { type: 'v3', value: this.color         } ,
                visible :   { type: 'f',  value: this.visible       } ,
            } ,
            geometry : this.lineGeom,
            clear    : false,
            clearColor : [0.,0.,0.,0.] ,
    } ) ;

/*------------------------------------------------------------------------
 * initialize signal
 *------------------------------------------------------------------------
 */
    this.init = function(currTime){
        if (currTime != undefined ){
            this.pltTime = currTime ;
        }
        this.iplt.render() ;
        this.hist.setUniform('shift',0) ;
        this.hist.render() ;
        this.wA2b.render() ;
    }

/*------------------------------------------------------------------------
 * update signal
 *------------------------------------------------------------------------
 */
    this.update = function(currTime){
        var timeDiff = currTime-this.pltTime ;
        var shift = timeDiff/this.timeWindow ;
        if ( shift>= 1.0/this.noPltPoints) {
            this.callback() ;
            this.hist.setUniform('shift', shift) ;
            this.hist.render() ;
            this.wA2b.render() ;
            this.pltTime = currTime ;
        }
        return ;
    }

/*------------------------------------------------------------------------
 * update time window of the signal
 *------------------------------------------------------------------------
 */
    this.updateTimeWindow = function(timeWindow){
        var oldWindow = this.timeWindow ;
        this.scaleTimeWindow.setUniform('oldWindow',oldWindow       ) ;
        this.scaleTimeWindow.setUniform('newWindow',timeWindow      ) ;
        this.timeWindow = timeWindow ;
        this.scaleTimeWindow.render() ;
        this.wA2b.render() ;
        this.hist.setUniform('shift',0) ;
        this.hist.render() ;
        this.wA2b.render() ;
        this.render() ;
        return ;
    }

/*------------------------------------------------------------------------
 * set channel
 *------------------------------------------------------------------------
 */
    this.setChannel = function(c){
        this.channel = c ;
        this.channelMultiplier = getChannelMultiplier(c) ;

        this.hist.setUniform('channel', this.channelMultiplier) ;
    }

/*------------------------------------------------------------------------
 * set pobe position for the signal
 *------------------------------------------------------------------------
 */
    this.setProbePosition = function(probePosition){
        this.init(this.pltTime) ;
        this.probePosition = probePosition ;
        this.hist.setUniform('probePosition',this.probePosition) ;
        return ;
    }

/*------------------------------------------------------------------------
 * get prob position for the signal
 *------------------------------------------------------------------------
 */
    this.getProbePosition = function(){
        return this.probePosition ;
    }

/*------------------------------------------------------------------------
 * set the minimum value on the vertical-axis of the signal plot
 *------------------------------------------------------------------------
 */
    this.setMinValue = function(minValue){
        this.minValue = minValue ;
        this.line.setUniform('minValue', this.minValue) ;
        return ;
    }

/*------------------------------------------------------------------------
 * set the maximum value on the vertical-axis of the signal pot
 *------------------------------------------------------------------------
 */
    this.setMaxValue = function(maxValue){
        this.maxValue = maxValue ;
        this.line.setUniform('maxValue', this.maxValue);
        return ;
    }

/*------------------------------------------------------------------------
 * set the rest (default) value of the signal
 *------------------------------------------------------------------------
 */
    this.setRestValue = function(restValue){
        this.restValue = restValue ;
        this.iplt.setUniform('restValue', this.restValue );
        return ;
    }

/*------------------------------------------------------------------------
 * set the color of the signal curve
 *------------------------------------------------------------------------
 */
    this.setColor = function(color){
        this.color = color  ;
        this.line.setUniform('color',this.color);
        return ;
    }

/*------------------------------------------------------------------------
 * set line width of the signal plot
 *------------------------------------------------------------------------
 */
    this.setLinewidth = function(lw){
        this.linewidth = lw ;
        this.lineGeom.width = this.linewidth ;
        this.material.linewidth = this.linewidth ;
        return ;
    }

/*------------------------------------------------------------------------
 * set sample target
 *------------------------------------------------------------------------
 */
    this.setSampleTarget = function(ST){
        this.sample = ST ;
        this.hist.setUniform('surf',this.sample) ;
    }

/*------------------------------------------------------------------------
 * reset(Opts)
 *
 * Opt(ion)s :
 *      -   sample      : a render target sampler
 *      -   channel     : r,g,b,a
 *      -   probePosition     : position of the probe
 *      -   timeWindow  : timeWindow to be plotted
 *      -   minValue    : minimum value on the vertical axis
 *      -   maxValue    : maximum value on the vertical axis
 *      -   restValue   : rest value of the signal
 *      -   color       : color of the curve to be plotted
 *      -   linewidth   : linewidth of the signal
 *------------------------------------------------------------------------
 */
    this.reset = function(Opts){
        if (Opts != undefined ){
            if ( Opts.minValue != undefined ){
                this.setMinValue(Opts.minValue) ;
            }
            if ( Opts.maxValue != undefined ){
                this.setMaxValue(Opts.maxValue) ;
            }
            if ( Opts.restValue != undefined ){
                this.setRestValue( Opts.restValue) ;
            }
            if ( Opts.probePosition != undefined ){
                this.setProbePosition( Opts.probePosition ) ;
            }
            if ( Opts.timeWindow != undefined ){
                this.setTimeWindow( Opts.timeWindow ) ;
            }
            if ( Opts.color != undefined ){
                this.setColor( Opts.color ) ;
            }
            if ( Opts.linewidth != undefined ){
                this.setLinewidth( Opts.linewidth ) ;
            }
            if ( Opts.channel != undefined ){
                this.setChannel(Opts.channel ) ;
            }
            if ( Opts.sample != undefined ) {
                this.setSampleTarget( Opts.sample ) ;
            }
        }
        this.init() ;
    }

/*------------------------------------------------------------------------
 * hide the signal plot
 *------------------------------------------------------------------------
 */
    this.hide = function(){
        this.visible = 0.0 ;
        this.line.setUniform('visible',0.0) ;
    }

/*------------------------------------------------------------------------
 * show the signal plot
 *------------------------------------------------------------------------
 */
    this.show = function(){
        this.visible = true ;
        this.line.setUniform('visible',1.0) ;
    }

/*------------------------------------------------------------------------
 * set visiblity of the signal plot
 *------------------------------------------------------------------------
 */
    this.setVisiblity = function( flag ){
        this.visible = flag ;
        this.line.setUniform('visible',flag) ;
    }

/*------------------------------------------------------------------------
 * render
 *------------------------------------------------------------------------
 */
    this.render = function(){
        if (this.visible > 0.5 ){
            this.line.render() ;
        }
    }
}
/*========================================================================
 * fromTickOptions
 *========================================================================
 */
function fromTickOptions(tOption){
        var t = {} ;
        var opts = {} ;
        if (tOption != undefined ){
            opts = tOption ;
        }
        t.ticks = readOption( opts.ticks,    []          ) ;
        t.mode  = readOption( opts.mode,     'off'       ) ;
        t.unit  = readOption( opts.unit,     ''          ) ;
        t.style = readOption( opts.style,    '#000000'   ) ;
        t.font  = readOption( opts.font,     '11pt Times') ;
        t.min   = readOption( opts.min,      0           ) ;
        t.max   = readOption( opts.max,      1           ) ;
        t.precision = readOptions( opts.precision, undefined ) ;
        return t ;
    }

/*========================================================================
 * Message
 *========================================================================
 */ 
class Message{
    constructor( message, x,y, options){
        this.text = message ;
        this.x  = x ;
        this.y    = y ;
        
        this.style   = readOption( options.style,    "#000000"       ) ;
        this.font    = readOption( options.font,     "12px Times"    ) ;
        this.visible = readOption( options.visible,  true            ) ;
        this.align   = readOption( options.align ,   'start'         ) ;
    }

/*------------------------------------------------------------------------
 * setFont
 *------------------------------------------------------------------------
 */
    setFont(font){
        this.font   = readOption(font,      this.font   ) ;
    }

/*------------------------------------------------------------------------
 * setStyle
 *------------------------------------------------------------------------
 */
    setStyle(style){
        this.style  = readOption(style ,    this.style  ) ;
    }

/*------------------------------------------------------------------------
 * setAlign
 *------------------------------------------------------------------------
 */
    setAlign(align){
        this.align  = readOption(align,     this.align  ) ;
    }

/*------------------------------------------------------------------------
 * setText
 *------------------------------------------------------------------------
 */
    setText(text){
        this.text = readOption(text, this.text) ;
    }

/*------------------------------------------------------------------------
 * hide
 *------------------------------------------------------------------------
 */
    hide(){
        this.visible = false ;
    }

/*------------------------------------------------------------------------
 * show
 *------------------------------------------------------------------------
 */
    show(){
        this.visible = true ;
    }
/*------------------------------------------------------------------------
 * setVisiblity
 *------------------------------------------------------------------------
 */
    setVisiblity( visible ){
        this.visible = readOption( visible, this.visible ) ;
    }

/*------------------------------------------------------------------------
 * toggleVisible
 *------------------------------------------------------------------------
 */
    toggleVisible(){
        this.visible = !this.visible ;
    }

    toggle(){
        this.visible = !this.visible ;
    }
}

/*=========================================================================
 * SignalPlot( renderer, camera, options )
 *
 * Usage    :   Constructor for plotting. The inputs are as follows
 *
 * renderer :   renderer to be used for all plotting purposes;
 * camera   :   camera to be used for plotting
 * options  :
 *      -   noPlotPoints    :   number of points on each signal curve
 *      -   backgroundColor :   color of plot's background
 *      -   dispWidth       :   number of horizontal pixels of plot
 *      -   dispHeight      :   number of vertical pixels of the plot
 *      -   grid            :   'on', 'off'
 *      -   nx              :   number of horizontal divisions of the grid
 *      -   ny              :   number of vertical divisions of the grid
 *      -   gridColor       :   color of the grid
 *      -   xticks          :   array of xticks
 *      -   yticks          :   array of yticks
 *      -   callback        :   callback function
 *=========================================================================
 */
function SignalPlot (pltOptions={}){
    this.cgl                = cgl ;
    this.gl                 = cgl.gl ;

    this.canvasTarget   = false ;
    this.backgroundColor = readOption(
        pltOptions.backgroundColor,
        [0,0,0,0]
    ) ;
    this.noPlotPoints = readOption( pltOptions.noPltPoints, 512 ) ;
    this.grid       = readOption( pltOptions.grid, 'off'        ) ;
    this.nx         = readOption( pltOptions.nx ,   5           ) ;
    this.ny         = readOption( pltOptions.ny ,   5           ) ;
    this.gridColor  = readOption( pltOptions.gridColor, '#999999') ;
    this.dispWidth  = readOption( pltOptions.dispWidth, 512     ) ;
    this.dispHeight = readOption( pltOptions.dispHeight,512     ) ;

    this.canvas     = readOption( pltOptions.canvas, undefined  ) ;
    if (this.canvas != undefined ){
        this.context = this.canvas.getContext('2d') ;
    }

    this.container  = readOption( pltOptions.container, undefined ) ;
    this.callback   = readOption( pltOptions.callback, function(){} ) ;

    this.xticks = fromTickOptions( pltOptions.xticks ) ;
    this.yticks = fromTickOptions( pltOptions.yticks ) ;

    if ( ( this.container != undefined ) &&
            (this.canvas != undefined ) ){
        this.canvasTarget = true ;
    }

/*-------------------------------------------------------------------------
 * Grid and Background
 *-------------------------------------------------------------------------
 */
    this.bcanvas = document.createElement('canvas') ;
    this.bcanvas.width = this.canvas.width ;
    this.bcanvas.height = this.canvas.height ;
    this.bcontext= this.bcanvas.getContext('2d') ;

/*------------------------------------------------------------------------
 * addMessage
 *------------------------------------------------------------------------
 */
    this.messages = [] ;
    this.addMessage = function( message, x, y, options){
        var msg = new Message( message,x,y, options) ;
        this.messages.push(msg) ;
        this.initBackground() ;
        return msg ;
    }

/*------------------------------------------------------------------------
 * initTitle
 *------------------------------------------------------------------------
 */
    var titleOptions = readOption( pltOptions.title, {} ) ;
    this.title = {} ;
    this.title.text = readOption(titleOptions.text, '' ) ;
    this.title.x = readOption( titleOptions.x , 0.5  ) ;
    this.title.y = readOption( titleOptions.y , 0.05 ) ;
    this.title.style = readOption( titleOptions.style,    "#000000"  ) ;
    this.title.font = readOption( titleOptions.font, '12pt Times'    ) ;
    this.title.visible = readOption( titleOptions.visible, true  ) ;
    this.title.align = readOption( titleOptions.align, 'center' ) ;
    this.messages.push( this.title ) ;

/*------------------------------------------------------------------------
 * setTitle
 *------------------------------------------------------------------------
 */
    this.setTitle = function(text, options={}){
        this.title.text = text ;
        this.title.x    = readOption( options.x , this.title.x         ) ;
        this.title.y    = readOption( options.y , this.title.y         ) ;
        this.title.style= readOption( options.style, this.title.style  ) ;
        this.title.font = readOption( options.font,  this.title.font   ) ;
        this.title.visible = readOption( options.visible, 
                this.title.visible ) ;
        this.title.align= readOption( options.align,this.title.align  ) ;
    
        this.messages.push( this.title ) ;
        this.initBackground() ;
        this.render() ;
    }


/*------------------------------------------------------------------------
 * writeMessages
 *------------------------------------------------------------------------
 */
    this.writeMessages = function(){
        for (var i=0 ; i < this.messages.length; i++){
            var message = this.messages[i] ;
            if (message.visible){
                this.bcontext.font = message.font ;
                this.bcontext.fillStyle = message.style ;
                this.bcontext.textAlign = message.align ;
                this.bcontext.fillText( message.text,
                                        this.canvas.width*message.x,
                                        this.canvas.height*message.y );
            }
        }
    }

/*------------------------------------------------------------------------
 * setTicks
 *------------------------------------------------------------------------
 */
    this.setTicks = function(){
        if ( this.xticks.mode == 'auto' ){
            this.xticks.ticks = [] ;
            var dt = this.timeWindow/this.nx ;
            for (var i=1 ; i<this.nx ; i++){
                var num = (dt*i) ;
                if( this.xticks.precision != undefined ){
                    num = num.toFixed(this.xticks.precision) ;
                }
                this.xticks.ticks.push(num + this.xticks.unit) ;
            }
        }

        if ( this.yticks.mode == 'auto' ){
            var dy = (this.yticks.max-this.yticks.min)/this.ny ;
            this.yticks.ticks = [] ;
            for (var i=1 ; i<this.ny ; i++){
                var num = (dy*i+this.yticks.min) ;
                if( this.yticks.precision != undefined ){
                    num = num.toFixed(this.yticks.precision) ;
                }
                this.yticks.ticks.push(  num + this.yticks.unit );
            }
        }
    }

/*------------------------------------------------------------------------
 * setXTicks
 *------------------------------------------------------------------------
 */
    this.setXTicks= function(xt){
        if ( xt.ticks != undefined ){
            this.xticks.ticks = xt.ticks ;
        }
        if ( xt.mode != undefined ){
            this.xticks.mode = xt.mode ;
        }
        if ( xt.unit != undefined ){
            this.xticks.unit = xt.unit ;
        }
        if ( xt.style != undefined ){
            this.xticks.style = xt.style ;
        }
        if ( xt.font != undefined ){
            this.xticks.font = xt.font ;
        }
        this.initBackground() ;
    }

/*------------------------------------------------------------------------
 * setYTicks
 *------------------------------------------------------------------------
 */

    this.setYTicks = function(yt){
        if ( yt.ticks != undefined ){
            this.yticks.ticks = yt.ticks ;
        }
        if ( yt.mode != undefined ){
            this.yticks.mode = yt.mode ;
        }
        if ( yt.unit != undefined ){
            this.yticks.unit = yt.unit ;
        }
        if ( yt.style != undefined ){
            this.yticks.style = yt.style ;
        }
        if ( yt.font != undefined ){
            this.yticks.font = yt.font ;
        }
        if ( yt.min != undefined ){
            this.yticks.min = yt.min ;
        }
        if ( yt.max != undefined ){
            this.yticks.max = yt.max ;
        }
        this.initBackground() ;
    }

/*------------------------------------------------------------------------
 * writeTicks
 *------------------------------------------------------------------------
 */
    this.writeTicks = function(){
        this.setTicks() ;
        if (this.xticks.mode != 'off' ){
            this.bcontext.font = this.xticks.font ;
            this.bcontext.fillStyle = this.xticks.style ;
            this.bcontext.textAlign = "center" ;
            for (var i=1; i<=this.xticks.ticks.length ;i++){
                var dx = this.canvas.width / (this.xticks.ticks.length+1)
                var dy = this.canvas.height/ (this.ny) ;
                this.bcontext.fillText(
                    this.xticks.ticks[i-1],
                    i*dx,
                    this.canvas.height-10
                ) ;
            }
        }
        if ( this.yticks.mode != 'off' ){
            this.bcontext.font = this.yticks.font ;
            this.bcontext.fillStyle = this.yticks.style ;
            this.bcontext.textAlign = "start" ;
            for (var i=1; i<=this.yticks.ticks.length ;i++){
                var dy = this.canvas.height
                        /(this.yticks.ticks.length+1) ;
                this.bcontext.fillText(
                    this.yticks.ticks[i-1],
                    10,
                    this.canvas.height-i*dy
                ) ;
            }
        }
    }

/*------------------------------------------------------------------------
 * initBackground
 *------------------------------------------------------------------------
 */
    this.initBackground = function(){
        this.bcontext.clearRect(
            0,
            0,
            this.canvas.width,
            this.canvas.height
        ) ;
        if ( this.grid == 'on' ){
            this.bcontext.setLineDash([10,10]) ;
            this.bcontext.strokeStyle=this.gridColor ;
            var dx = this.canvas.width / (this.nx) ;
            var dy = this.canvas.height/ (this.ny) ;
            for (var i=1; i<this.nx ; i++){
                this.bcontext.moveTo(i*dx,0) ;
                this.bcontext.lineTo(i*dx,this.canvas.height) ;
                this.bcontext.stroke() ;
            }
            for (var j=1; j<this.ny ; j++){
                this.bcontext.moveTo(0,j*dy) ;
                this.bcontext.lineTo(this.canvas.width,j*dy) ;
                this.bcontext.stroke() ;
            }
        }

        this.writeTicks() ;
        this.writeMessages() ;
    }

/*-------------------------------------------------------------------------
 * Signals
 *-------------------------------------------------------------------------
 */
    this.noSignals = 0 ;
    this.signals = [] ;

/*------------------------------------------------------------------------
 * addSignal(SampleTarget, options)
 *
 * Usage    :   Adds a signal to the plot. The inputs are as follows:
 *
 * SampleTarget : target to be sampled
 * options      :
 *      -   channel         : r,g,b,a
 *      -   probePosition   : position of the probe
 *      -   timeWindow      : timeWindow to be plotted
 *      -   minValue        : minimum value on the vertical axis
 *      -   maxValue        : maximum value on the vertical axis
 *      -   restValue       : rest value of the signal
 *      -   color           : color of the curve to be plotted
 *      -   visiblity       : "true" or "false"
 *      -   linewidth       : linewidth of the signal
 *------------------------------------------------------------------------
 */
    this.addSignal = function(SampleTarget, options){
        var newSignal = new Signal(
                    SampleTarget,
                    this.noPltPoints,
                    options ) ;
        this.signals.push( newSignal ) ;
        this.noSignals ++ ;
        this.yticks.min = newSignal.minValue ;
        this.yticks.max = newSignal.maxValue ;
        this.timeWindow = newSignal.timeWindow ;
        return newSignal ;
    }
    
/*------------------------------------------------------------------------
 * setMinValue
 *------------------------------------------------------------------------
 */
    this.setMinValue = function(val){
        this.yticks.min = val ;
        this.initBackground() ;
        this.render() ;
    }

/*------------------------------------------------------------------------
 * setMaxValue
 *------------------------------------------------------------------------
 */
    this.setMaxValue = function(val){
        this.yticks.max = val ;
        this.initBackground() ;
        this.render() ;
        this.render() ;
    }


/*------------------------------------------------------------------------
 * update(currTime)
 *
 * Usage    :   update all signals, and set the plot time to currTime
 *------------------------------------------------------------------------
 */
    /* update signals                    */
    this.update= function(currTime){
        this.callback() ;
        for(var i=0; i<this.noSignals; i++){
            this.signals[i].update(currTime) ;
        }
        return ;
    }
/*------------------------------------------------------------------------
 * init(currTime)
 *
 * Usage    :   initialize all signals
 *------------------------------------------------------------------------
 */

    /* initialize signals                */
    this.init=function(currTime){
        this.initBackground() ;
        for(var i=0; i<this.noSignals; i++){
            this.signals[i].init(currTime) ;
        }
        return ;
    }

/*------------------------------------------------------------------------
 * updateTimeWindow(timeWindow)
 *
 * Usage    :   updates timeWindow for all signals
 *------------------------------------------------------------------------
 */
    /* update timeWindow for signals     */
    this.updateTimeWindow = function(timeWindow){
        this.timeWindow = timeWindow ;
        for(var i=0; i <this.noSignals; i++){
            this.signals[i].updateTimeWindow(timeWindow) ;
        }
        this.initBackground() ;
        this.render() ;
        return ;
    }
/*------------------------------------------------------------------------
 * setProbePosition(probePosition)
 *
 * Usage    :   set the probe position for all signals to probePosition
 *------------------------------------------------------------------------
 */
    /* set probe position for signals    */
    this.setProbePosition = function(probePosition){
        for(var i=0; i <this.noSignals; i++){
            this.signals[i].setProbePosition(probePosition) ;
        }
        this.init() ;
        return ;
    }

/*------------------------------------------------------------------------
 * getProbePosition
 *
 * Usage    : returns the position of the signals
 *------------------------------------------------------------------------
 */
    this.getProbePosition = function(){
        return this.signals[0].getProbePosition() ;
    }

/*------------------------------------------------------------------------
 * setSize
 *------------------------------------------------------------------------
 */
    this.setSize = function( dispWidth, dispHeight ){
        this.dispWidth = dispWidth ;
        this.dispHeight = dispHeight ;
        this.bgrnd.setSize( this.dispWidth, this.dispHeight ) ;
    }

/*------------------------------------------------------------------------
 * render([renderTarget,[forceClear])
 *
 * Usage        :   render the plot
 *
 * renderTarget :   target if the render if other than screen
 * forceClear   :   boolean asking the renderer to clear the output
                    before rendering. Default: false
 *------------------------------------------------------------------------
 */
    /* render plot                       */
    this.render = function(renderTarget, forceClear){
        this.context.clearRect(
            0,
            0,
            this.canvas.width,
            this.canvas.height
        ) ;
        this.context.drawImage(
            this.bcanvas,
            0,
            0,
            this.canvas.width,
            this.canvas.height
        ) ;
        gl.bindFramebuffer(
            gl.DRAW_FRAMEBUFFER,
            null
        );
        gl.clear(
            gl.COLOR_BUFFER_BIT
        );

        for(var i=0; i<this.noSignals; i++){
            this.signals[i].render() ;
        }
        this.context.drawImage(
            gl.canvas,
            0,
            0,
            this.canvas.width,
            this.canvas.height
        ) ;
    } ;

}  /* End of SignalPlot */

/*========================================================================
 * Curve        : Curve Structure
 *
 * options      :
 *      -   channel         : r,g,b,a
 *      -   probePosition   : position of the probe
 *      -   timeWindow      : timeWindow to be plotted
 *      -   minValue        : minimum value on the vertical axis
 *      -   maxValue        : maximum value on the vertical axis
 *      -   restValue       : rest value of the signal
 *      -   color           : color of the curve to be plotted
 *      -   visiblity       : "true" or "false"
 *      -   linewidth       : linewidth of the signal
 *========================================================================
 */
function Curve( SampleTarget,
                xAxisRange,
                options){

/*------------------------------------------------------------------------
 * Initial values
 *------------------------------------------------------------------------
 */
    this.cgl        = cgl ;
    this.sample     = SampleTarget ;
    this.noPltPoints= this.sample.width ;
    this.linewidth  = 2.0 ;
    this.lineGeom   = LineGeometry(this.noPltPoints) ;
    this.color          = [1,0,0] ;
    this.visible        = 1.0 ;
    this.channel        = 'r' ;

    this.xAxisRange  = xAxisRange ;

    this.localXrange = xAxisRange ;

    this.calcXrange  = function(){
        var ax = this.xAxisRange[1]-this.xAxisRange[0] ;
        var x0 = (this.localXrange[0]-this.xAxisRange[0])/ax ;
        var x1 = (this.localXrange[1]-this.xAxisRange[0])/ax ;
        this.xrange = [x0,x1] ;
    }
    this.calcXrange() ;

    this.yrange     = [0,1] ;

    if ( options != undefined ){
        if (options.xrange != undefined ){
            this.localXrange = options.xrange ;
            this.calcXrange() ;
        }

        if (options.color != undefined ){
            this.color = options.color ;
        }
        if (options.linewidth != undefined ){
            this.linewidth = options.linewidth ;
        }
        if (options.visible != undefined ){
            this.visible = options.visible ;
        }
        if (options.channel != undefined ){
            this.channel = options.channel ;
        }

        if (options.yrange != undefined ){
            this.yrange = options.yrange ;
        }
    }

    this.lineGeom.width = this.linewidth ;
    this.channelMultiplier = getChannelMultiplier(this.channel) ;

/*------------------------------------------------------------------------
 * curve
 *------------------------------------------------------------------------
 */
    this.curve = new Solver({
            vertexShader    : lpvtShader.value,
            fragmentShader  : lfgmShader.value,
            uniforms    : {
                xrange  :   {
                    type: 'v2',
                    value: this.xrange
                } ,
                yrange  :   {
                    type: 'v2',
                    value: this.yrange
                } ,
                map     :   {
                    type: 't',
                    value: this.sample
                } ,
                channelMultiplier : {
                    type: 'v4',
                    value: this.channelMultiplier
                } ,
                color   :   {
                    type: 'v3',
                    value: this.color
                } ,
                visible :   {
                    type: 'f',
                    value: this.visible
                } ,
            } ,
            geometry : this.lineGeom,
            clear    : false,
            clearColor : [0.,0.,0.,0.] ,
    } ) ;


/*------------------------------------------------------------------------
 * initialize signal
 *------------------------------------------------------------------------
 */
    this.init = function(currTime){
        this.curve.render() ;
    }

/*------------------------------------------------------------------------
 * set channel
 *------------------------------------------------------------------------
 */
    this.setChannel = function(c){
        this.channel = c ;
        this.channelMultiplier = getChannelMultiplier(c) ;

        this.curve.setUniform('channel', this.channelMultiplier) ;
    }

/*------------------------------------------------------------------------
 * setXAxisRange
 *------------------------------------------------------------------------
 */
    this.setXAxisRange= function( xa ){
        this.xAxisRange = xa ;
        this.calcXrange() ;
        this.curve.setUniform('xrange', this.xrange) ;
    }

/*------------------------------------------------------------------------
 * set the range of the vertical axis
 *------------------------------------------------------------------------
 */
    this.setYRange = function(yr){
        this.yrange = yr ;
        this.curve.setUniform('yrange', this.yrange) ;
        return ;
    }

/*------------------------------------------------------------------------
 * setXrange
 *------------------------------------------------------------------------
 */
    this.setXrange = function(xr){
        this.localXrange = xr ;
        this.calcXrange ;
    }

/*------------------------------------------------------------------------
 * set the color of the signal curve
 *------------------------------------------------------------------------
 */
    this.setColor = function(color){
        this.color = color  ;
        this.curve.setUniform('color',this.color);
        return ;
    }

/*------------------------------------------------------------------------
 * set line width of the signal plot
 *------------------------------------------------------------------------
 */
    this.setLinewidth = function(lw){
        this.linewidth = lw ;
        this.lineGeom.width = this.linewidth ;
        return ;
    }

/*------------------------------------------------------------------------
 * set sample target
 *------------------------------------------------------------------------
 */
    this.setSampleTarget = function(ST){
        this.sample = ST ;
        this.curve.setUniform('map',this.sample) ;
    }

/*------------------------------------------------------------------------
 * hide the signal plot
 *------------------------------------------------------------------------
 */
    this.hide = function(){
        this.visible = 0.0 ;
        this.line.setUniform('visible',0.0) ;
    }

/*------------------------------------------------------------------------
 * show the signal plot
 *------------------------------------------------------------------------
 */
    this.show = function(){
        this.visible = 1.0 ;
        this.curve.setUniform('visible',1.0) ;
    }

/*------------------------------------------------------------------------
 * set visiblity of the signal plot
 *------------------------------------------------------------------------
 */
    this.setVisiblity = function( flag ){
        this.visible = flag ;
        this.curve.setUniform('visible',flag) ;
    }

/*------------------------------------------------------------------------
 * render
 *------------------------------------------------------------------------
 */
    this.render = function(){
        if (this.visible > 0.5 ){
            this.curve.render() ;
        }
    }
} /* End of Curve */

/*========================================================================
 * Plot1D( options )
 *
 * Usage    :   Constructor for plotting 1D lines out of texture of data
 *
 * options  :
 *      -   backgroundColor :   color of plot's background
 *      -   dispWidth       :   number of horizontal pixels of plot
 *      -   dispHeight      :   number of vertical pixels of the plot
 *      -   grid            :   'on', 'off'
 *      -   nx              :   number of horizontal divisions of the grid
 *      -   ny              :   number of vertical divisions of the grid
 *      -   gridColor       :   color of the grid
 *      -   xticks          :   array of xticks
 *      -   yticks          :   array of yticks
 *========================================================================
 */
function Plot1D(pltOptions={}){
    this.cgl                = cgl ;
    this.gl                 = cgl.gl ;
    this.backgroundCollor = readOption(
        pltOptions.backgroundColor,
        [0.,0.,0.,0]
    ) ;
    this.grid       = readOption(pltOptions.grid,    'off'   ) ;
    this.nx         = readOption(pltOptions.nx,      5       ) ;
    this.ny         = readOption(pltOptions.ny,      5       ) ;
    this.gridColor  = readOption(pltOptions.gridColor, '#999999') ;
    this.dispWidth  = readOption(pltOptions.dispWidth, 512   ) ;
    this.dispHeight = readOption(pltOptions.dispHeight,512   ) ;
    this.xrange = readOption(pltOptions.xrange, [0,1]       ) ;
    this.yrange = readOption(pltOptions.yrange, [0,1]       ) ;

    this.canvas = readOption(pltOptions.canvas, null        ) ;
    if ( this.canvas == null ){
        warn( 'No canvas was provided! No destination plot is assumed! '
            + 'No Plot1D can be defined '   ) ;
        delete this ;
        return null ;
    }
    this.context = this.canvas.getContext("2d") ;


    this.xticks = fromTickOptions( pltOptions.xticks ) ;
    this.yticks = fromTickOptions( pltOptions.yticks ) ;

    this.canvasTarget   = true ;

/*-------------------------------------------------------------------------
 * Grid and Background
 *-------------------------------------------------------------------------
 */
    this.bcanvas = document.createElement('canvas') ;
    this.bcanvas.width = this.canvas.width ;
    this.bcanvas.height = this.canvas.height ;
    this.bcontext= this.bcanvas.getContext('2d') ;

/*------------------------------------------------------------------------
 * addMessage
 *------------------------------------------------------------------------
 */
    this.messages = [] ;
    this.addMessage = function( message, x, y, options ){
        var msg = new Message( message, x,y, options) ;
        this.messages.push(msg) ;
        this.initBackground() ;
    }

/*------------------------------------------------------------------------
 * writeMessages
 *------------------------------------------------------------------------
 */
    this.writeMessages = function(){
        for (var i=0 ; i < this.messages.length; i++){
            var message = this.messages[i] ;
            if (message.visible){
                this.bcontext.font = message.font ;
                this.bcontext.fillStyle = message.style ;
                this.bcontext.textAlign = message.align ;
                this.bcontext.fillText( message.text,
                                        this.canvas.width*message.x,
                                        this.canvas.height*message.y );
            }
        }
    }

/*------------------------------------------------------------------------
 * setTicks
 *------------------------------------------------------------------------
 */
    this.setTicks = function(){
        if ( this.xticks.mode == 'auto' ){
            this.xticks.ticks = [] ;
            var dx = (this.xrange[1]-this.xrange[0])/this.nx ;
            for (var i=1 ; i<this.nx ; i++){
                var num = this.xrange[0]+(dx*i) ;
                if( this.xticks.precision != undefined ){
                    num = num.toFixed(this.xticks.precision) ;
                }
                this.xticks.ticks.push(num+ this.xticks.unit ) ;
            }
        }

        if ( this.yticks.mode == 'auto' ){
            var dy = (this.yrange[1]-this.yrange[0])/this.ny ;
            this.yticks.ticks = [] ;
            for (var i=1 ; i<this.ny ; i++){
                var num = (dy*i+this.yrange[0]) ;
                if( this.yticks.precision != undefined ){
                    num = num.toFixed(this.yticks.precision) ;
                }
                this.yticks.ticks.push( num
                + this.yticks.unit );
            }
        }
    }

/*------------------------------------------------------------------------
 * setXTicks
 *------------------------------------------------------------------------
 */
    this.setXTicks= function(xt){
        if ( xt.ticks != undefined ){
            this.xticks.ticks = xt.ticks ;
        }
        if ( xt.mode != undefined ){
            this.xticks.mode = xt.mode ;
        }
        if ( xt.unit != undefined ){
            this.xticks.unit = xt.unit ;
        }
        if ( xt.style != undefined ){
            this.xticks.style = xt.style ;
        }
        if ( xt.font != undefined ){
            this.xticks.font = xt.font ;
        }
        this.initBackground() ;
    }

/*------------------------------------------------------------------------
 * setYTicks
 *------------------------------------------------------------------------
 */

    this.setYTicks = function(yt){
        if ( yt.ticks != undefined  ){
            this.yticks.ticks = yt.ticks ;
        }
        if ( yt.mode != undefined  ){
            this.yticks.mode = yt.mode ;
        }
        if ( yt.unit != undefined  ){
            this.yticks.unit = yt.unit ;
        }
        if ( yt.style != undefined   ){
            this.yticks.style = yt.style ;
        }
        if ( yt.font != undefined  ){
            this.yticks.font = yt.font ;
        }
        this.initBackground() ;
    }

/*------------------------------------------------------------------------
 * writeTicks
 *------------------------------------------------------------------------
 */
    this.writeTicks = function(){
        this.setTicks() ;
        if (this.xticks.mode != 'off' ){
            this.bcontext.font = this.xticks.font ;
            this.bcontext.fillStyle = this.xticks.style ;
            this.bcontext.textAlign = "center" ;
            for (var i=1; i<=this.xticks.ticks.length ;i++){
                var dx = this.canvas.width / (this.xticks.ticks.length+1)
                var dy = this.canvas.height/ (this.ny) ;
                this.bcontext.fillText( this.xticks.ticks[i-1],
                                        i*dx,this.canvas.height-10) ;
            }
        }
        if ( this.yticks.mode != 'off' ){
            this.bcontext.font = this.yticks.font ;
            this.bcontext.fillStyle = this.yticks.style ;
            this.bcontext.textAlign = "start" ;
            for (var i=1; i<=this.yticks.ticks.length ;i++){
                var dy = this.canvas.height /
                    (this.yticks.ticks.length+1) ;
                this.bcontext.fillText(
                    this.yticks.ticks[i-1],
                    10,
                    this.canvas.height-i*dy
                ) ;
            }
        }
    }

/*------------------------------------------------------------------------
 * initBackground
 *------------------------------------------------------------------------
 */
    this.initBackground = function(){
        this.bcontext.clearRect(
            0,
            0,
            this.canvas.width,
            this.canvas.height
        ) ;
        if ( this.grid != 'off' & this.grid != false ){
            this.bcontext.setLineDash([10,10]) ;
            this.bcontext.strokeStyle=this.gridColor ;
            var dx = this.canvas.width / (this.nx) ;
            var dy = this.canvas.height/ (this.ny) ;
            for (var i=1; i<this.nx ; i++){
                this.bcontext.moveTo(i*dx,0) ;
                this.bcontext.lineTo(i*dx,this.canvas.height) ;
                this.bcontext.stroke() ;
            }
            for (var j=1; j<this.ny ; j++){
                this.bcontext.moveTo(0,j*dy) ;
                this.bcontext.lineTo(this.canvas.width,j*dy) ;
                this.bcontext.stroke() ;
            }
        }

        this.writeTicks() ;
        this.writeMessages() ;
    }

/*-------------------------------------------------------------------------
 * Signals
 *-------------------------------------------------------------------------
 */
    this.noCurves = 0 ;
    this.curves = [] ;

/*------------------------------------------------------------------------
 * addCurve(SampleTarget, options)
 *
 * Usage    :   Adds a curve to the plot. The inputs are as follows:
 *
 * SampleTarget : target to be sampled
 * options      :
 *      -   channel         : r,g,b,a
 *      -   probePosition   : position of the probe
 *      -   timeWindow      : timeWindow to be plotted
 *      -   minValue        : minimum value on the vertical axis
 *      -   maxValue        : maximum value on the vertical axis
 *      -   restValue       : rest value of the curve
 *      -   color           : color of the curve to be plotted
 *      -   visiblity       : "true" or "false"
 *      -   linewidth       : linewidth of the curve
 *------------------------------------------------------------------------
 */
    this.addCurve = function(SampleTarget ,options){
        options.xrange = this.xrange ;
        options.yrange = this.yrange ;
        var newCurve = new Curve(    SampleTarget,
                                    this.xrange,
                                    options ) ;
        this.curves.push( newCurve ) ;
        this.noCurves ++ ;
        return newCurve ;
    }

/*------------------------------------------------------------------------
 * setSize
 *------------------------------------------------------------------------
 */
    this.setSize = function( dispWidth, dispHeight ){
        this.dispWidth = dispWidth ;
        this.dispHeight = dispHeight ;
        this.canvas.width = this.dispWidth  ;
        this.canvas.height = this.dispHeight ;
        this.bcanvas.width = this.dispWidth ;
        this.bcanvas.height = this.dispHeight ;
        this.initBackground() ;
        this.render() ;
    }

/*------------------------------------------------------------------------
 * setXrange
 *------------------------------------------------------------------------
 */
    this.setXrange = function(xr){
        this.xrange = xr ;
        this.initBackground() ;

        for(var i=0; i < this.noCurves; i++){
            this.curves[i].setXAxisRange(xr) ;
        }
        this.render() ;
    }
/*------------------------------------------------------------------------
 *
 *------------------------------------------------------------------------
 */
    this.init = function(){
        this.initBackground() ;
        for(var i=0; i<this.noCurves; i++){
            this.curves[i].render() ;
        }

        this.render() ;
    }

/*------------------------------------------------------------------------
 * render([renderTarget,[forceClear])
 *
 * Usage        :   render the plot
 *
 * renderTarget :   target if the render if other than screen
 * forceClear   :   boolean asking the renderer to clear the output
                    before rendering. Default: false
 *------------------------------------------------------------------------
 */
    /* render plot                       */
    this.render = function(renderTarget, forceClear){
        this.context.clearRect(
            0,
            0,
            this.canvas.width,
            this.canvas.height
        ) ;
        this.context.drawImage(
            this.bcanvas,
            0,
            0,
            this.canvas.width,
            this.canvas.height
        ) ;
        gl.bindFramebuffer(
            gl.DRAW_FRAMEBUFFER,
            null
        );
        gl.clear(
            gl.COLOR_BUFFER_BIT
        );
        for(var i=0; i<this.noCurves; i++){
            this.curves[i].render() ;
        }
        this.context.drawImage(
            gl.canvas,
            0,
            0,
            this.canvas.width,
            this.canvas.height
        ) ;
    } ;

}  /* End of Plot1D */

/*========================================================================
 * getColormaps
 *========================================================================
 */
function getColormaps(mapList){
    var colormaps = {} ;
    for (var i=0 ; i<mapList.length;i++ ){
        var name =mapList[i] ;
        var map  = {} ;
        map.name = name  ;
        map.image = eval(name) ;
        map.width = map.image.width ;
        map.height = map.image.height ;
        map.target = new FloatRenderTarget (
                                                map.width,
                                                map.height,
                                                {data: map.image } ) ;
        map.texture = map.target.texture ;
        colormaps[name] = map ;
    }
    return colormaps ;
}

function getColormapList(){
    return  [ 
                            'chaoslab',
                            'hotbrightbands',
                            'brilliant',
                            'oygb',
                            'rainbowHotSpring',

                            /* tica colormaps   */
                            'alpineColors',
                            'armyColors',
                            'atlanticColors',
                            'auroraColors',
                            'avacadoColors',
                            'beachColors',
                            'candyColors',
                            'cmykColors',
                            'deepSeaColors',
                            'fallColors',
                            'fruitPunchColors',
                            'islandColors',
                            'lakeColors',
                            'mintColors',
                            'neonColors',
                            'pearlColors',
                            'plumColors',
                            'roseColors',
                            'solarColors',
                            'southwestColors',
                            'starryNightColors',
                            'sunsetColors',
                            'thermometerColors',
                            'watermelonColors',
                            'brassTones',
                            'brownCyanTones',
                            'cherryTones',
                            'coffeeTones',
                            'fuchsiaTones',
                            'grayTones',
                            'greenPinkTones',
                            'pigeonTones',
                            'redBlueTones',
                            'rustTones',
                            'siennaTones',
                            'valentineTones',
                            'darkTerrain',
                            'greenBrownTerrain',
                            'lightTerrain',
                            'sandyTerrain',
                            'aquamarine',
                            'blueGreenYellow',
                            'brightBands',
                            'darkBands',
                            'darkRainbow',
                            'fuitPunch',
                            'lightTemperatureMap',
                            'pastel',
                            'rainbow',
                            'temperatureMap',

                            /* mat colormaps    */
                            'autumn',
                            'blue',
                            'bone',
                            'colorcube',
                            'cool',
                            'copper',
                            'flag',
                            'gray',
                            'green',
                            'hot',
                            'hsv',
                            'jet',
                            'lines',
                            'parula',
                            'pink',
                            'prism',
                            'red',
                            'spring',
                            'summer',
                            'white',
                            'winter' 
                            ] ;
} ;
/*========================================================================
 * Plot2D( renderer, camera, renderTargets, options )
 *
 * Usage    : plots a 2D field in addition to possible tip-trajectories
 *
 * renderer :   renderer to be used for all plotting purposes;
 * camera   :   camera to be used for plotting
 * renderTargets:   [1-2 steps of renderTargets]
 * options  :
 *      -   channel     :   channel to plot         (default='r'        )
 *      -   minValue    :   min. value of the field (default=0          )
 *      -   maxValue    :   max. value of the field (default=1          )
 *      -   colormap    :   name of colormap        (default='jet'      )
 *      -   tipt        :   plot tip-trajectory?    (default='false'    )
 *      -   tiptColor   :   tip-trajectory color    (default=white      )
 *      -   tiptThreshold:  threshold for tipt      (default=0.5        )
 *      -   tiptThickness:  thickness of tipt       (default=2          )
 *      -   width       :   width of display        (default=512        )
 *      -   height      :   height of display       (default=512        )
 *      -   probePosition:   probe position         (default=(0.5,0.5)  )
 *========================================================================
 */
function Plot2D(options={}){

/*------------------------------------------------------------------------
 * return if no options are defined
 *------------------------------------------------------------------------
 */
    if (options == undefined ){
        delete this ;
        console.log('Options need to be defined') ;
        return undefined ;
    }

/*------------------------------------------------------------------------
 * setting up colormaps
 *------------------------------------------------------------------------
 */
    this.colormapList   = getColormapList() ;
    this.colormaps      = getColormaps(this.colormapList) ;

/*------------------------------------------------------------------------
 * default values
 *------------------------------------------------------------------------
 */
    this.cgl        = cgl ;
    this.gl         = cgl.gl ;

    this.canvasTarget   = false ;

    this.phase          = undefined ;
/*------------------------------------------------------------------------
 * options
 *------------------------------------------------------------------------
 */
    this.target = readOption( options.target, null ) ;
    if ( this.target == null){
        warn('Error : The target to plot needs to be defined!') ;
        return undefined ;
    }
    this.minValue   = readOption(options.minValue,      0           ) ;
    this.maxValue   = readOption(options.maxValue,      1           ) ;
    this.channel    = readOption(options.channel,       'r'         ) ;
    this.prevTarget = readOption(options.prevTarget,    undefined   ) ;
    this.callback   = readOption(options.callback,      function(){}) ;
    this.clrmName   = readOption(options.colormap,      'jet'       ) ;
    
    this.pltTipt    = readOption(options.tipt ,         false       ) ;
    this.tiptColor  = readOption(options.tiptColor,     [1,1,1]     ) ;
    this.tiptThreshold= readOption(options.tiptThreshold, 0.5       ) ;
    this.tiptThickness = readOptions( options.tiptThickness, 2      ) ;

    this.width      = readOption(options.width,         512         ) ;
    this.height     = readOption(options.height,        512         ) ;
    this.probeVisible = readOption(options.probeVisible, false      ) ;
    this.probePosition= readOption(options.probePosition, [0.5,0.5] ) ;
    this.probeColor = readOption( options.probeColor ,  "#000000"   ) ;
    this.canvas     = readOption( options.canvas,       null        ) ;
    this.unit       = readOption( options.unit ,        ''          ) ;
    this.colorbar   = readOption( options.colorbar,     false       ) ;
    this.phase      = readOption( options.phase,        null        ) ;
    this.phase      = readOption( options.phaseField,   this.phase  ) ;

    this.cblborder   = readOption( options.cblborder,   40          ) ;
    this.cbrborder   = readOption( options.cbrborder,   40          ) ;

    if ( this.canvas != null ){
        this.canvasTarget = true ;
        this.context = this.canvas.getContext("2d");
        this.width = this.canvas.width ;
        this.height = this.canvas.height ;
    }

    if ( this.prevTarget == undefined ){
        this.pltTipt = false ;
    }

    this.channelMultiplier = getChannelMultiplier(this.channel) ;

    this.ftipt  = new FloatRenderTarget( this.width, this.height ) ;
    this.stipt  = new FloatRenderTarget( this.width, this.height ) ;
    this.prob   = new FloatRenderTarget( this.width, this.height ) ;
    this.clrm   = this.colormaps[this.clrmName] ;

/*------------------------------------------------------------------------
 * tiptInit solver
 *------------------------------------------------------------------------
 */
    this.tiptInit = new Solver(
            {
                vertexShader:   vertShader.value,
                fragmentShader: tiptInitShader.value,
                renderTargets : {
                    ftipt : { location : 0 , target : this.ftipt } ,
                    stipt : { location : 1 , target : this.stipt } ,
                } ,
            }) ;

/*------------------------------------------------------------------------
 * tipts solver
 *------------------------------------------------------------------------
 */
    if ( this.prevTarget != undefined ){
        this.tipts  = new Solver(
                {
                    vertexShader:   vertShader.value,
                    fragmentShader: tiptShader.value,
                    uniforms: {
                       vPrv    : { type: "t",
                                   value: this.prevTarget           } ,
                       vCur    : { type: "t",
                                   value: this.target               } ,
                       tips    : { type: "t",
                                   value: this.stipt                } ,
                       path    : { type: "i",  value: this.pltTipt  } ,

                       /* Potential Threshold */
                       Uth     : { type: "f",
                                   value: this.tiptThreshold        } ,

                    } ,
                    renderTargets :{
                        ftipt   : { location : 0 , target : this.ftipt} ,
                    } ,
                    clear   : true ,
                } ) ;
    }

/*------------------------------------------------------------------------
 * write stipt to ftipt
 *------------------------------------------------------------------------
 */
    this.stip2ftip = new Solver({
                vertexShader    : vertShader.value,
                fragmentShader  : wA2bShader.value,
                uniforms:{
                    map: { type: 't', value: this.ftipt     }
                },
                renderTargets : {
                    FragColor : { location : 0 , target : this.stipt} ,
                }
            } ) ;
/*------------------------------------------------------------------------
 * bcanvas
 *------------------------------------------------------------------------
 */
    this.bcanvas = document.createElement('canvas') ;
    this.bcanvas.width = this.width ;
    this.bcanvas.height = this.height ;
    this.bcontext = this.bcanvas.getContext('2d') ;
 
/*------------------------------------------------------------------------
 * plot solver
 *------------------------------------------------------------------------
 */
    if ( this.phase != undefined ){
        this.plot =
            new Solver(  {
                vertexShader    : vertShader.value,
                fragmentShader  : dispPhasShader.value,
                uniforms: {
                    phas    : { type: 't', value: this.phase        } ,
                    minValue: { type: 'f', value: this.minValue     } ,
                    maxValue: { type: 'f', value: this.maxValue     } ,
                    tiptColor:{ type: 'v3',value: this.tiptColor    } ,
                    tipt    : { 
                        type: 's', 
                        value: this.ftipt,       
                        wrapS : 'mirrored_repeat',
                        wrapT : 'mirrored_repeat'                   
                    } ,
                    tiptThickness : {
                        type : 'f',
                        value   : this.tiptThicknes                 } ,
                    map     : { type: 't', value: this.target       } ,
                    clrm    : { type: 't', value: this.clrm         } ,
                    prob    : { type: 't', value: this.prob         } ,
                    channelMultiplier : { type: 'v4',
                    value: this.channelMultiplier                   } ,
                    } ,
                    
                    canvas: this.bcanvas ,
                } ,
            ) ;
    }else{
        this.plot =
            new Solver( {
                vertexShader    : vertShader.value,
                fragmentShader  : dispShader.value,
                uniforms: {
                    minValue: { type: 'f', value: this.minValue     } ,
                    maxValue: { type: 'f', value: this.maxValue     } ,
                    tiptColor:{ type: 'v3',value: this.tiptColor    } ,
                    tipt    : { 
                        type: 's', 
                        value: this.ftipt , 
                        wrapS : 'mirrored_repeat',
                        wrapT : 'mirrored_repeat'
                    } ,
                    tiptThickness : {
                        type : 'f',
                        value   : this.tiptThickness                } ,
                    map     : { type: 't', value: this.target       } ,
                    clrm    : { type: 't', value: this.clrm         } ,
                    prob    : { type: 't', value: this.prob         } ,
                    channelMultiplier : { type: 'v4',
                    value: this.channelMultiplier                   } ,
                    } ,
                    canvas : this.bcanvas ,
                } ) ;
    }

/*------------------------------------------------------------------------
 * foreground
 *------------------------------------------------------------------------
 */
    this.fcanvas = document.createElement('canvas') ;
    this.fcanvas.width = this.width ;
    this.fcanvas.height = this.height ;
    this.fcontext = this.fcanvas.getContext('2d') ;

/*------------------------------------------------------------------------
 * messages to appear on foreground
 *------------------------------------------------------------------------
 */
    this.messages = [] ;
    this.addMessage = function(message, x, y, options ){
        var msg = new Message(message,x,y,options) ;
        this.messages.push(msg) ;
        this.initForeground() ;
        return msg ;
    }

/*------------------------------------------------------------------------
 * write all messages
 *------------------------------------------------------------------------
 */
    this.writeMessages = function(){
        for (var i=0 ; i < this.messages.length; i++){
            var message = this.messages[i] ;
            if (message.visible){
                this.fcontext.font = message.font ;
                this.fcontext.fillStyle = message.style ;
                this.fcontext.textAlign = message.align ;
                this.fcontext.fillText( message.text,
                                        this.canvas.width*message.x,
                                        this.canvas.height*message.y );
            }
        }
    }

/*------------------------------------------------------------------------
 * drawProbePosition
 *------------------------------------------------------------------------
 */
    this.drawProbePosition = function (){
        if (!this.probeVisible)
            return ;
        this.fcontext.strokeStyle = this.probeColor;
        this.fcontext.beginPath();
        this.fcontext.arc(
            this.canvas.width*this.probePosition[0],
            this.canvas.height*(1-this.probePosition[1]) ,
            this.canvas.width*0.02 ,
            0.,
            Math.PI * 2.0 ) ;
        this.fcontext.stroke() ;

        this.fcontext.moveTo(
            this.canvas.width*this.probePosition[0]
                - this.canvas.width*0.02,
            this.canvas.height*(1-this.probePosition[1])
        ) ;

        this.fcontext.lineTo(
            this.canvas.width*this.probePosition[0]
                + this.canvas.width*0.02,
            this.canvas.height*(1-this.probePosition[1])
        ) ;
        this.fcontext.stroke() ;
        this.fcontext.moveTo(
            this.canvas.width*this.probePosition[0],
            this.canvas.height*(1-this.probePosition[1] )
                    - this.canvas.width*0.02
        ) ;

        this.fcontext.lineTo(
                this.canvas.width*this.probePosition[0],
                this.canvas.height*(1-this.probePosition[1] )
                    + this.canvas.width*0.02
        ) ;
        this.fcontext.stroke() ;


        return ;
    }

/*------------------------------------------------------------------------
 * drawColorbar
 *------------------------------------------------------------------------
 */
    this.drawColorbar = function() {
        if (this.colorbar){
            this.fcontext.font = '10pt Arial' ;
            this.fcontext.fillStyle = "#FFFFFF" ;
            this.fcontext.fillRect( this.canvas.width/4 - this.cblborder ,
                                    this.canvas.height - 38,
                                    this.canvas.width/2 
                                        + this.cblborder
                                        + this.cbrborder
                                        ,
                                    30 ) ;

            this.fcontext.fillStyle = "#000000" ;
            this.fcontext.textAlign = 'end' ;
            this.fcontext.fillText(     this.minValue + this.unit,
                                    this.canvas.width/4,
                                    this.canvas.height - 30 + 13) ;
            this.fcontext.textAlign = 'start' ;
            this.fcontext.fillText(     this.maxValue + this.unit,
                                    this.canvas.width*3/4,
                                    this.canvas.height - 30 + 13) ;


        this.fcontext.drawImage(    this.clrm.image,this.canvas.width/4,
                                    this.canvas.height - 30 ,
                                    this.canvas.width/2,16) ;
        }
    }

/*------------------------------------------------------------------------
 * setColorbarVisiblity
 *------------------------------------------------------------------------
 */
 this.setColorbarVisiblity  = function(v){
     this.colorbar = readOption(v, this.colorbar) ;
     this.initForeground() ;
 }
/*------------------------------------------------------------------------
 * toggleColorbar
 *------------------------------------------------------------------------
 */
    this.toggleColorbar = function(){
        this.colorbar = !this.colorbar ;
        this.initForeground() ;
    }

/*------------------------------------------------------------------------
 * showColorbar
 *------------------------------------------------------------------------
 */
    this.showColorbar = function(){
        this.colorbar = true ;
        this.initForeground() ;
    }

/*------------------------------------------------------------------------
 * hideColorbar
 *------------------------------------------------------------------------
 */
    this.hideColorbar = function(){
        this.colorbar = false ;
        this.initForeground() ;
    }

/*------------------------------------------------------------------------
 * initForeground
 *------------------------------------------------------------------------
 */
    this.initForeground = function() {
        this.fcontext.clearRect(0,0,this.canvas.width,this.canvas.height) ;
        this.writeMessages() ;
        this.drawProbePosition() ;
        this.drawColorbar() ;
    }
/*------------------------------------------------------------------------
 * setColormap
 *------------------------------------------------------------------------
 */
    this.setColormap = function(clrmName){
        if (clrmName != undefined ){
            this.clrmName = clrmName ;
        }
        this.clrm = this.colormaps[this.clrmName] ;
        this.plot.setUniform( 'clrm', this.clrm ) ;
        this.initForeground() ;
    }

/*------------------------------------------------------------------------
 * setMinValue
 *------------------------------------------------------------------------
 */
    this.setMinValue = function(val){
        this.minValue = val ;
        this.plot.setUniform('minValue',this.minValue );
        this.initForeground() ;
    }

/*------------------------------------------------------------------------
 * setMaxValue
 *------------------------------------------------------------------------
 */
    this.setMaxValue = function(val){
        this.maxValue = val ;
        this.plot.setUniform('maxValue',this.maxValue);
        this.initForeground() ;
    }

/*------------------------------------------------------------------------
 * setChannel
 *------------------------------------------------------------------------
 */
    this.setChannel = function(channel){
        this.channel = channel ;
        this.channelMultiplier = getChannelMultiplier( this.channel ) ;
        this.plot.setUniform('channelMultiplier',
            this.channelMultiplier );
    }

/*------------------------------------------------------------------------
 * setTiptVisiblity
 *------------------------------------------------------------------------
 */
    this.setTiptVisiblity = function( tipt ){
        this.pltTipt = tipt ;
        this.tipts.setUniform('path' , this.pltTipt ) ;
        this.tiptInit.render() ;
    }

/*------------------------------------------------------------------------
 * setTiptColor
 *------------------------------------------------------------------------
 */
    this.setTiptColor= function(color){
        this.tiptColor = color ;
        this.plot.setUniform('tiptColor',
            this.tiptColor );
    }

/*------------------------------------------------------------------------
 * setTiptThreshold
 *------------------------------------------------------------------------
 */
    this.setTiptThreshold = function(threshold){
        this.tiptThreshold = threshold ;
        this.tipts.setUniform('Uth',
            this.tiptThreshold ) ;
    }

/*------------------------------------------------------------------------
 * setTiptThickness
 *------------------------------------------------------------------------
 */
    this.setTiptThickness = function(thickness){
        this.tiptThickness = readOption(thickness, this.tiptThickness ) ;
        this.plot.setUniform('tiptThickness', this.tiptThickness ) ;
    }

/*------------------------------------------------------------------------
 * setProbePosition
 *------------------------------------------------------------------------
 */
    this.setProbePosition = function(probePosition){
        if (probePosition != undefined ){
            this.probePosition = probePosition ;
        }
        this.initForeground() ;
    }

/*------------------------------------------------------------------------
 * setProbVisiblity
 *------------------------------------------------------------------------
 */
    this.setProbeVisiblity = function(flag){
        if ( flag != undefined ){
            this.probeVisible = flag ;
            this.initForeground() ;
        }
    }

/*------------------------------------------------------------------------
 * setProbColor
 *------------------------------------------------------------------------
 */
    this.setProbeColor = function(clr){
        if (clr != undefined ){
            this.probeColor = clr ;
            this.initForeground() ;
        }
    }

/*------------------------------------------------------------------------
 * init
 *------------------------------------------------------------------------
 */
    this.init = function(){
        this.initForeground() ;
        this.tiptInit.render() ;
    }

/*------------------------------------------------------------------------
 * initialize
 *------------------------------------------------------------------------
 */
    this.initialize = this.init ;

/*------------------------------------------------------------------------
 * setSize
 *------------------------------------------------------------------------
 */
    this.setSize = function(width, height){
        this.ftipt.resize( width, height ) ;
        this.stipt.resize( width, height ) ;
        this.prob.resize( width, height ) ;
        this.init() ;
    }

/*------------------------------------------------------------------------
 * tiptUpdate
 *------------------------------------------------------------------------
 */
    this.updateTipt = function(){
        if ( this.pltTipt ){
            this.tipts.render() ;
            this.stip2ftip.render() ;
        }
        return ;
    }

/*------------------------------------------------------------------------
 * render
 *------------------------------------------------------------------------
 */
    this.render = function(){
        this.updateTipt() ;
        this.plot.render() ;

        this.context.clearRect(0,0,this.canvas.width, this.canvas.height ) ;
        this.context.drawImage(this.bcanvas,0,0) ;
        this.context.drawImage(this.fcanvas, 0,0) ;

        return ;
    }

} /* end of Plot2D */

/*========================================================================
 * VolumeRayCaster({options}):
 *      - target            :   a texture to plot from
 *      - canvas            :   a canvas to draw on
 *      - mx                :   number of z-slices in x-direction
 *      - my                :   number of z-slices in y-direction
 *      - alphaCorrection   :   alpha-correction
 *      - noSteps           :   number of ray-casting steps
 *      - channel           :   the channel to draw colors from
 *      - threshold         :   the drawing threshold value
 *      - minValue          :   minimum value in the colorbar range
 *      - maxValue          :   maximum value in the colorbar range
 *      - colorbar          :   name of the colorbar to calc. colors
 *      - lights            :   a v3v of directional flood lights
 *      - phaseField        :   phase-field texture when necessary
 *      - compressionMap    :   compression map of a compressed structure
 *      - decompressionMap  :   decompression map of a compressed structure
 *      - onCtrlClick       :   callback function for Ctrl+Click events
 *      - clickPenetration  :   clickPenetration factor
 *========================================================================
 */
function VolumeRayCaster(opts={}){

/*------------------------------------------------------------------------
 * setting up colormaps
 *------------------------------------------------------------------------
 */
    this.colormapList   = getColormapList() ;

    this.colormaps      = getColormaps(this.colormapList) ;

/*------------------------------------------------------------------------
 * reading options
 *------------------------------------------------------------------------
 */
    this.target = readOption(opts.target,null,
            'Error : A FloatRenderTarget must be provided for '+
            'plotting.\n'+
            'No VolumeRayCaster can be defined!'                    ) ;
    if (this.target == null ){
        return null ;
    }

    this.prevTarget = readOption(opts.prevTarget, null ) ;

    this.canvas = readOption(opts.canvas, null,
        'Error: No canvas for VolumeRayCaster was provided.\n'+
        'No VolumeRayCaster can be defined!'                        ) ;
    if (this.canvas == null){
        return null ;
    }

    this.dispWidth  = this.canvas.width ;
    this.dispHeight = this.canvas.height ;
    this.context    = this.canvas.getContext('2d') ;

    this.mx = readOption( opts.mx, 1,
        'Warning : Number of z-slices in x-direction '+
        'of structure/mx was not provided. Assuming mx = 1. '       ) ;

    this.my = readOption(opts.my, 1,
        'Warning : Number of z-slices in y-direction '+
        'of structure/my was not provided. Assuming my = 1. '       ) ;

    this.alphaCorrection = readOption(opts.alphaCorrection, 0.5     ) ;
    this.fov            = readOption(opts.fieldOfView, Math.PI*0.1  ) ;
    this.fov            = readOption(opts.fov   , this.fov          ) ;
    this.nearField      = readOption(opts.nearField,    0.01        ) ;
    this.farField       = readOption(opts.farField,     100         ) ;
    this.noSteps        = readOption(opts.noSteps   , 50            ) ;
    this.channel        = readOption(opts.channel   , 'r'           ) ;
    this.threshold      = readOption(opts.threshold , 0.            ) ;
    this.minValue       = readOption(opts.minValue  , 0.            ) ;
    this.maxValue       = readOption(opts.maxValue  , 1.            ) ;
    this.unit           = readOption(opts.unit      , ''            ) ;
    this.clrmName       = readOption(opts.colormap  , 'jet'         ) ;
    this.scale          = readOption(opts.scale ,   1.0             ) ;
    this.clickPenetration = readOptions( opts.clickPenetration, 0   ) ;
    this.clickPenetration = readOptions( opts.cp, this.clickPenetration ) ;

    this.clrm   = this.colormaps[this.clrmName] ;

    this.colorbar       = readOption(opts.colorbar  , false         ) ;

    this.dfls           = readOption(opts.floodLights, []           ) ;
    this.noDfls = Math.floor(this.dfls.length/3) ;

    this.ptls           = readOption(opts.pointLights, []           ) ;
    this.noPtls         = Math.floor(this.ptls.length/3) ;
    this.lightShift     = readOption(opts.lightShift,   0           ) ;

    this.dfls.push(0,0,0) ; /* this is added to avoid problems
                               when no light is provided        */
    this.ptls.push(0,0,0) ;

    this.phaseField     = readOption(opts.phaseField , null         ) ;
    this.compMap        = readOption(opts.compressionMap, null      ) ;

    if (this.compMap != null ){
        this.useCompMap = true ;
        this.width  = this.compMap.width ;
        this.height = this.compMap.height ;
    }else{
        this.useCompMap = false ;
        this.width  = this.target.width ;
        this.height = this.target.height ;
    }

    function ifNullThenUnit(trgt){
        if (trgt == null ){
            return new FloatRenderTarget(1,1) ;
        }else{
            return trgt ;
        }
    }
    if( this.phaseField != null ){
        this.usePhaseField = true ;
    }else{
        this.usePhaseField = false ;
    }
    this.phaseField = ifNullThenUnit(this.phaseField) ;
    this.compMap    = ifNullThenUnit(this.compMap   ) ;
    this.prevTarget = ifNullThenUnit(this.prevTarget) ;


    /* callback function for control click */
    this.onCtrlClick = readOption(opts.onCtrlClick, function(){}    ) ;

    this.channelMultiplier = getChannelMultiplier( this.channel ) ;

/*------------------------------------------------------------------------
 * coordinate and light
 *------------------------------------------------------------------------
 */
    this.crdtTxt = new FloatRenderTarget(this.width, this.height) ;
    this.crdt   = new  Solver( {
        vertexShader    : vertShader.value,
        fragmentShader  : vrcCrdShader.value,
	uniforms : {
            mx          : {
                type    : 'f',
                value   : this.mx
            } ,
            my          : {
                type    : 'f',
                value   : this.my
            } ,
        } ,
        renderTargets : {
            crd : { location : 0 , target : this.crdtTxt  } ,
        }
    } ) ;
    this.crdt.render() ;

/*------------------------------------------------------------------------
 * light
 *------------------------------------------------------------------------
 */
    this.lightTxt = new FloatRenderTarget(this.width, this.height) ;
    this.light = new Solver({
        vertexShader    :   vertShader.value ,
        fragmentShader  :   vrcLgtShader.value ,
        uniforms : {
            crdtTxt     : {
                type    : 't',
                value   : this.crdtTxt
            } ,
            phaseTxt    : {
                type    : 's',
                value   : this.phaseField,
                //minFilter: 'nearest',
                //magFilter: 'nearest',
            } ,
            target      : {
                type    : 's',
                value   : this.target ,
                minFilter: 'nearest',
                magFilter: 'nearest',
            } ,
            usePhaseField: {
                type    : 'b',
                value   : this.usePhaseField
            } ,
            mx          : {
                type    : 'f',
                value   : this.mx
            } ,
            my          : {
                type    : 'f',
                value   : this.my,
            },
            minValue    : {
                type    : 'f',
                value   : this.minValue
            } ,
            maxValue    : {
                type    : 'f' ,
                value   : this.maxValue
            } ,
            threshold   : {
                type    : 'f',
                value   : this.threshold
            } ,
            dfls        : {
                type    : 'f3v',
                value   : this.dfls
            } ,
            noDfls      : {
                type    : 'i',
                value       : this.noDfls
            } ,
            ptls        : {
                type    : 'f3v',
                value   : this.ptls,
            } ,
            noPtls      : {
                type    : 'i',
                value   : this.noPtls,
            } ,
            alphaCorrection : {
                type    : 'f',
                value   : this.alphaCorrection
            } ,
            channelMultiplier : {
                type    : 'v4',
                value   : this.channelMultiplier
            } ,
            lightShift  : {
                type    : 'f',
                value   : this.lightShift,
            } ,
        } ,
        renderTargets: {
            light   : { location : 0 , target : this.lightTxt   } ,
        }
    } ) ;
    this.light.render() ;

/*------------------------------------------------------------------------
 * geometry
 *------------------------------------------------------------------------
 */
    var geometry = new UnitCubeGeometry() ;

/*------------------------------------------------------------------------
 * transformation matrices
 *------------------------------------------------------------------------
 */
    /* modelMatrix  */
    var modelMatrix = mat4.create() ;
    mat4.identity(  modelMatrix                 ) ;

    mat4.rotate(    modelMatrix, modelMatrix,
                    -Math.PI/2.,[1.,0.,0.]      ) ;

    mat4.translate( modelMatrix, modelMatrix,
                    [-0.5,-0.5,-0.5]            ) ;

    /* viewMatrix   */
    var viewMatrix = mat4.create() ;

    mat4.rotate(    viewMatrix,viewMatrix,
                    Math.PI/3.0,[1,1,1]         ) ;

    mat4.identity(  viewMatrix                  ) ;

    mat4.lookAt(    viewMatrix,
                    [2,2,2],[0,0,0],[0,1,0]     ) ;

    var controler = new OrbitalCameraControl(
        viewMatrix,
        4.0 , this.canvas,
        {
            prevx: -.4,
            prevy: 0.4,
        }
    ) ;


    /* projectionMatrix */
    var projectionMatrix = mat4.create() ;
    mat4.identity(      projectionMatrix        ) ;
    mat4.perspective (  projectionMatrix ,
                        this.fov, this.dispWidth/this.dispHeight,
                        this.nearField, this.farField               ) ;

/*------------------------------------------------------------------------
 * pass1
 *------------------------------------------------------------------------
 */
    this.backfaceCrdTxt = new FloatRenderTarget(this.dispWidth,
                                                this.dispHeight     ) ;
    this.pass1 = new Solver({
        vertexShader    : vrc1VShader.value,
        fragmentShader  : vrc1FShader.value,
        uniforms : {
            modelMatrix : {
                type    : 'mat4',
                value   : modelMatrix
            } ,
            viewMatrix  : {
                type    : 'mat4',
                value   : viewMatrix
            } ,
            projectionMatrix : {
                type    : 'mat4',
                value   : projectionMatrix
            } ,
        } ,
        geometry        : geometry ,
        cullFacing      : true ,
        cullFace        : 'front',
        depthTest       : 'true',
        renderTargets   : {
            back_face_Crds : {
                location :0 ,
                target  : this.backfaceCrdTxt
            } ,
        } ,
    } ) ;

/*------------------------------------------------------------------------
 * pass2
 *------------------------------------------------------------------------
 */
    this.pass2  = new Solver({
        vertexShader    : vrc2VShader.value,
        fragmentShader  : vrc2FShader.value,
        uniforms    : {
            modelMatrix : {
                type    : 'mat4',
                value   : modelMatrix
            } ,
            viewMatrix  : {
                type    : 'mat4',
                value   : viewMatrix
            } ,
            projectionMatrix : {
                type    : 'mat4',
                value   : projectionMatrix
            } ,
            backfaceCrdTxt : {
                type    : 's',
                value   : this.backfaceCrdTxt ,
                minFilter : 'nearest' ,
                magFilter : 'nearest' ,
                wrapS   : 'clamp_to_edge' ,
                wrapT   : 'clamp_to_edge' ,
            } ,
            phaseTxt    : {
                type    : 's',
                value   : this.phaseField,
                minFilter: 'nearest',
                magFilter: 'nearest',
            } ,
            target      : {
                type    : 's',
                value   : this.target ,
                minFilter: 'nearest',
                magFilter: 'nearest',
            } ,
            compMap     : {
                type    : 't',
                value   : this.compMap
            } ,
            lightTxt    : {
                type    : 't' ,
                value   : this.lightTxt ,
            } ,
            clrm        : {
                type    : 't',
                value   : this.clrm,
            } ,
            usePhaseField: {
                type    : 'b',
                value   : this.usePhaseField
            } ,
            useCompMap  : {
                type    : 'b',
                value   : this.useCompMap
            } ,
            minValue    : {
                type    : 'f',
                value   : this.minValue
            } ,
            maxValue    : {
                type    : 'f',
                value   : this.maxValue
            } ,
            threshold   : {
                type    : 'f',
                value   : this.threshold
            } ,
            channelMultiplier: {
                type    : 'v4',
                value   : this.channelMultiplier
            } ,
            alphaCorrection : {
                type    : 'f',
                value   : this.alphaCorrection
            } ,
            noSteps       : {
                type    : 'i',
                value   : this.noSteps
            } ,
            mx          : {
                type    : 'f' ,
                value   : this.mx ,
            } ,
            my          : {
                type    : 'f',
                value   : this.my ,
            } ,
            lightShift  : {
                type    : 'f',
                value   : this.lightShift ,
            } ,
        } ,
        geometry        : geometry ,
        cullFacing      : true ,
        cullFace        : 'back' ,
        depthTest       : true ,
        clear           : true ,
    } ) ;

/*------------------------------------------------------------------------
 * projectedCrds
 *------------------------------------------------------------------------
 */
    this.projectedCrds = new FloatRenderTarget(
        this.dispWidth,
        this.dispHeight,
    ) ;

    this.projectCrds = new Solver({
        vertexShader    :   vrc2VShader.value,
        fragmentShader  :   vrcPCShader.value,
        uniforms :{
            modelMatrix : {
                type    : 'mat4',
                value   : modelMatrix
            } ,
            viewMatrix  : {
                type    : 'mat4',
                value   : viewMatrix
            } ,
            projectionMatrix : {
                type    : 'mat4',
                value   : projectionMatrix
            } ,
            backfaceCrdTxt : {
                type    : 's',
                value   : this.backfaceCrdTxt ,
                minFilter : 'nearest' ,
                magFilter : 'nearest' ,
                wrapS   : 'clamp_to_edge' ,
                wrapT   : 'clamp_to_edge' ,
            } ,
            phaseTxt    : {
                type    : 's',
                value   : this.phaseField,
                minFilter: 'nearest',
                magFilter: 'nearest',
            } ,
            target      : {
                type    : 's',
                value   : this.target ,
                minFilter: 'nearest',
                magFilter: 'nearest',
            } ,
            usePhaseField: {
                type    : 'b',
                value   : this.usePhaseField
            } ,
            minValue    : {
                type    : 'f',
                value   : this.minValue
            } ,
            maxValue    : {
                type    : 'f',
                value   : this.maxValue
            } ,
            threshold   : {
                type    : 'f',
                value   : this.threshold
            } ,
            channelMultiplier: {
                type    : 'v4',
                value   : this.channelMultiplier
            } ,
            noSteps       : {
                type    : 'i',
                value   : this.noSteps
            } ,
            mx          : {
                type    : 'f' ,
                value   : this.mx ,
            } ,
            my          : {
                type    : 'f',
                value   : this.my ,
            } ,
            clickPenetration : {
                type    : 'f',
                value   : this.clickPenetration ,
            } ,
        } ,
        renderTargets :{
            FragColor : {
                location    : 0,
                target      : this.projectedCrds ,
            } ,
        } ,
        geometry        : geometry ,
        cullFacing      : true ,
        cullFace        : 'back' ,
        depthTest       : true ,
        clear           : true ,
    } ) ;

/*------------------------------------------------------------------------
 * setClickPenetration
 *------------------------------------------------------------------------
 */
    this.setClickPenetration = function(cp){
        if ( cp != undefined ){
            this.clickPenetration = cp ;
        }
        this.projectCrds.setUniform('clickPenetration', 
                this.clickPenetration) ;
        this.projectCrds.render() ;
    }
    this.setCP = this.setClickPenetration ;
/*------------------------------------------------------------------------
 * clickCoordinate
 *------------------------------------------------------------------------
 */
    this.clickCoordinates   = new FloatRenderTarget(1,1) ;
    this.clickVoxelCrd      = new FloatRenderTarget(1,1) ;
    this.clickPosition      = [0.,0.] ;
    this.clickVoxelProbe    = new Probe(this.clickVoxelCrd) ; 
    this.clickVoxelPosition = [0.,0.] ;

    this.clickCoordinator = new Solver({
        vertexShader    : vertShader.value ,
        fragmentShader  : vrcClickCrdShader.value ,
        uniforms        : {
            projectedCrds : {
                type        : 't' ,
                value       : this.projectedCrds ,
            } ,
            clickPosition : {
                type        : 'v2' ,
                value       : this.clickPosition ,
            } ,
        } ,
        renderTargets   : {
            clickCoordinates : {
                location    : 0 ,
                target      : this.clickCoordinates ,
            }
        } ,
        clear : true ,
    } ) ;

    this.clickVoxelCoordinator = new Solver({
        vertexShader    : vertShader.value ,
        fragmentShader  : vrcClickVoxelCrdShader.value,
        uniforms   : {
            mx  : { type : 'f', value : this.mx } ,
            my  : { type : 'f', value : this.my } ,
            useCompMap : { type : 'b', value : this.useCompMap },
            compMap : { type : 't', value : this.compMap } ,
            clickCoordinates : { type : 't', 
                value :  this.clickCoordinates } ,
        } ,
        renderTargets : { 
            voxelPos : { location : 0 , target : this.clickVoxelCrd } ,
        } ,
        clear : true ,
    } ) ;

/*------------------------------------------------------------------------
 * updateClickCoordinate
 *------------------------------------------------------------------------
 */
    this.updateClickCoordinates = function(clickPosition){
        this.clickPosition = clickPosition ;
        controler.update() ;
        mat4.scale(
            viewMatrix,
            viewMatrix, [
                this.scale,
                this.scale,
                this.scale,
                this.scale
            ] ) ;

        this.pass1.setUniform(
            'viewMatrix',
            viewMatrix
        ) ;
        this.projectCrds.setUniform(
            'viewMatrix',
            viewMatrix
        ) ;
        this.clickCoordinator.setUniform(
            'clickPosition',
            this.clickPosition ,
        ) ;

        this.pass1.render() ;
        this.projectCrds.render() ;
        this.clickCoordinator.render() ;
        this.clickVoxelCoordinator.render() ;
    }

    this.updateClickPosition = this.updateClickCoordinates ;

/*------------------------------------------------------------------------
 * getClickVoxelPosition
 *------------------------------------------------------------------------
 */
    this.getClickVoxelPosition = function(){
        var voxel = this.clickVoxelProbe.getPixel() ;
        this.clickVoxelPosition[0] = voxel[0] ;
        this.clickVoxelPosition[1] = voxel[1] ;
        return this.clickVoxelPosition ;
    }
    this.getClickVoxel = this.getClickVoxelPosition ;

/*------------------------------------------------------------------------
 * foreground
 *------------------------------------------------------------------------
 */
    this.fcanvas = document.createElement('canvas') ;
    this.fcanvas.width = this.canvas.width ;
    this.fcanvas.height= this.canvas.height ;
    this.fcontext = this.fcanvas.getContext('2d') ;

/*------------------------------------------------------------------------
 * messages to appear on foreground
 *------------------------------------------------------------------------
 */
    this.messages = [] ;
    this.addMessage = function(message, x, y, options ){
        var msg = new Message( message, x,y, options);
        this.messages.push(msg) ;
        this.initForeground() ;
        return msg ;
    }

/*------------------------------------------------------------------------
 * write all messages
 *------------------------------------------------------------------------
 */
    this.writeMessages = function(){
        for (var i=0 ; i < this.messages.length; i++){
            var message = this.messages[i] ;
            if (message.visible){
                this.fcontext.font = message.font ;
                this.fcontext.fillStyle = message.style ;
                this.fcontext.textAlign = message.align ;
                this.fcontext.fillText( message.text,
                                        this.canvas.width*message.x,
                                        this.canvas.height*message.y );
            }
        }
    }

/*------------------------------------------------------------------------
 * drawColorbar
 *------------------------------------------------------------------------
 */
    this.drawColorbar = function() {
        if (this.colorbar){
            this.fcontext.fillStyle = "#FFFFFF" ;
            this.fcontext.fillRect( this.canvas.width/4 - 40 ,
                                    this.canvas.height - 38,
                                    this.canvas.width/2 + 2*40  ,
                                    30 ) ;

            this.fcontext.fillStyle = "#000000" ;
            this.fcontext.textAlign = 'end' ;
            this.fcontext.fillText(     this.minValue + this.unit,
                                    this.canvas.width/4,
                                    this.canvas.height - 30 + 13) ;
            this.fcontext.textAlign = 'start' ;
            this.fcontext.fillText(     this.maxValue + this.unit,
                                    this.canvas.width*3/4,
                                    this.canvas.height - 30 + 13) ;


        this.fcontext.drawImage(    this.clrm.image,this.canvas.width/4,
                                    this.canvas.height - 30 ,
                                    this.canvas.width/2,16) ;
        }
    }

/*------------------------------------------------------------------------
 * showColorbar
 *------------------------------------------------------------------------
 */
    this.showColorbar = function(){
        this.colorbar = true ;
        this.initForeground() ;
    }

/*------------------------------------------------------------------------
 * hideColorbar
 *------------------------------------------------------------------------
 */
    this.hideColorbar = function(){
        this.colorbar = false ;
        this.initForeground() ;
    }

/*------------------------------------------------------------------------
 * initForeground
 *------------------------------------------------------------------------
 */
    this.initForeground = function() {
        this.fcontext.clearRect(    0,  0,
                                    this.canvas.width,
                                    this.canvas.height  ) ;
        this.writeMessages() ;
        this.drawColorbar() ;
    }

/*------------------------------------------------------------------------
 * setLightShift
 *------------------------------------------------------------------------
 */
    this.setLightShift = function(lf){
        this.lightShift = readOption(lf,    this.lightShift ) ;
        this.light.setUniform('lightShift', this.lightShift ) ;
        this.pass2.setUniform('lightShift', this.lightShift ) ;
        this.light.render() ;
    }

/*------------------------------------------------------------------------
 * setColormap
 *------------------------------------------------------------------------
 */
    this.setColormap = function(clrmName){
        if (clrmName != undefined ){
            this.clrmName = clrmName ;
        }
        this.clrm = this.colormaps[this.clrmName] ;
        this.pass2.setUniform( 'clrm', this.clrm ) ;
        this.initForeground() ;
    }

/*------------------------------------------------------------------------
 * setMinValue
 *------------------------------------------------------------------------
 */
    this.setMinValue = function(val){
        this.minValue = val ;
        this.pass2.setUniform('minValue', this.minValue ) ;
        this.light.setUniform('minValue', this.minValue ) ;
        this.light.render() ;
    }

/*------------------------------------------------------------------------
 * setMaxValue
 *------------------------------------------------------------------------
 */
    this.setMaxValue = function(val){
        this.maxValue = val ;
        this.pass2.setUniform('maxValue', this.maxValue ) ;
        this.light.setUniform('maxValue', this.maxValue ) ;
        this.light.render() ;
    }

/*-------------------------------------------------------------------------
 * setThreshold
 *-------------------------------------------------------------------------
 */
    this.setThreshold = function(val){
        this.threshold = readOption(val, this.threshold ) ;
        this.light.setUniform('threshold', this.threshold ) ;
        this.pass2.setUniform('threshold', this.threshold ) ;
    }

/*------------------------------------------------------------------------
 * setAlphaCorrection
 *------------------------------------------------------------------------
 */
    this.setAlphaCorrection = function(ac){
        this.alphaCorrection = readOption(ac, this.alphaCorrection) ;
        this.light.setUniform('alphaCorrection', this.alphaCorrection) ;
        this.pass2.setUniform('alphaCorrection', this.alphaCorrection) ;
        this.light.render() ;
    }

/*------------------------------------------------------------------------
 * setNoSteps
 *------------------------------------------------------------------------
 */
    this.setNoSteps = function(_ns){
        this.noSteps = readOption(_ns, this.noSteps) ;
        this.pass2.setUniform('noSteps', this.noSteps ) ;
    }

/*------------------------------------------------------------------------
 * render
 *------------------------------------------------------------------------
 */
    this.rrender = function(){
        var s = this.scale ;
        if (gl.canvas.width!=this.canvas.width) {
            gl.canvas.width = this.canvas.width ;
        }if (gl.canvas.height != this.canvas.height){
            gl.canvas.height= this.canvas.height ;
        }
        gl.viewport(0,0, this.canvas.width, this.canvas.height) ;
        this.context.clearRect(  0 ,   0,
                                this.canvas.width,
                                this.canvas.height  ) ;
        controler.update() ;
        mat4.scale( viewMatrix, viewMatrix, [s,s,s,s] ) ;
        this.pass1.setUniform('viewMatrix', viewMatrix) ;
        this.pass2.setUniform('viewMatrix', viewMatrix) ;

        this.pass1.render() ;
        this.pass2.render() ;
        this.context.drawImage(  gl.canvas,0,0       ) ;
        this.context.drawImage(  this.fcanvas, 0,0   ) ;
    }

    this.render = function(){
        this.rrender() ;
        this.rrender() ;
    }
}

/*========================================================================
 * Probe  : probe a location for the value of a channel
 *
 * options:
 *      - renderer  : renderer to be used (compulsory)
 *      - target    : render target to be probed ( compulsory )
 *      - channel   : preferred probed channel (r,g,b,a -- default = a )
 *      - probePosition   : position of the probe
 *========================================================================
 */
function Probe( target, options={} ){
    this.channel = readOption( options.channel, 'r') ;
    this.probePosition = readOption( options.probePosition, [0.5,0.5]) ;


    if ( target != undefined ){
        this.target = target ;
    }else return null ;
    this.channelMultiplier =
        getChannelMultiplier( this.channel ) ;


    this.pixelValue = new Float32Array(4) ;

/*------------------------------------------------------------------------
 * framebuffer
 *------------------------------------------------------------------------
 */
    this.framebuffer = gl.createFramebuffer() ;
    gl.bindFramebuffer( gl.READ_FRAMEBUFFER, this.framebuffer) ;
    gl.framebufferTexture2D(gl.READ_FRAMEBUFFER, gl.COLOR_ATTACHMENT0,
                            gl.TEXTURE_2D,
                            this.target.texture, 0 ) ;
    gl.readBuffer( gl.COLOR_ATTACHMENT0 ) ;
    this.canRead    = (
        gl.checkFramebufferStatus(gl.READ_FRAMEBUFFER)
        == gl.FRAMEBUFFER_COMPLETE
    ) ;
    gl.bindFramebuffer( gl.READ_FRAMEBUFFER, null) ;

/*------------------------------------------------------------------------
 * setPosition
 *------------------------------------------------------------------------
 */
    this.setPosition = function(pos){
        this.probePosition = readOption( pos , this.probePosition ) ;
    }

/*------------------------------------------------------------------------
 * setChannel
 *------------------------------------------------------------------------
 */
    this.setChannel = function(c){
        this.channel = c ;
        this.channelMultiplier =
            getChannelMultiplier( this.channel ) ;
    }

/*------------------------------------------------------------------------
 * setTarget
 *------------------------------------------------------------------------
 */
    this.setTarget = function(trgt){
        this.target = trgt ;
    }

/*------------------------------------------------------------------------
 * getPixel : get the value of whole pixel
 *------------------------------------------------------------------------
 */
    this.getPixel = function(){
        if (this.canRead){
        var x = Math.floor(this.target.width   * this.probePosition[0]) ;
        var y = Math.floor(this.target.height  * this.probePosition[1]) ;
        gl.bindFramebuffer( gl.READ_FRAMEBUFFER, this.framebuffer) ;
        gl.framebufferTexture2D(gl.READ_FRAMEBUFFER, gl.COLOR_ATTACHMENT0,
                            gl.TEXTURE_2D,
                            this.target.texture, 0 ) ;
        gl.readBuffer( gl.COLOR_ATTACHMENT0 ) ;
        gl.readPixels(  x, y,1,1, gl.RGBA, gl.FLOAT, this.pixelValue ) ;
        gl.bindFramebuffer( gl.READ_FRAMEBUFFER, null) ;
        return this.pixelValue ;
        }else{
            return null ;
        }
    }


/*------------------------------------------------------------------------
 * get      : get the value of a channel
 *------------------------------------------------------------------------
 */
    this.get = function(){
        this.getPixel() ;

        var g = this.pixelValue[0]*this.channelMultiplier[0] +
            this.pixelValue[1]*this.channelMultiplier[1] +
            this.pixelValue[2]*this.channelMultiplier[2] +
            this.pixelValue[3]*this.channelMultiplier[3] ;
        return g ;
    }


} /* end of Probe */

/*========================================================================
 * ProbeRecorder
 *========================================================================
 */
function ProbeRecorder(probe, options){
    this.probe = probe ;
    this.sampleRate = 1 ;
    this.lastRecordedTime = -1 ;
    this.timeSeries = [] ;
    this.samples    = [] ;
    this.recording = false ;
    this.fileName ='samples.csv' ;

    if (options != undefined ){
        if (options.sampleRate != undefined){
            this.sampleRate = options.sampleRate ;
        }

        if (options.recording != undefined ){
            this.recording = options.recording ;
        }

        if (options.fileName != undefined ){
            this.fileName = options.fileName ;
        }
    }

/*------------------------------------------------------------------------
 * record(time) :   records probe with the required sample rate if
 *                  recording is requested.
 *
 *       time   :   recording current time ;
 *------------------------------------------------------------------------
 */
    this.record = function(time){
        if (this.recording){
            if (time > (this.lastRecordedTime + this.sampleRate)){
                this.timeSeries.push(time) ;
                this.lastRecordedTime = time ;
                this.samples.push(this.probe.get()) ;
            }
        }
    }

/*------------------------------------------------------------------------
 * stop         : stop recording
 *------------------------------------------------------------------------
 */
    this.stop   = function(){
        this.recording = false ;
    }

/*------------------------------------------------------------------------
 * start        : start recording
 *------------------------------------------------------------------------
 */
    this.start = function(){
        this.recording = true ;
    }

/*------------------------------------------------------------------------
 * setRecordingStatus(recording)    : set this.recording
 *------------------------------------------------------------------------
 */
    this.setRecordingStatus = function(recording){
        this.recording = recording  ;
    }

/*------------------------------------------------------------------------
 * toggleRecording  : toggle recording status
 *------------------------------------------------------------------------
 */
    this.toggleRecording = function(){
        this.recording = !(this.recording) ;
    }

/*------------------------------------------------------------------------
 * setSampleRate(sampeRate)
 *------------------------------------------------------------------------
 */
    this.setSampleRate = function(sampleRate){
        this.sampleRate = sampleRate ;
    }

/*------------------------------------------------------------------------
 * setProbe(probe)  : set a new probe
 *------------------------------------------------------------------------
 */
    this.setProbe = function(probe){
        this.probe = probe ;
    }

/*------------------------------------------------------------------------
 * setFileName(fileName)
 *------------------------------------------------------------------------
 */
    this.setFileName = function(fileName){
        this.fileName = fileName ;
    }

/*------------------------------------------------------------------------
 * resetRecording
 *------------------------------------------------------------------------
 */
    this.resetRecording = function(){
        this.timeSeries = [] ;
        this.samples    = [] ;
        this.lastRecordedTime = -1 ;
    }
/*------------------------------------------------------------------------
 * reset
 *------------------------------------------------------------------------
 */
    this.reset = function(){
        this.resetRecording() ;
    }

/*------------------------------------------------------------------------
 * save
 *------------------------------------------------------------------------
 */
    this.save = function(){
        var csvContent = "data:text;charset=utf-8,";
        for(i=0;i<this.samples.length;i++){
            csvContent+= this.timeSeries[i]+'\t'+this.samples[i]+'\n' ;
        }
        var encodedUri = encodeURI(csvContent);
        var link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", this.fileName);
        link.click() ;
    }

}   /* end of ProbeRecorder */

/*========================================================================
 * IntervalCaller
 *========================================================================
 */
function IntervalCaller( options={} ){
    this.interval = readOption(options.interval, 1      ) ;
    this.callback = readOption(options.callback, function(){} ) ;
    this.active   = readOption(options.active, false    ) ;
    this.lastCall = readOption(options.currTime, 1e10   ) ;

    this.timeDiff = 0 ;
    this.lastCall = -1e10 ;

/*------------------------------------------------------------------------
 * setInetrval
 *------------------------------------------------------------------------
 */
    this.reset = function(){
        this.lastCall = -1e10 ;
    }

/*------------------------------------------------------------------------
 * setInetrval
 *------------------------------------------------------------------------
 */
    this.setInterval = function(intr){
        this.interval = intr ;
    }

/*------------------------------------------------------------------------
 * toggleActive
 *------------------------------------------------------------------------
 */
    this.toggleActive = function(){
        this.active = !(this.active) ;
    }

/*------------------------------------------------------------------------
 * 
 *------------------------------------------------------------------------
 */
    this.toggle = function(){
        this.active = !this.active ;
    }


/*------------------------------------------------------------------------
 * setActive
 *------------------------------------------------------------------------
 */
    this.setActive = function(){
        this.active = true ;
    }

/*------------------------------------------------------------------------
 * setInactive
 *------------------------------------------------------------------------
 */
    this.setInactive = function(){
        this.active = false ;
    }

/*------------------------------------------------------------------------
 * setActivity
 *------------------------------------------------------------------------
 */
    this.setActivity = function(state){
        this.active = readOption(state, this.active ) ;
    }

/*------------------------------------------------------------------------
 * setCallback
 *------------------------------------------------------------------------
 */
    this.setCallback = function(cb){
        this.callback = cb ;
    }

/*------------------------------------------------------------------------
 * call the callback function if necessary
 *------------------------------------------------------------------------
 */
    this.call = function(ctime){
        if (this.lastCall > ctime ){
            this.lastCall = ctime  ;
        }
        this.timeDiff = ctime - this.lastCall ;
        if ( this.timeDiff >= this.interval ){
            this.lastCall = ctime ;
            this.timeDiff = 0 ;
            if ( this.active == true ){
                this.callback() ;
            }
        }
    }
} /* end of IntervalCaller */

/*========================================================================
 * saveCanvas
 *========================================================================
 */
function saveCanvas(canvasId, options){
    var link = document.createElement('a') ;
    link.href = document.getElementById(canvasId).toDataURL() ;

    var prefix   = '' ;
    var postfix  = '' ;
    var number   = '' ;
    var format   = 'png' ;
    var download = 'download';

    if ( options != undefined ){
        if ( options.prefix != undefined ){
            prefix = options.prefix ;
            download = '' ;
        }

        if ( options.postfix != undefined ){
            postfix = options.postfix ;
            download = '' ;
        }

        if ( options.number != undefined ){
            download = '' ;
            var t = Math.floor(options.number) ;
            if ( t<1000 ){
                number = '000'+ t.toString() ;
            }else if (t<10000){
                number = '00'+t.toString() ;
            }else if (t<100000){
                number = '0'+t.toString() ;
            }else{
                number = t.toString() ;
            }
        }

        if (options.format != undefined ){
            format = options.format ;
        }
    }

    link.download = download + prefix + number + postfix + '.' + format ;
    var clickEvent = new MouseEvent("click", {
        "view": window,
        "bubbles": true,
        "cancelable": false
    });

    link.dispatchEvent(clickEvent) ;
} /* end of saveCanvas */

/*========================================================================
 * APD
 *========================================================================
 */
function APD( target,  opts={}){
    this.target         = target ;
    this.currVal        = undefined ;
    this.apCounts       = readOption( opts.apCounts,    10  ) ;
    this.threshold      = readOption( opts.threshold,   -75 ) ;
    this.channel        = readOption( opts.channel,     'r' ) ;
    this.avgApd         = 0;
    this.noApsMeasured  = 0 ;
    this.measuring      = readOption( opts.measuring , false ) ;
    this.apStarted      = false ;
    this.apIncomplete   = true ;
    this.apStartTime    = undefined ;
    this.apEndTime      = undefined ;
    this.apd            = undefined ;
    this.probePosition = readOption( opts.probePosition, [.5,.5] ) ;

    this.probe = new Probe(this.target, {
            channel : this.channel,
            probePosition : this.probePosition } ) ;

/*------------------------------------------------------------------------
 * getAvgApd    : getAvgValue of APD
 *------------------------------------------------------------------------
 */
    this.getAvgApd = function(){
        return this.avgApd ;
    }

/*------------------------------------------------------------------------
 * setMeasuring
 *------------------------------------------------------------------------
 */
    this.setMeasuring = function( measuring ){
        this.measuring = readOption( measuring, this.measuring ) ;
    }

/*------------------------------------------------------------------------
 * toggleMeasuring
 *------------------------------------------------------------------------
 */
    this.toggleMeasuring = function(){
        this.measuring = ! this.measuring ;
    }

/*------------------------------------------------------------------------
 * startMeasuring
 *------------------------------------------------------------------------
 */
    this.startMeasuring = function(){
        this.measuring = true ;
    }

/*------------------------------------------------------------------------
 * stopMeasuring
 *------------------------------------------------------------------------
 */
    this.stopMeasuring = function(){
        this.measuring = false ;
    }
      

/*------------------------------------------------------------------------
 * reset
 *------------------------------------------------------------------------
 */
    this.reset = function(ropts={}){
        this.noApsMeasured  = 0 ;
        this.apStarted      = false ;
        this.apIncomplete   = true ;
        this.apStartTime    = undefined ;
        this.apEndTime      = undefined ;
        this.apd            = 0 ;
        this.avgApd         = 0 ;
        this.apCounts = 
            readOption( ropts.apCounts, this.apCounts ) ;
        this.threshold = 
            readOption ( ropts.threshold, this.threshold);
        this.channel = 
            readOption( ropts.channel, this.channel ) ;
        this.target = 
            readOption( ropts.target, this.target ) ;
        this.probePosition =
            readOption( ropts.probePosition, this.probePosition ) ;
        this.measuring = readOption( ropts.measuring, this.measuring ) ;

        this.probe.setChannel(this.channel) ;
        this.probe.setPosition(this.probePosition) ;
        this.probe.setTarget(this.target) ;
    }

/*------------------------------------------------------------------------
 * measure      : measure APD
 *------------------------------------------------------------------------
 */
    this.measure = function( currTime ){
        if ( ! this.measuring ){
            return ;
        }
        if ( this.noApsMeasured >= this.apCounts )
            return this.getAvgApd() ;

        this.currVal = this.probe.get() ;
        if (this.apIncomplete){
            /*  check if A.P.
                just completed       */
            if (this.currVal < this.threshold){
                this.apIncomplete = false ;
                this.apEndTime = currTime ;
                if (this.apStarted){
                    this.apd = this.apEndTime - this.apStartTime ;
                    this.avgApd =
                        (this.apd + this.avgApd*this.noApsMeasured)/
                        (this.noApsMeasured+1) ;
                    this.noApsMeasured += 1 ;
                    this.apStarted = false ;
                }
            }
        }else if (!this.apStarted){
            /*  Check if a new A.P.
                just started        */
            if( this.currVal > this.threshold ){
                this.apStarted      = true ;
                this.apIncomplete   = true;
                this.apStartTime    = currTime ;
            }
        }

        return this.getAvgApd() ;
    } /* end of measure */

} /* end of APD */

/*========================================================================
 * resizeRenderTargets
 *========================================================================
 */
function resizeRenderTargets( targets, width, height ){
    for (var i=0 ; i< targets.length;  i++  ){
        targets[i].resize(width,height) ;
    }
    return ;
}

/*========================================================================
 * setUniformInSolvers
 *========================================================================
 */
function setUniformInSolvers( name,value, solvers ){
    for( var i=0; i< solvers.length; i++ ){
        solvers[i].setUniform(name , value ) ;
    }
    return ;
}

/*========================================================================
 * setUniformsInSolvers
 *========================================================================
 */ 
function setUniformsInSolvers( names, values, solvers ){
    for (var i=0; i < names.length; i++){
        setUniformInSolvers( names[i], values[i], solvers ) ;
    }
}

/*========================================================================
 * CtrlClickListener
 *========================================================================
 */
function CtrlClickListener( __object, __callback, options={}){
    this.object     = __object ;
    this.callback   = __callback ;
    this.onClick    = function(e){
        if ( e.ctrlKey & !e.shiftKey ){
            if ( (e.type == 'click') || (e.buttons >=1)){
                e.position = [
                    e.offsetX/this.object.width ,
                    1.-e.offsetY/this.object.height
                ] ;
                this.callback(e) ;
            }
        }
    }

    this.mousemove  = readOption(options.mousemove, false   ) ;
    this.click      = readOption(options.click, true        ) ;

    if ( this.mousemove ){
        this.object.addEventListener(
            'mousemove',
            (e) => this.onClick(e),
            false
        ) ;
    }

    if (this.click){
        this.object.addEventListener(
            'click',
            (e) => this.onClick(e),
            false
        ) ;
    }
}

/*========================================================================
 * ShiftClickListener
 *========================================================================
 */
function ShiftClickListener( __object, __callback, options={}){
    this.object     = __object ;
    this.callback   = __callback ;
    this.onClick    = function(e){
        if ( e.shiftKey & !e.ctrlKey ){
            if ( (e.type == 'click') || (e.buttons >=1)){
                e.position = [
                    e.offsetX/this.object.width ,
                    1.-e.offsetY/this.object.height
                ] ;
                this.callback(e) ;
            }
        }
    }

    this.mousemove  = readOption(options.mousemove, false   ) ;
    this.click      = readOption(options.click, true        ) ;

    if ( this.mousemove ){
        this.object.addEventListener(
            'mousemove',
            (e) => this.onClick(e),
            false
        ) ;
    }

    if (this.click){
        this.object.addEventListener(
            'click',
            (e) => this.onClick(e),
            false
        ) ;
    }
}

/*========================================================================
 * DoubleClickListener
 *========================================================================
 */ 
function DoubleClickListener(__object, __callback, options={}){
    this.object = __object ;
    this.callback = __callback ;
    this.onClick = function(e){
        e.position = [
                    e.offsetX/this.object.width ,
                    1.-e.offsetY/this.object.height
                ] ;

        var clickTime = new Date().getTime();
        var deltaT = clickTime - gl.lastClickTime ;
        gl.lastClickTime = clickTime ;
        if (deltaT>600) {
            return ;
        }
        this.callback(e) ;
    }
    this.object.addEventListener(
            'mousedown',
            (e) => this.onClick(e),
            false ) ;
}

/*========================================================================
 * LongClickListener
 *========================================================================
 */
function LongClickListener( __object, __callback, options={}){
    this.object = __object ;
    this.callback = __callback ;
    this.duration = readOptions( options.duration, 1000 ) ;
    this.movementTolerance = 
        readOptions( options.movementTolerance, 0.05 ) ;
    
    this.onMousedown = function(e){
        e.position = [
                    e.offsetX/this.object.width ,
                    1.-e.offsetY/this.object.height
                ] ;
        gl.__clickPosition = e.position ;
        var clickTime = new Date().getTime();
        gl.lastClickTime = clickTime ;
    }

    this.onMouseup = function(e){
        e.position = [
                    e.offsetX/this.object.width ,
                    1.-e.offsetY/this.object.height
                ] ;
        var releaseTime = new Date().getTime() ;
        var deltaT = releaseTime - gl.lastClickTime ;
        var deltaX = e.position[0] - gl.__clickPosition[0] ;
        var deltaY = e.position[1] - gl.__clickPosition[1] ;
        var deltaL = Math.sqrt( deltaX*deltaX + deltaY*deltaY ) ;

        if (    (deltaT > this.duration) && 
                (deltaL < this.movementTolerance )
            ){
            this.callback(e) ;
        }

    }

    this.object.addEventListener(
            'mousedown',
            (e) => this.onMousedown(e),
            false ) ;
    this.object.addEventListener(
            'mouseup',
            (e) => this.onMouseup(e),
            false ) ;

}

/*========================================================================
 * CtrlShiftClickListener
 *========================================================================
 */
function CtrlShiftClickListener( __object, __callback, options={}){
    this.object     = __object ;
    this.callback   = __callback ;
    this.onClick    = function(e){
        if ( e.shiftKey & e.ctrlKey ){
            if ( (e.type == 'click') || (e.buttons >=1)){
                e.position = [
                    e.offsetX/this.object.width ,
                    1.-e.offsetY/this.object.height
                ] ;
                this.callback(e) ;
            }
        }
    }

    this.mousemove  = readOption(options.mousemove, false   ) ;
    this.click      = readOption(options.click, true        ) ;

    if ( this.mousemove ){
        this.object.addEventListener(
            'mousemove',
            (e) => this.onClick(e),
            false
        ) ;
    }

    if (this.click){
        this.object.addEventListener(
            'click',
            (e) => this.onClick(e),
            false
        ) ;
    }
}


/*========================================================================
 * ClickListener
 *========================================================================
 */
function ClickListener( __object, __callback, options={}){
    this.object     = __object ;
    this.callback   = __callback ;
    this.onClick    = function(e){
        var deltaT = clickTime - gl.lastClickTime ;
        gl.lastClickTime = new Date().getTime() ;
        if (deltaT<600) {
            return ;
        }

        if ( (e.type == 'click') || (e.buttons >=1)){
            e.position = [
                e.offsetX/this.object.width ,
                1.-e.offsetY/this.object.height
            ] ;
            this.callback(e) ;
        }
    }


    this.mousemove  = readOption(options.mousemove, false   ) ;
    this.click      = readOption(options.click, true        ) ;

    if ( this.mousemove ){
        this.object.addEventListener(
            'mousemove',
            (e) => this.onClick(e),
            false
        ) ;
    }

    if (this.click){
        this.object.addEventListener(
            'click',
            (e) => this.onClick(e),
            false
        ) ;
    }
}

/*========================================================================
 * Storage : Store Values using LocalStorage
 *========================================================================
 */ 
class Storage{
    constructor(options={}){
        this.storage = localStorage ;
        this.prefix = readOption( options.prefix, "") ;
    }
    
/*------------------------------------------------------------------------
 * store
 *------------------------------------------------------------------------
 */
    store(name, value){
        this.storage.setItem(this.prefix+name, value) ;
    }

/*------------------------------------------------------------------------
 * get
 *------------------------------------------------------------------------
 */
    get(name){
        return this.storage.getItem(this.prefix+name) ;
    }

/*------------------------------------------------------------------------
 * getFloat
 *------------------------------------------------------------------------
 */
    getFloat(name){
        return parseFloat(this.get(name)) ;
    }

/*------------------------------------------------------------------------
 * storeList
 *------------------------------------------------------------------------
 */
    storeList( names, values ){
        for(var i=0; i<names.length; i++){
            this.store(names[i], values[i]) ;
        }
    }
    
/*------------------------------------------------------------------------
 * restoreFloatList
 *------------------------------------------------------------------------
 */
    restoreFloatList( vars, names ){
        for(var i=0; i< vars.length ; i++){
            vars[i] = this.getFloat( names[i]) ;
        }
    }

/*------------------------------------------------------------------------
 * restoreValue
 *------------------------------------------------------------------------
 */
    restoreValue( variable, name ){
        variable = this.get(name) ;
    }

/*------------------------------------------------------------------------
 * storeAsXML
 *------------------------------------------------------------------------
 */
    storeAsXML(options={}){
        var xml = readOption(options.xml, undefined ) ;
        var obj = readOption(options.object,undefined) ;
        obj = readOption(options.obj, obj ) ;
        if( obj == undefined ){
            warn('You need to define "object"') ;
        } 

        var names = readOption(options.names, [] ) ;

         
        function xmlAdd( name, value ){
            var type = typeof(value) ;
            return '\t<data id="'+
                                name+
                '" type="'    
                                +type+'">'
                                            +value+
            '</data>\n' ;
        }

        var fileName = readOption(options.fileName, 'download.xml') ;
        var stream =  '<?xml version="1.0" encoding="utf-8"?>\n' ;
        stream += '<xml>\n' ;

        for( var i=0 ; i< names.length ; i++){
            var name = names[i] ;
            stream += xmlAdd( name , obj[name] ) ;
        }
        stream += '</xml>' ;
        
        this.store(xml, stream) ;
    }

/*------------------------------------------------------------------------
 * restoreFromXML
 *------------------------------------------------------------------------
 */
    restoreFromXML(options={}){
        var xml = readOption(options.xml, undefined ) ;
        var obj = readOption(options.object,undefined) ;
        obj = readOption(options.obj, obj ) ;
        if( obj == undefined ){
            warn('You need to define "object"') ;
        } 
        var names = readOption(options.names, undefined , 'You need to define "names"' ) ;
        
        if ( obj == undefined || names == undefined ){
            warn( 'Insuficient information was provided' ) ;
            warn( 'Exit without loading from XML file') ;
            return ;
        }
        var callback = readOption(options.callback, function(){} ) ;
    
        var stream = this.get(xml) ;

        if (stream){
            var parser = new DOMParser() ;
            var doc = parser.parseFromString(stream, "text/xml") ;

            for (var i=0; i<names.length ; i++){
                var name = names[i] ;
                var v = doc.getElementById(name) ;
                var type ;
                if (v){
                    type = v.getAttribute('type') ;
                    switch (type){
                        case 'number':
                            obj[name] = eval( v.innerHTML ) ;
                            break ;
                        case 'boolean':
                            obj[name] = eval( v.innerHTML ) ;
                            break ;
                        case 'object':
                            var strArray = v.innerHTML.split(',') ;
                            for(var i=0 ; i<strArray.length; i++){
                                obj[name][i] = eval(strArray[i]) ;
                            }
                            break ;

                        default:
                            obj[name] = v.innerHTML ;
                            break ;
                    }
                }
            }
            callback() ;
        }
    }
} /* end of Storage Class */

/*=========================================================================
 * saveToXML    :   save variables from and object to xml file
 *
 *      options :
 *          - obj   :   parent object that contains variables
 *          - names :   array of names of children of the obj to be saved
 *          - fileName: default name for the xml file to be saved to disk
 *=========================================================================
 */
    function saveToXML( options={}){
        var obj = readOption(options.object,undefined) ;
        obj = readOption(options.obj, obj ) ;
        if( obj == undefined ){
            warn('You need to define "object"') ;
        } 
        var names = readOption(options.names, [] ) ;

         
        function xmlAdd( name, value ){
            var type = typeof(value) ;
            return '\t<data id="'+
                                name+
                '" type="'    
                                +type+'">'
                                            +value+
            '</data>\n' ;
        }

        var fileName = readOption(options.fileName, 'download.xml') ;
        var stream =  '<?xml version="1.0" encoding="utf-8"?>\n' ;
        stream += '<xml>\n' ;

        for( var i=0 ; i< names.length ; i++){
            var name = names[i] ;
            stream += xmlAdd( name , obj[name] ) ;
        }
        stream += '</xml>' ;
        
        var link = document.createElement('a') ;
        link.download = fileName ;
        var blob = new Blob([stream], {type:'text/plain'});

        if (window.URL != null)
        {
            // Chrome allows the link to be clicked
            // without actually adding it to the DOM.
            link.href = 
                window.URL.createObjectURL(blob);
        }
        else
        {
            // Firefox requires the link to be added to the DOM
            // before it can be clicked.
            link.href = 
                window.URL.createObjectURL(blob);
            link.onclick = destroyClickedElement;
            link.style.display = "none";
            document.body.appendChild(link);
        }
        var clickEvent = new MouseEvent("click", {
            "view": window,
            "bubbles": true,
            "cancelable": false
        });

        link.dispatchEvent(clickEvent) ;
    }

/*=========================================================================
 * loadFromXML :
 *      options: 
 *          - input     :   input element on the page which loads the file
 *          - obj       :   parent object to be loaded
 *          - names     :   list of names of children of obj to be loaded 
 *                          from xml file
 *          - callback  :   callback function to call when loading is 
 *                          finished
 *=========================================================================
 */
    function loadFromXML(options={}){
        var input = readOption(options.input,undefined, 
                'You need define "input" option') ;
        var obj = readOption(options.object,undefined) ;
        obj = readOption(options.obj, obj ) ;
        if( obj == undefined ){
            warn('You need to define "object"') ;
        } 
        var names = readOption(options.names, undefined , 
                'You need to define "names"' ) ;
        
        if (    input == undefined || 
                obj == undefined || 
                names == undefined ){
            warn( 'Insuficient information was provided' ) ;
            warn( 'Exit without loading from XML file') ;
            return ;
        }
        var callback = readOption(options.callback, function(){} ) ;

        var file = input.files[0] ;
        var reader = new FileReader();
        var savedXml ;
        if (window.XMLHttpRequest)
        {// code for IE7+, Firefox, Chrome, Opera, Safari
            savedXml = new XMLHttpRequest();
        }
        else
        {// code for IE6, IE5
            savedXml=new ActiveXObject("Microsoft.XMLHTTP");
        }

        if (file){
            reader.readAsDataURL(file) ;
        }


        reader.onload = function(){
            fileURL = reader.result ;

            savedXml.open("GET", fileURL, true);
            savedXml.send();

            savedXml.onreadystatechange = function() {
                if (savedXml.readyState == 4 && savedXml.status == 200) {
                    doc = savedXml.responseXML ;
                    for (var i=0; i<names.length ; i++){
                        var name = names[i] ;
                        var v = doc.getElementById(name) ;
                        var type ;
                        if (v){
                            type = v.getAttribute('type') ;
                            switch (type){
                                case 'number':
                                    obj[name] = eval( v.innerHTML ) ;
                                    break ;
                                case 'boolean':
                                    obj[name] = eval( v.innerHTML ) ;
                                    break ;
                                case 'object':
                                    var strArray = v.innerHTML.split(',') ;
                                    for(var i=0 ; i<strArray.length; i++){
                                        obj[name][i] = eval(strArray[i]) ;
                                    }
                                    break ;
                                default:
                                    obj[name] = v.innerHTML ;
                                    break ;
                            }
                        }
                    }
                    callback() ;
                } /* end of if Statement ) */
            } /* End of onreadystatechange */
        } /* End of reader.onload */
    }/* End of loadFromXML */ 

/*========================================================================
 * Gui  :   forks dat.GUI and adds updateDisplay functionality to the 
 *          entirety of the gui
 *
 *          instead of new dat.GUI we can now use addPanel of the class
 *========================================================================
 */ 
class Gui{
    constructor(){
        this.panels = [] ;
    }

/*------------------------------------------------------------------------
 * create a new panel and add it to the gui
 *------------------------------------------------------------------------
 */
    addPanel(options={}){
        var panel = new GUI.GUI(options) ;
        this.panels.push(panel) ;
        return panel ;
    }

/*------------------------------------------------------------------------
 * updateControllersDisplay     : update display for all conrolers
 *------------------------------------------------------------------------
 */
    updateControllersDisplay( controllers, verbose ){
        for(var c in controllers ){
            if(verbose) log('Controller : ', c) ;
            
            controllers[c].updateDisplay() ;
            if( typeof(controllers[c].__onChange) == 'function'){
                if (verbose) log('running onChange') ;
                controllers[c].__onChange() ;
            }
        }
    }

/*------------------------------------------------------------------------
 * updateFolderDisplay  : update display for all subfolder of a folder
 *------------------------------------------------------------------------
 */
    updateFolderDisplay( folder ,verbose ){
        for(var fldr in folder.__folders ){
            if (verbose) log( 'Entering folder :', fldr ) ;
            this.updateFolderDisplay(folder.__folders[fldr], verbose) ;
        }
        this.updateControllersDisplay( folder.__controllers , verbose ) ;
    }

/*------------------------------------------------------------------------
 * updateDisplay    :   updates all gui displays and runs onChange
 *                      callback functions
 *------------------------------------------------------------------------
 */
    updateDisplay(options={}){
        var verbose = readOption(options.verbose, false ) ;
        for(var panel in this.panels){
            this.updateFolderDisplay(this.panels[panel], verbose) ;
        }
    }

/*------------------------------------------------------------------------
 * update           : forks updateDisplay
 *------------------------------------------------------------------------
 */
    update(options={}){
        this.updateDisplay(options) ;
    }
}

/*************************************************************************
 * The structure to be returned as CompGL
 *************************************************************************
 */
return {
    cgl                 : cgl ,
    gl                  : gl ,
    ComputeGL           : ComputeGL ,
    LineGeometry        : LineGeometry ,
    UnitCubeGeometry    : UnitCubeGeometry ,
    FloatRenderTarget   : FloatRenderTarget ,
    ImageTexture        : ImageTexture ,
    TableTexture        : TableTexture ,
    CanvasTexture       : CanvasTexture ,
    SparseData          : SparseData ,
    Solver              : Solver ,
    Copy                : Copy ,
    setUniformInSolvers : setUniformInSolvers ,
    setUniformsInSolvers: setUniformsInSolvers ,
    resizeRenderTargets : resizeRenderTargets ,
    copyTexture         : copyTexture ,
    SignalPlot          : SignalPlot ,
    Plot1D              : Plot1D ,
    Plot2D              : Plot2D ,
    VolumeRayCaster     : VolumeRayCaster ,
    getColormapList     : getColormapList ,
    Probe               : Probe ,
    ProbeRecorder       : ProbeRecorder ,
    IntervalCaller      : IntervalCaller ,
    saveCanvas          : saveCanvas ,
    APD                 : APD ,

    /* glMatrix             */
    glMatrix            : glMatrix.glMatrix ,
    mat2                : mat2 ,
    mat2d               : mat2d ,
    mat3                : mat3 ,
    mat4                : mat4 ,
    quat                : quat ,
    vec2                : vec2 ,
    vec3                : vec3 ,
    vec4                : vec4 ,

    /* OrbitalCamera Control    */
    OrbitalCameraControl: OrbitalCameraControl ,

    /* Event Listeners          */
    ClickListener       :   ClickListener,
    DoubleClickListener :   DoubleClickListener,
    CtrlClickListener   :   CtrlClickListener,
    ShiftClickListener  :   ShiftClickListener,
    CtrlShiftClickListener : CtrlShiftClickListener ,
    ShiftCtrlClickListener : CtrlShiftClickListener ,
    LongClickListener   : LongClickListener ,

    readOption      : readOption,

    /* Storage */
    Storage         : Storage ,
    saveToXML       : saveToXML,
    loadFromXML     : loadFromXML,

    Gui             : Gui ,
} /* end of return structure */

/* End of return function of define */
} ) ;
