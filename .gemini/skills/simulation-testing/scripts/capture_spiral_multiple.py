#!/usr/bin/env python3
"""
Capture spiral wave screenshots at multiple time points from FK 3V cardiac model simulation
"""

from playwright.sync_api import sync_playwright
import time
import os
import sys

def capture_spiral_screenshots(file_path, output_dir, time_points):
    """
    Run cardiac simulation and capture canvas_1 screenshots at specified simulation times

    Args:
        file_path: Path to the HTML simulation file
        output_dir: Directory to save screenshots
        time_points: List of simulation times (in ms) to capture
    """

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Convert file path to absolute path with proper file:// URL
    abs_path = os.path.abspath(file_path).replace('\\', '/')
    file_url = f"file:///{abs_path}"

    print(f"Opening simulation: {file_url}")
    print(f"Capture times: {time_points} ms")

    with sync_playwright() as p:
        # Launch browser in headed mode for WebGL support
        browser = p.chromium.launch(
            headless=False,
            args=['--enable-webgl', '--use-gl=angle']
        )

        context = browser.new_context(
            viewport={'width': 1280, 'height': 900}
        )
        page = context.new_page()

        # Navigate to the simulation
        page.goto(file_url)
        page.wait_for_load_state('networkidle')

        # Wait for canvas to be ready
        time.sleep(2)

        # Start the simulation by clicking the "running" checkbox
        try:
            # The dat.GUI checkbox for running is typically a label
            page.evaluate("""
                () => {
                    env.running = true;
                }
            """)
            print("Simulation started")
        except Exception as e:
            print(f"Could not auto-start simulation: {e}")
            print("Please manually start the simulation by clicking 'running' in the GUI")

        # Track captured times
        captured_times = set()

        # Monitor simulation and capture at specified times
        max_wait_time = max(time_points) * 0.025 / 1000 * 50  # Estimate real time needed
        start_time = time.time()
        check_interval = 0.5  # Check every 0.5 seconds

        print(f"\nMonitoring simulation (estimated max wait: {max_wait_time:.1f}s)...")

        while time.time() - start_time < max_wait_time + 30:  # Add buffer
            # Get current simulation time
            try:
                sim_time = page.evaluate("() => env.time")

                # Check if we should capture at this time
                for target_time in time_points:
                    if target_time not in captured_times and sim_time >= target_time:
                        # Capture canvas_1 (the spiral wave visualization)
                        canvas = page.locator('#canvas_1')
                        screenshot_path = os.path.join(output_dir, f'spiral_wave_{target_time}ms.png')
                        canvas.screenshot(path=screenshot_path)
                        print(f"[OK] Captured at {sim_time:.1f}ms -> {screenshot_path}")
                        captured_times.add(target_time)

                # Exit if all screenshots captured
                if len(captured_times) == len(time_points):
                    print(f"\n[OK] All {len(time_points)} screenshots captured successfully!")
                    break

            except Exception as e:
                print(f"Error reading simulation time: {e}")

            time.sleep(check_interval)

        # Check if we captured everything
        if len(captured_times) < len(time_points):
            missed = set(time_points) - captured_times
            print(f"\n[WARNING] Only captured {len(captured_times)}/{len(time_points)} screenshots")
            print(f"Missed times: {sorted(missed)} ms")

        # Keep browser open briefly to see final state
        time.sleep(2)

        browser.close()
        print("\nBrowser closed")

if __name__ == "__main__":
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage: python capture_spiral_multiple.py <html_file> [--times t1,t2,t3,...] [--output dir]")
        sys.exit(1)

    html_file = sys.argv[1]

    # Default values
    time_points = [500, 1000, 1500, 2000]
    output_dir = "outputs"

    # Parse optional arguments
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--times" and i + 1 < len(sys.argv):
            time_points = [int(t) for t in sys.argv[i + 1].split(',')]
            i += 2
        elif sys.argv[i] == "--output" and i + 1 < len(sys.argv):
            output_dir = sys.argv[i + 1]
            i += 2
        else:
            i += 1

    print("=" * 60)
    print("FK 3V Cardiac Model - Spiral Wave Screenshot Capture")
    print("=" * 60)

    capture_spiral_screenshots(html_file, output_dir, time_points)
