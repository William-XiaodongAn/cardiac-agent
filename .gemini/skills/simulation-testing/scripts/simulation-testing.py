from playwright.sync_api import sync_playwright
import time
import os

# Configuration
file_path = r"C:\Users\xan37\OneDrive - Georgia Institute of Technology\Documents\GitHub\cardiac-agent\outputs\cardiac_model.html"
output_dir = r"C:\Users\xan37\OneDrive - Georgia Institute of Technology\Documents\GitHub\cardiac-agent\outputs"
run_time = 20  # seconds to run simulation (enough for 3000ms simulation time)

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,
        args=['--enable-webgl', '--use-gl=angle']
    )
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080}, # Set to a standard widescreen size
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

    # Wait for the auto-download from saveVoltage()
    print(f"Running simulation for {run_time} seconds, waiting for voltage trace download...")
    with page.expect_download(timeout=run_time * 1000 + 5000) as download_info:
        time.sleep(run_time)

    # Save the downloaded file
    download = download_info.value
    save_path = os.path.join(output_dir, download.suggested_filename)
    download.save_as(save_path)
    print(f"Voltage trace saved to: {save_path}")

    browser.close()
    print("Done!")
