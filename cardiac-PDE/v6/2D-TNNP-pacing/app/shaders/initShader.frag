#version 300 es
/*@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
 * initShader   :   Initialize Beeler-Reuter Variables 
 *
 * PROGRAMMER   :   ABOUZAR KABOUDIAN
 * DATE         :   Wed 19 Jul 2017 12:31:30 PM EDT
 * PLACE        :   Chaos Lab @ GaTech, Atlanta, GA
 *@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
 */
#include precision.glsl
#include celltype.glsl

/*------------------------------------------------------------------------
 * Interface variables : 
 * varyings change to "in" types in fragment shaders 
 * and "out" in vertexShaders
 *------------------------------------------------------------------------
 */
in vec2 pixPos ;

uniform int cellType ;
/*------------------------------------------------------------------------
 * It turns out for my current graphics card the maximum number of 
 * drawBuffers is limited to 8 
 *------------------------------------------------------------------------
 */
layout (location = 0 )  out vec4  vrnk ;
layout (location = 1 )  out vec4  cssr ;
layout (location = 2 )  out vec4  mhjx ;
layout (location = 3 )  out vec4  dfff ;
layout (location = 4 )  out vec4  rsxr ;

/*========================================================================
 * Main body of the shader
 *========================================================================
 */
void main() {
    float V,R ;
    
    if ( cellType == EPI ){
        vrnk = vec4(
                -85.46 ,            /* V                */ 
                0.9891 ,            /* R                */ 
                9.293 ,             /* Nai              */
                136.2               /* Ki               */
        ) ;

        cssr = vec4(    
                0.0001156,          /* Cai              */  
                0.0002331,          /* CaSS             */
                3.432,              /* CaSR             */
                0.0                 /* I_SumCa          */
        ) ;

        mhjx  = vec4(    
                0.001633,           /* m                */
                0.7512,             /* h                */
                0.7508,             /* j                */
                0.003214            /* xs               */
        ) ;
        
        dfff = vec4(    
                3.270e-5,           /* d                */
                0.9767,             /* f                */
                0.9995,             /* f2               */
                1.0000              /* f_cass           */
        ) ;

    }else if( cellType == MYO){
        vrnk = vec4(
                -84.53 ,
                0.9874 ,
                9.322,              /* Nai              */
                136.0               /* Ki               */
            ) ;
        
        cssr = vec4(    
                0.0001156,          /* Cai              */
                0.0002331,          /* CaSS             */
                4.130,              /* CaSR             */
                0.0                 /* I_SumCa          */
        ) ;

        mhjx = vec4(    
                0.001694,           /* m                */
                0.7466,             /* h                */
                0.7457,             /* j                */
                0.003343            /* xs               */
        ) ;

        dfff = vec4(    
                3.345e-5,           /* d                */
                0.9595,             /* f                */
                0.9995,             /* f2               */
                1.0000              /* f_cass           */
        ) ;

    }else{ /* Endo */
        vrnk    = vec4(
                -84.70 ,            /* V                */
                0.9891 ,            /* R                */
                9.413,              /* Nai              */
                136.1               /* Ki               */
        ) ;

        cssr = vec4(    
                0.0001021,          /* Cai              */
                0.0002111,          /* CaSS             */
                3.385,              /* CaSR             */
                0.0                 /* I_SumCa          */
        ) ;

        mhjx = vec4(    
                0.001634,           /* m                */
                0.7512,             /* h                */
                0.7508,             /* j                */
                0.003213            /* xs               */
        ) ;
    
        dfff = vec4(    
                3.270e-5,           /* d                */
                0.9771,             /* f                */
                0.9995,             /* f2               */
                1.0000              /* f_cass           */
        ) ;
    }
    rsxr = vec4(0.0, 1.0, 0.0, 1.0);
    return ;
}
