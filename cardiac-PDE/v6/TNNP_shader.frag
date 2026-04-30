#version 300 es
#include precision.glsl
#include celltype.glsl

in vec2 pixPos ;

uniform float       ds_x, ds_y ;
uniform float       dt ;
uniform float       diffCoef ;

uniform sampler2D   inVrnk ;
uniform sampler2D   inCssr ;
uniform sampler2D   inMhjx ;
uniform sampler2D   inDfff ;
uniform sampler2D   inRsxr ;

/*------------------------------------------------------------------------
 * It turns out for my current graphics card the maximum number of 
 * drawBuffers is limited to 8 
 *------------------------------------------------------------------------
 */
layout (location = 0 )  out vec4  outVrnk ;
layout (location = 1 )  out vec4  outCssr ;
layout (location = 2 )  out vec4  outMhjx ;
layout (location = 3 )  out vec4  outDfff ;
layout (location = 4 )  out vec4  outRsxr ;

/*========================================================================
 * Main body of the shader
 *========================================================================
 */
void main() {
    
/*------------------------------------------------------------------------
 * parameters
 *------------------------------------------------------------------------
 */
    float Ko=5.4;           float Cao=2.0;          float Nao=140.0 ;
    float Vc=0.016404;      float Vsr=0.001094;     float Vss=0.00005468 ;
    float Bufc=0.2;         float Kbufc=0.001;      float Bufsr=10.;
    float Kbufsr=0.3;       float Bufss=0.4;        float Kbufss=0.00025 ;
    float Vmaxup=0.006375;  float Kup=0.00025;      float Vrel=0.102 ;
    float k3=0.060;         float k4=0.005;
    float k1prime=0.15;     float k2prime=0.045;
    float EC=1.5;           float maxsr=2.5;        float minsr=1.;
    float Vleak=0.00036;    float Vxfer=0.0038;
    float RR=8314.3;        float FF=96486.7;       float TT=310.0;

    float CAPACITANCE=0.185 ;
    float   Gks, Gto ;

    Gks=0.392 ; Gto=0.294 ;


    float Gkr=0.153;    float pKNa=0.03;        
    float GK1=5.405;    float alphanaca=2.5;
    float GNa=14.838;   float GbNa=0.00029;     
    float KmK=1.0;      float KmNa=40.0;
    float knak=2.724;   float GCaL=0.00003980;  
    float GbCa=0.000592;
    float knaca=1000.;  float KmNai=87.5;       
    float KmCa=1.38;    float ksat=0.1;
    float n=0.35;       float GpCa=0.1238;      
    float KpCa=0.0005;  float GpK=0.0146;

/*------------------------------------------------------------------------
 * helpful values
 *------------------------------------------------------------------------
 */
    float   inverseVcF2=1./(2.*Vc*FF) ;
    float   inverseVcF=1./(Vc*FF) ;
    float   inversevssF2=1./(2.*Vss*FF) ;
    float   rtof=(RR*TT)/FF ;
    float   fort=1./rtof ;
    float   KmNai3=KmNai*KmNai*KmNai ;
    float   Nao3=Nao*Nao*Nao ;
    float   Gkrfactor=sqrt(Ko/5.4) ;

/*------------------------------------------------------------------------
 * pixelPos and discretization
 *------------------------------------------------------------------------
 */
    vec2 cp = pixPos ;
    vec2    size    = vec2(textureSize( inVrnk, 0 ) );
    float   cddx    = size.x/ds_x ;
    float   cddy    = size.y/ds_y ;

    cddx *= cddx ;
    cddy *= cddy ;

/*------------------------------------------------------------------------
 * reading from textures
 *------------------------------------------------------------------------
 */
    vec4    vrnkC = texture( inVrnk, cp ) ;
    float   V       = vrnkC.r ;
    float   v       = V ;
    float   vv      = V ;
    float   sRR     = vrnkC.g ;
    float   Nai     = vrnkC.b ;
    float   Ki      = vrnkC.a ;

/*========================================================================
 * mhjx
 *========================================================================
 */
    vec4    mhjxC   =   texture(inMhjx, pixPos) ;
    float   sm      =   mhjxC.r ;
    float   sh      =   mhjxC.g ;
    float   sj      =   mhjxC.b ;
    float   sxs     =   mhjxC.a ;

/*------------------------------------------------------------------------
 * m
 *------------------------------------------------------------------------
 */
    float   AM      =   1./(1.+exp((-60.-vv)/5.)) ;
    float   BM      =   0.1/(1.+exp((vv+35.)/5.))
                    +   0.10/(1.+exp((vv-50.)/200.)) ;

    float   minft   =   1./((1.+exp((-56.86-vv)/9.03))*
                                (1.+exp((-56.86-vv)/9.03))) ;
    float   TAU_M   =   AM*BM ;
    float   exptaumt=   exp(-dt/TAU_M) ;

    float   hinft   =   1./((1.+exp((vv+71.55)/7.43))
                                *(1.+exp((vv+71.55)/7.43))) ;
    
    sm = minft-(minft-sm)*exptaumt ;

/*------------------------------------------------------------------------
 * h
 *------------------------------------------------------------------------
 */
    float   AH, BH ;
    if(vv >=-40.){
        AH=0. ;
        BH=(0.77/(0.13*(1.+exp(-(vv+10.66)/11.1)))) ;
    }
    else{
        AH=(0.057*exp(-(vv+80.)/6.8)) ;
        BH=(2.7*exp(0.079*vv)+(3.1e5)*exp(0.3485*vv)) ;
    }
    float   TAU_H   =1.0/(AH+BH) ;
    float   exptauht=exp(-dt/TAU_H) ;
    
    sh  = hinft-(hinft-sh)*exptauht ;


/*------------------------------------------------------------------------
 * j
 *------------------------------------------------------------------------
 */
    float AJ, BJ ;
    if(vv >=-40.){ 
        AJ=0. ;
        BJ=(0.6*exp((0.057)*vv)/(1.+exp(-0.1*(vv+32.)))) ;
    }
    else{
        AJ= (((-2.5428e4)*exp(0.2444*vv)-(6.948e-6)
                    *exp(-0.04391*vv))*(vv+37.78)
                    /(1.+exp(0.311*(vv+79.23)))) ;
        BJ= (0.02424*exp(-0.01052*vv)
                /(1.+exp(-0.1378*(vv+40.14)))) ;
    }
    float   jinft   =   hinft ;
    float   TAU_J   =   1.0/(AJ+BJ) ;
    float   exptaujt=exp(-dt/TAU_J) ;
    
    sj  = jinft-(jinft-sj)*exptaujt ;

/*------------------------------------------------------------------------
 * xs
 *------------------------------------------------------------------------
 */
    float   xsinft  =   1./(1.+exp((-5.-vv)/14.)) ;
    float   Axs     =   (1400./(sqrt(1.+exp((5.-vv)/6.)))) ;
    float   Bxs     =   (1./(1.+exp((vv-35.)/15.))) ;
    float   TAU_Xs  =   Axs*Bxs+80. ;
    float   exptauxst=  exp(-dt/TAU_Xs) ;

    sxs     =   xsinft-(xsinft-sxs)*exptauxst ;
    
    outMhjx = vec4( sm, sh, sj, sxs ) ;

/*========================================================================
 * dfff
 *========================================================================
 */
    vec4    dfffC   =   texture(inDfff, pixPos) ;
    vec4    cssrC   =   texture(inCssr, pixPos) ;

    float   Cai     = cssrC.r ;
    float   CaSS    = cssrC.g ;
    float   CaSR    = cssrC.b ;

    float   ccass   =   CaSS ;
    float   sd      =   dfffC.r ;
    float   sf      =   dfffC.g ;
    float   sf2     =   dfffC.b ;
    float   sfcass  =   dfffC.a ;

/*------------------------------------------------------------------------
 * d
 *------------------------------------------------------------------------
 */
    float   dinft   =   1./(1.+exp((-8.-vv)/7.5)) ;
    float   Ad      =   1.4/(1.+exp((-35.-vv)/13.))+0.25 ;
    float   Bd      =   1.4/(1.+exp((vv+5.)/5.)) ;
    float   Cd      =   1./(1.+exp((50.-vv)/20.)) ;
    float   TAU_D   =   Ad*Bd+Cd ;
    float   exptaudt=   exp(-dt/TAU_D) ;
    
    sd              =   dinft-(dinft-sd)*exptaudt ;

/*------------------------------------------------------------------------
 * f
 *------------------------------------------------------------------------
 */
    float   finft   =   1./(1.+exp((vv+20.)/7.));
    float   Af      =   1102.5*exp(-(vv+27.)*(vv+27.)/225.) ;
    float   Bf      =   200./(1.+exp((13.-vv)/10.)) ;
    float   Cf      =   (180./(1.+exp((vv+30.)/10.)))+20. ;
    float   TAU_F   =   Af+Bf+Cf ;
    float   exptauft=   exp(-dt/TAU_F) ;

    sf              =   finft-(finft-sf)*exptauft ;

/*------------------------------------------------------------------------
 * f2
 *------------------------------------------------------------------------
 */
    float   f2inft  =   0.67/(1.+exp((vv+35.)/7.))+0.33 ;
    float   Af2     =   600.*exp(-(vv+25.)*(vv+25.)/49.) ;
    float   Bf2     =   31./(1.+exp((25.-vv)/10.)) ;
    float   Cf2     =   16./(1.+exp((vv+30.)/10.)) ;
    float   TAU_F2  =   Af2+Bf2+Cf2 ;
    float   exptauf2t=exp(-dt/TAU_F2) ;

    sf2             =   f2inft-(f2inft-sf2)*exptauf2t ;

/*------------------------------------------------------------------------
 * fcass
 *------------------------------------------------------------------------
 */
    float   fcassinft   =   0.6/(1.+(ccass/0.05)*(ccass/0.05))+0.4 ;
    float   taufcass    =   80./(1.+(ccass/0.05)*(ccass/0.05))+2. ;
    float   exptaufcasst=   exp(-dt/taufcass) ;
    float   exptaufcassinf= exp(-dt/2.0) ;
 
    float   casshi      =   1.0 ;
    float   FCaSS_INF, exptaufcass ;

    if ( CaSS >= casshi ){
        FCaSS_INF   =   0.4 ;
        exptaufcass =   exptaufcassinf ;
    }else{
        FCaSS_INF   =   fcassinft ;
        exptaufcass =   exptaufcasst ;
    }
    
    sfcass          =   FCaSS_INF-(FCaSS_INF-sfcass)*exptaufcass ;
 
    outDfff = vec4( sd, sf, sf2, sfcass ) ;

/*========================================================================
 * rsxr
 *========================================================================
 */
    vec4    rsxrC   = texture(inRsxr, pixPos) ;
    
    float   sr      = rsxrC.r ;
    float   ss      = rsxrC.g ;
    float   sxr1    = rsxrC.b ;
    float   sxr2    = rsxrC.a ;

/*------------------------------------------------------------------------
 * r, s
 *------------------------------------------------------------------------
 */
    float rinft, sinft ;
    float TAU_R, TAU_S ;

    rinft   =   1./(1.+exp((20.-vv)/6.)) ;
    sinft   =   1./(1.+exp((vv+20.)/5.)) ;
    TAU_R   =   9.5*exp(-(vv+40.)*(vv+40.)/1800.)+0.8 ;
    TAU_S   =   85.*exp(-(vv+45.)*(vv+45.)/320.)
            +   5./(1.+exp((vv-20.)/5.))+3. ;

    float   exptaurt    =   exp(-dt/TAU_R) ;
    float   exptaust    =   exp(-dt/TAU_S) ;
    sr  = rinft-(rinft-sr)*exptaurt ;
    ss  = sinft-(sinft-ss)*exptaust ;

/*------------------------------------------------------------------------
 * xr1, xr2
 *------------------------------------------------------------------------
 */
    float   xr1inft     =   1./(1.+exp((-26.-vv)/7.)) ;
    float   axr1        =   450./(1.+exp((-45.-vv)/10.)) ;
    float   bxr1        =   6./(1.+exp((vv-(-30.))/11.5)) ;
    float   TAU_Xr1     =   axr1*bxr1 ;
    float   exptauxr1t  =   exp(-dt/TAU_Xr1) ;
    float   xr2inft     =   1./(1.+exp((vv-(-88.))/24.)) ;
    float   axr2        =   3./(1.+exp((-60.-vv)/20.)) ;
    float   bxr2        =   1.12/(1.+exp((vv-60.)/20.)) ;
    float   TAU_Xr2     =   axr2*bxr2 ;
    float   exptauxr2t  =   exp(-dt/TAU_Xr2) ;
    
    sxr1 = xr1inft-(xr1inft-sxr1)*exptauxr1t ;
    sxr2 = xr2inft-(xr2inft-sxr2)*exptauxr2t ;
    
    outRsxr = vec4(sr,ss,sxr1,sxr2) ;
        
/*========================================================================
 * reversal potentials
 *========================================================================
 */
    float   Ek      = rtof*(log((Ko/Ki))) ;
    float   Ena     = rtof*(log((Nao/Nai))) ;
    float   Eks     = rtof*(log((Ko+pKNa*Nao)/(Ki+pKNa*Nai))) ;
    float   Eca     = 0.5*rtof*(log((Cao/Cai))) ;

/*========================================================================
 * INaCa
 *========================================================================
 */

/*------------------------------------------------------------------------
 * I_Na
 *------------------------------------------------------------------------
 */
    float   INa = GNa*sm*sm*sm*sh*sj*(v-Ena) ;
/*------------------------------------------------------------------------
 * I_Kr
 *------------------------------------------------------------------------
 */
    float   IKr = Gkr*Gkrfactor*sxr1*sxr2*(v-Ek) ;

/*------------------------------------------------------------------------
 * I_Ks
 *------------------------------------------------------------------------
 */
    float   IKs = Gks*sxs*sxs*(v-Eks) ;

/*------------------------------------------------------------------------
 * I_to
 *------------------------------------------------------------------------
 */
    float   Ito = Gto*sr*ss*(v-Ek) ;

/*------------------------------------------------------------------------
 * I_K1
 *------------------------------------------------------------------------
 */
    float   vmek=v-Ek ;
    float   Ak1 =   0.1/(1.+exp(0.06*(vmek-200.))) ;
    float   Bk1 =   (3.*exp(0.0002*(vmek+100.))
                +   exp(0.1*(vmek-10.)))/(1.+exp(-0.5*(vmek))) ;
    float   ik1coefft=GK1*Ak1/(Ak1+Bk1) ;
    
    float   IK1= ik1coefft*(v-Ek) ;

/*------------------------------------------------------------------------
 * I_pK
 *------------------------------------------------------------------------
 */
    float   ipkcoefft   =   GpK/(1.+exp((25.-vv)/5.98)) ;

    float   IpK         =   ipkcoefft*(v-Ek) ;

/*------------------------------------------------------------------------
 * I_bNa
 *------------------------------------------------------------------------
 */
    float   IbNa        =   GbNa*(v-Ena) ;

/*------------------------------------------------------------------------
 * I_NaK
 *------------------------------------------------------------------------
 */
    float   inakcoefft  =   (1./(1.+0.1245*exp(-0.1*vv*fort)
                        +   0.0353*exp(-vv*fort)))*knak*(Ko/(Ko+KmK)) ;

    float   INaK        =   inakcoefft*(Nai/(Nai+KmNa)) ;

/*------------------------------------------------------------------------
 * I_NaCa
 *------------------------------------------------------------------------
 */
    float   temp        =   exp((n-1.)*vv*fort) ;
    float   temp2       =   knaca/((KmNai3+Nao3)*(KmCa+Cao)*(1.+ksat*temp)) ;
    float   inaca1t     =   temp2*exp(n*vv*fort)*Cao ;
    float   inaca2t     =   temp2*temp*Nao3*alphanaca ;

    float   INaCa       =   inaca1t*Nai*Nai*Nai-inaca2t*Cai ;


/*------------------------------------------------------------------------
 * Na_i
 *------------------------------------------------------------------------
 */
    float   dNai    =   -(INa+IbNa+3.*INaK+3.*INaCa)*inverseVcF*CAPACITANCE ;
    
    Nai             =   Nai+dt*dNai ;

/*------------------------------------------------------------------------
 * K_i
 *------------------------------------------------------------------------
 */
    float   Istim ;
    Istim = 0.0 ;

    float   dKi =-(Istim+IK1+Ito+IKr+IKs-2.*INaK+IpK)*inverseVcF*CAPACITANCE ;
    Ki          =   Ki +   dt*dKi ;

/*------------------------------------------------------------------------
 * ISumNaK
 *------------------------------------------------------------------------
 */
    float   ISumNaK    = INa   + IbNa  + INaK  + IK1 
                        + IKr   + IKs   + IpK   + Ito ;

/*========================================================================
 * cssr
 *========================================================================
 */

/*------------------------------------------------------------------------
 * ICaL
 *------------------------------------------------------------------------
 */
    temp    =   exp(2.*(vv-15.)*fort) ;
    float  ical1t ,  ical2t ;
    if(abs(vv-15.) < 1.e-4){
        float diff  = 1.e-4 ; 
        temp        =   exp(2.*(diff)*fort) ;
        ical1t      = GCaL*4.*(diff)*(FF*fort)*(0.25*temp)/(temp-1.) ;
        ical2t      = GCaL*4.*(diff)*(FF*fort)*Cao/(temp-1.) ;

    }else{
        ical1t      = GCaL*4.*(vv-15.)*(FF*fort)*(0.25*temp)/(temp-1.) ;
        ical2t      = GCaL*4.*(vv-15.)*(FF*fort)*Cao/(temp-1.) ;
    }

    float   ICaL    = sd*sf*sf2*sfcass*(ical1t*CaSS-ical2t) ;
/*------------------------------------------------------------------------
 * IpCa
 *------------------------------------------------------------------------
 */
    float   IpCa    =   GpCa*Cai/(KpCa+Cai) ;
/*------------------------------------------------------------------------
 * IbCa
 *------------------------------------------------------------------------
 */
    float   IbCa    = GbCa*(vv-Eca) ;
/*------------------------------------------------------------------------
 * update concentrations
 *------------------------------------------------------------------------
 */
    float   kCaSR   =   maxsr-((maxsr-minsr)/(1.+(EC/CaSR)*(EC/CaSR))) ;
    float   k1      =   k1prime/kCaSR ;
    float   k2      =   k2prime*kCaSR ;
    float   dRR     =   k4*(1.-sRR)-k2*CaSS*sRR ;
    sRR             =   sRR+dt*dRR ;
    float   sOO     =   k1*CaSS*CaSS*sRR/(k3+k1*CaSS*CaSS) ;

/*------------------------------------------------------------------------
 * Intracellular currents
 *------------------------------------------------------------------------
 */
    float   Irel    =   Vrel*sOO*(CaSR-CaSS) ;
    float   Ileak   =   Vleak*(CaSR-Cai) ;
    float   Iup     =   Vmaxup/(1.+((Kup*Kup)/(Cai*Cai))) ;
    float   Ixfer   =   Vxfer*(CaSS-Cai) ;

/*------------------------------------------------------------------------
 * update concentrations
 *------------------------------------------------------------------------
 */
    float   CaCSQN  =   Bufsr*CaSR/(CaSR+Kbufsr) ;
    float   dCaSR   =   dt*(Iup-Irel-Ileak) ;
    float   bjsr    =   Bufsr-CaCSQN-dCaSR-CaSR+Kbufsr ;
    float   cjsr    =   Kbufsr*(CaCSQN+dCaSR+CaSR) ;
    CaSR            =   (sqrt(bjsr*bjsr+4.*cjsr)-bjsr)/2. ;

    float   CaSSBuf =   Bufss*CaSS/(CaSS+Kbufss) ;
    float   dCaSS   =   dt*(-Ixfer*(Vc/Vss)+Irel*(Vsr/Vss)
                    +   (-ICaL*inversevssF2*CAPACITANCE)) ;
    float   bcss    =   Bufss-CaSSBuf-dCaSS-CaSS+Kbufss ;
    float   ccss    =   Kbufss*(CaSSBuf+dCaSS+CaSS) ;
    CaSS            =   (sqrt(bcss*bcss+4.*ccss)-bcss)/2. ;

    float   CaBuf   =   Bufc*Cai/(Cai+Kbufc) ;
    float   dCai    =   dt*(    (   -(IbCa+IpCa-2.*INaCa)
                                    *inverseVcF2
                                    *CAPACITANCE 
                                )
                                -(Iup-Ileak)
                                *(Vsr/Vc)
                                +
                                Ixfer
                            ) ;
    float   bc      =   Bufc-CaBuf-dCai-Cai+Kbufc ;
    float   cc      =   Kbufc*(CaBuf+dCai+Cai) ;
    Cai             =   (sqrt(bc*bc+4.*cc)-bc)/2. ;

/*------------------------------------------------------------------------
 * I_SumCa
 *------------------------------------------------------------------------
 */
    float   ISumCa  = ICaL + IpCa + IbCa ;

    outCssr = vec4(Cai, CaSS, CaSR, ISumCa) ;


/*-------------------------------------------------------------------------
 * Laplacian
 *-------------------------------------------------------------------------
 */
    vec2 ii = vec2(1.0,0.0)/size ;
    vec2 jj = vec2(0.0,1.0)/size ;    
    
    float gamma = 1./3. ;

    float dVlt2dt = 
        (1.-gamma)*((   texture(inVrnk,cp+ii).r
                    -   2.0*vrnkC.r
                    +   texture(inVrnk,cp-ii).r     )*cddx
                +   (   texture(inVrnk,cp+jj).r
                    -   2.0*vrnkC.r
                    +   texture(inVrnk,cp-jj).r     )*cddy  )

        +   gamma*0.5*(     texture(inVrnk,cp+ii+jj).r
                +   texture(inVrnk,cp+ii-jj).r
                +   texture(inVrnk,cp-ii-jj).r
                +   texture(inVrnk,cp-ii+jj).r
                -   4.0*vrnkC.r               )*(cddx + cddy) ;
    dVlt2dt *= diffCoef ;

/*------------------------------------------------------------------------
 * I_sum
 *------------------------------------------------------------------------
 */
    float I_sum =  ISumCa + ISumNaK + INaCa ;

/*------------------------------------------------------------------------
 * Time integration for membrane potential
 *------------------------------------------------------------------------
 */
    dVlt2dt -= I_sum ;
    V += dVlt2dt*dt ;

    vrnkC = vec4(V, sRR, Nai, Ki ) ;
/*------------------------------------------------------------------------
 * ouputing the shader
 *------------------------------------------------------------------------
 */
    outVrnk = vrnkC ;

    return ;
}
