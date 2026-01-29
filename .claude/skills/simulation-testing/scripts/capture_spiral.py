from playwright.sync_api import sync_playwright
import time
import os

# Configuration
file_path = r"C:\Users\xan37\OneDrive - Georgia Institute of Technology\Documents\GitHub\cardiac-agent\outputs\cardiac_model.html"
output_dir = r"C:\Users\xan37\OneDrive - Georgia Institute of Technology\Documents\GitHub\cardiac-agent\outputs"
run_time = 20  # seconds to run simulation - capture spiral at ~600-800ms sim time

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,
        args=['--enable-webgl', '--use-gl=angle']
    )
    context = browser.new_context(
        viewport={'width': 1200, 'height': 800},
        accept_downloads=True
    )
    page = context.new_page()

    # Open the cardiac model HTML file
    page.goto(f"file:///{file_path.replace(chr(92), '/')}")
    page.wait_for_load_state('networkidle')
    print("Page loaded...")

    # Wait for GUI to initialize then start simulation
    time.sleep(1)
    page.evaluate("env.running = true")
    print("Simulation started!")

    # Run simulation to allow spiral to form
    # S2 triggers at ~150ms, spiral should be visible around 500-1000ms
    print(f"Running simulation for {run_time} seconds to capture spiral wave...")
    time.sleep(run_time)

    # Check simulation time
    sim_time = page.evaluate("env.time")
    print(f"Simulation time: {sim_time:.1f} ms")

    # Capture screenshot of the main canvas (spiral wave visualization)
    canvas = page.locator("#canvas_1")
    screenshot_path = os.path.join(output_dir, f"spiral_wave_{int(sim_time)}ms.png")
    canvas.screenshot(path=screenshot_path)
    print(f"Spiral wave screenshot saved to: {screenshot_path}")

    # Also capture full page screenshot
    full_screenshot_path = os.path.join(output_dir, f"simulation_full_{int(sim_time)}ms.png")
    page.screenshot(path=full_screenshot_path)
    print(f"Full simulation screenshot saved to: {full_screenshot_path}")

    browser.close()
    print("Done!")
