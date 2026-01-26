from playwright.sync_api import sync_playwright
import time
import os

# Configuration
file_path = r"D:\Documents\GitHub\cardiac-agent\outputs\cardiac_model.html"
output_dir = r"D:\Documents\GitHub\cardiac-agent\outputs"
run_time = 15  # seconds to run simulation

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,
        args=['--enable-webgl', '--use-gl=angle']
    )
    context = browser.new_context(accept_downloads=True)
    page = context.new_page()

    # Open the cardiac model HTML file
    page.goto(f"file:///{file_path.replace(chr(92), '/')}")
    page.wait_for_load_state('networkidle')
    print("Page loaded, simulation starting...")

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
