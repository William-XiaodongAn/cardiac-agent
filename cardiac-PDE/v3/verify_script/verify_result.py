import os
import time
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from functools import partial
import re

def load_IC(simulation_file: str, IC_file: str, T_end: float = 100.0) -> None:
    """
    Load Initial condition file to simulation file

    Args:
        simulation_file (str): The relative path to the simulation file (html).
        IC_file (str): The path to the initial condition file (csv), relative to the simulation file.
        T_end (float): The end time value. Defaults to 100.0.
    """
    with open(simulation_file, 'r') as f:
        content = f.read()

    # Regex pattern to find the content between //IC markers
    # It looks for //IC, captures everything in between, and ends at //IC
    pattern = r'(//IC\n)(.*?)(\n//IC)'
    
    # The replacement string with your new values
    replacement_content = (
        f"const IC_url = '{IC_file}';\n"
        f"const T_end = {T_end};"
    )
    
    # re.DOTALL allows the '.' to match newlines
    new_content = re.sub(
        pattern, 
        rf'\1{replacement_content}\3', 
        content, 
        flags=re.DOTALL
    )

    with open(simulation_file, 'w') as f:
        f.write(new_content)

def verify_result(simulation_file: str, IC_file: str, T_end: float = 100.0) -> None:

    load_IC(simulation_file,IC_file,T_end)
    
    PORT = 8000
    TARGET_MESSAGE = "Simulation finished!"
    URL = f"http://localhost:{PORT}/index.html"
    download_folder = os.path.join(os.getcwd(), "simulation_downloads")
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)
        print(f"Created directory: {download_folder}")    
        
    def start_server():
        """Starts a local server in the specified directory."""
        handler_with_path = partial(SimpleHTTPRequestHandler, directory=simulation_file)

        TCPServer.allow_reuse_address = True
        with TCPServer(("", PORT), handler_with_path) as httpd:
            print(f"Serving {simulation_file} at {URL}")
            httpd.serve_forever()
        
    start_server()

    # 2. Configure Chrome
    options = webdriver.ChromeOptions()
    prefs = {
    "download.default_directory": download_folder, # Sets the save path
    "download.prompt_for_download": False,          # Skips the 'Save As' popup
    "download.directory_upgrade": True,
    "profile.default_content_setting_values.automatic_downloads": 1 # Allows multiple downloads
    }
    options.add_experimental_option("prefs", prefs)    
    options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
    # Optional: This keeps the driver logs quiet in your terminal
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    driver = webdriver.Chrome(options=options)

    try:
        # 3. Open the localhost URL
        driver.get(URL)
        print("Simulation started on localhost. Monitoring console...")
    
        # wait for 10 s
        time.sleep(10)
        # --- NEW: Automatically click the Solve/Pause button ---
        try:
            # 1. Look for the span containing 'Solve/Pause'
            # We use '*' because dat.GUI doesn't use standard <button> tags
            xpath_selector = "//*[contains(text(), 'Solve/Pause')]"
            
            # 2. Wait for the element to be present and visible
            solve_element = WebDriverWait(driver, 2).until(
                EC.visibility_of_element_located((By.XPATH, xpath_selector))
            )
            
            # 3. Click the element directly via Selenium
            solve_element.click()
            print("Clicked 'Solve/Pause' GUI element successfully.")
        except Exception as e:
            print(f"Could not find or click the button automatically: {e}")
        # -------------------------------------------------------
        running = True
        while running:
            logs = driver.get_log('browser')
            for entry in logs:
                # entry['message'] often contains extra info, so we check if our string is IN it
                if TARGET_MESSAGE.lower() in entry['message'].lower():
                    print(f"Match found: '{TARGET_MESSAGE}'. Finalizing...")
                    time.sleep(5) # Give you a moment to see the final state
                    running = False
                    break
            time.sleep(1)

    finally:
        print("Shutting down...")
        driver.quit()
        # The server thread will die automatically because it's a 'daemon'
        
