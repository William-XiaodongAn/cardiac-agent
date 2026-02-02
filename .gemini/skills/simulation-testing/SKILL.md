---
name: simulation-testing
description: Run and test WebGL cardiac simulations using Playwright, capturing screenshots after specified run times
---

# Simulation Testing

## Purpose

Run cardiac model HTML simulations with WebGL support and capture the auto-downloaded voltage trace PNG.

## Instructions

**1. Running a Simulation:**

- The cardiac model HTML includes a `saveVoltage(time)` function that auto-downloads `voltage_trace_{time}ms.png`
- Use Playwright to open the simulation and wait for the download

**2. Key Requirements:**

- WebGL simulations require headed mode (`headless=False`) for proper GPU rendering
- Set up a download handler to capture the auto-downloaded PNG
- Run simulation long enough for `saveVoltage()` to trigger (default: 1000ms simulation time)
- Remember to check console errors, if necessary, try to debug it.

**3. Example Usage:**

```python
from playwright.sync_api import sync_playwright
import time
import os

output_dir = "outputs"

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,
        args=['--enable-webgl', '--use-gl=angle']
    )
    context = browser.new_context(accept_downloads=True)
    page = context.new_page()

    # Navigate to the simulation
    page.goto(f"file:///{file_path}")
    page.wait_for_load_state('networkidle')

    # Wait for the auto-download from saveVoltage()
    with page.expect_download() as download_info:
        # Let simulation run until saveVoltage triggers
        time.sleep(15)

    # Save the downloaded file
    download = download_info.value
    download.save_as(os.path.join(output_dir, download.suggested_filename))

    browser.close()
```

**4. Parameters:**

- `file_path`: Path to the cardiac model HTML file
- `output_dir`: Where to save the downloaded voltage trace
- `run_time`: Real-time seconds to run (default 15s, adjust based on simulation speed)

## Output

- Saves the auto-downloaded `voltage_trace_{time}ms.png` to specified output folder
