---
name: cardiac-3v-model
description: Generate FK 3V cardiac model simulations using exact reference code, modifying only model parameters when needed for different species or drug effects\*\*
---

**#** FK 3V Cardiac Model Generator

**##** Purpose
Generate FK 3V cardiac model simulations using the exact reference code. Change parameters when needed (do not change paras other than those mentioned in instructions 2).

**##** Instructions

**1.\*\***Default Request\***\* ("cardiac model", "heart model"):
**-** Use the EXACT code from **`/reference/3V_MODEL.html`\*\*
**-** No modifications needed

**2.\*\***Species/Parameter change Request\***\*:
**-** Use the EXACT code from reference file
**-** DO NOT change other parameters like dt/ds/texture size
**-** ONLY modify these 14 parameters in the shader:
`     tau_pv, tau_v1, tau_v2, tau_pw, tau_mw, tau_d,       tau_0, tau_r, tau_si, K, V_csi, V_c, V_v, C_m     `
**-\*\* Search literature or use general knowledge for appropriate parameter values

**3.\*\***Pacing Request\***\* ("add pacing", "pace the heart"):
**-** Copy pacing function from **`/reference/pacing.js`\*\*
**-** Add function after march() definition
**-** Call `pacing(period)` after march() in run loop (period in ms)
**-** Default position: (0.1, 0.1), user can specify different location

**4.\*\***Save Voltage Request\***\* ("save voltage", "capture trace"):
**-** Copy saveVoltage function from **`/reference/save_voltage.js`\*\*
**-** Add `var voltageSaved = false;` at top with other variables
**-** Add function after pacing() definition  
**-** Call `saveVoltage(time)` after pacing() in run loop (time in ms)
**-** Saves canvas_2 (voltage trace) as PNG at specified time

**5. Plot Tip Request** ("plot tip", "show spiral tip"):

- Copy plotTip function from `/reference/plot_tip.js`
- Add function after march() definition (or after pacing/saveVoltage if present)
- Call `plotTip(startTime, endTime)` after march() in the run loop
- Controls visibility of the spiral tip plot between the specified start and end times (in ms, minimum 1000ms for fine results)

**6. S1-S2 Initialization Request** ("S1-S2", "spiral initiation", "spiral wave"):

**CRITICAL: Copy ALL code from `/reference/S1_S2_init.html` EXACTLY. Do NOT modify or simplify the logic.**

Step-by-step:

1. **Replace the `init` shader** - Copy the EXACT `<script id='init'>` from S1_S2_init.html (includes `if ( cc.x < 0.1 ){ color.r = 1. ; }`)

2. **Add the `initS1S2` shader** - Copy the EXACT `<script id='initS1S2'>` shader from S1_S2_init.html

3. **Add the initS1S2 solver** - Copy EXACTLY after `init.render();`:

```javascript
var initS1S2 = new Abubu.Solver({
  fragmentShader: source("initS1S2"),
  uniforms: {
    inTexture: { type: "t", value: fcolor },
  },
  targets: {
    color1: { location: 0, target: scolor },
  },
});
```

4. **Add S1-S2 state variables** - Copy EXACTLY:

```javascript
var turn_red_first = false;
var turn_red_second = false;
var measurePoint = 525312;
```

5. **Add S1S2Init function** - Copy EXACTLY (do NOT change the logic or threshold values):

```javascript
function S1S2Init() {
  if (!turn_red_first && fcolor.value[measurePoint] >= 0.9) {
    turn_red_first = true;
  }
  if (turn_red_first && !turn_red_second && fcolor.value[measurePoint] < 0.1) {
    turn_red_second = true;
    initS1S2.render();
    clickCopy.render();
  }
}
```

6. **Call in run loop** - Add `S1S2Init();` after `march();` in the run loop

7. **Update env.initialize** - Reset S1-S2 variables:

```javascript
turn_red_first = false;
turn_red_second = false;
```

**WARNING: Do NOT create your own time-based S2 trigger. The reference uses voltage-based detection at measurePoint. Copy it exactly.**

**7.\*\***Output**\*\***:
**-** Save as **`/mnt/user-data/outputs/cardiac_model.html`**
**-** Brief explanation of what was changed (if anything)
