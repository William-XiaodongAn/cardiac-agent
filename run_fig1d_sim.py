from playwright.sync_api import sync_playwright
import time
import os

# Configuration
file_path = r"C:\Users\xan37\OneDrive - Georgia Institute of Technology\Documents\GitHub\cardiac-agent\cardiac_model_fig1d.html"
output_dir = r"C:\Users\xan37\OneDrive - Georgia Institute of Technology\Documents\GitHub\cardiac-agent\outputs"
run_time = 25  # seconds to run simulation

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

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

    # Click the "running" checkbox to start the simulation
    time.sleep(1)  # Wait for GUI to initialize
    # Find and click the running checkbox in the Abubu GUI
    page.evaluate("env.running = true")
    print("Simulation started!")

    # Run for the specified time
    print(f"Running simulation for {run_time} seconds...")
    time.sleep(run_time)

    # Save screenshot of the canvas (canvas_1)
    save_path = os.path.join(output_dir, "Fig1D_replication.png")
    
    # Locate the canvas element
    canvas = page.locator("#canvas_1")
    canvas.screenshot(path=save_path)
    print(f"Figure 1D replication saved to: {save_path}")

    browser.close()
    print("Done!")
