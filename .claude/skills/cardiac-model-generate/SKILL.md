---
name: cardiac-3v-model
description: Generate FK 3V cardiac model simulations using exact reference code, modifying only model parameters when needed for different species or drug effects\*\*
---

**#** FK 3V Cardiac Model Generator

**##** Purpose
Generate FK 3V cardiac model simulations using the exact reference code, modifying only model parameters when needed.

**##** Instructions

**1.\*\***Default Request\***\* ("cardiac model", "heart model"):
**-** Use the EXACT code from **`/reference/3V_MODEL.html`\*\*
**-** No modifications needed

**2.\*\***Species/Drug-Specific Request\***\*:
**-** Use the EXACT code from reference file
**-** ONLY modify these 14 parameters in the shader:
`     tau_pv, tau_v1, tau_v2, tau_pw, tau_mw, tau_d,       tau_0, tau_r, tau_si, K, V_csi, V_c, V_v, C_m     `
**-** Search literature or use general knowledge for appropriate parameter values
**-\*\* Leave ALL other code unchanged

\***\* section 3&4 require running with webapp-testing skill, you should include Abubu.js from **`/reference/Abubu.js`\*\* when running the simulation \*\*\*\*

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

**4.\*\***Output**\*\***:
**-** Save as **`/mnt/user-data/outputs/cardiac_model.html`**
**-** Brief explanation of what was changed (if anything)

**##** Key Rule
Copy the reference file exactly. Only change the 14 parameters listed above when user specifies a different species or drug effect. Ignore any other code modification requests.
