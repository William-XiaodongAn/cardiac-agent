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
import threading
import shutil
from pathlib import Path

def load_IC(LLM,simulation_file_path: str, IC_file_path: str, T_end: float = 100.0) -> None:
    """
    Load Initial condition file to simulation file

    Args:
        simulation_file (str): The relative path to the simulation file (html).
        IC_file (str): The path to the initial condition file (csv), relative to the simulation file.
        T_end (float): The end time value. Defaults to 100.0.
    """
    # first, copy simulation file to the same folder as IC file.
    destination = os.path.join(os.path.dirname(IC_file_path), f'simulation_{LLM}.html')
    shutil.copy2(simulation_file_path, destination)
    
    simulation_file_path = destination
    
    with open(simulation_file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex pattern to find the content between //IC markers
    # It looks for //IC, captures everything in between, and ends at //IC
    pattern = r'(//IC\n)(.*?)(\n//IC)'
    
    # The replacement string with your new values
    IC_file_name = os.path.basename(IC_file_path)
    replacement_content = (
        f"const IC_url = '{IC_file_name}';\n"
        f"const T_end = {T_end};"
    )

    
    # re.DOTALL allows the '.' to match newlines
    new_content = re.sub(
        pattern, 
        rf'\1{replacement_content}\3', 
        content, 
        flags=re.DOTALL
    )
    
    # Write the modified content back to the file
    with open(simulation_file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    return simulation_file_path

def verify_result(LLM,simulation_file_path: str, IC_file_path: str, T_end: float,download_folder:str) -> None:

    simulation_file_path = load_IC(LLM,simulation_file_path,IC_file_path,T_end)
    
    # Get the directory where simulation_{LLM}.html is located
    simulation_directory = os.path.dirname(simulation_file_path)
    
    PORT = 8001
    TARGET_MESSAGE = "Simulation finished!"
    URL = f"http://localhost:{PORT}/simulation_{LLM}.html"
    
    download_path = Path(download_folder).resolve()
    download_path.mkdir(parents=True, exist_ok=True)
    
    target_file = download_path / "result.csv"
    if target_file.exists():
        print(f"Removing old {target_file.name} to prevent renaming...")
        target_file.unlink()
            
    def start_server():
        """Starts a local server in the specified directory."""
        handler_with_path = partial(SimpleHTTPRequestHandler, directory=simulation_directory)

        TCPServer.allow_reuse_address = True
        with TCPServer(("", PORT), handler_with_path) as httpd:
            print(f"Serving {simulation_file_path} at {URL}")
            httpd.serve_forever()
        
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start() # Moves to the next line of code immediately
    
    # Convert download_folder to absolute path with forward slashes for Chrome
    abs_download_folder = str(download_path)
    print(f"Download folder set to: {abs_download_folder}")
    
    # 2. Configure Chrome
    options = webdriver.ChromeOptions()
    prefs = {
    "download.default_directory": abs_download_folder,  # Use absolute path with forward slashes
    "download.prompt_for_download": False,          # Skips the 'Save As' popup
    "download.directory_upgrade": True,
    "profile.default_content_setting_values.automatic_downloads": 1, # Allows multiple downloads
    "safebrowsing.enabled": True, 
    "download.extensions_to_open": ""
    }
    options.add_experimental_option("prefs", prefs)    
    options.add_argument("--safebrowsing-disable-download-protection")
    options.add_argument("--safebrowsing-disable-extension-blacklist")
    options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
    # Optional: This keeps the driver logs quiet in your terminal
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    driver = webdriver.Chrome(options=options)

    try:
        # 3. Open the localhost URL
        driver.get(URL)
        print("Simulation started on localhost. Monitoring console...")
        time.sleep(2)  # Wait for page to fully load and GUI to initialize
        

        driver.execute_script("window.env.solve();")
        print("Started simulation using JavaScript injection.")

        # -------------------------------------------------------
        error_found = None
        running = True
        while running:
            logs = driver.get_log('browser')
            for entry in logs:
                # Skip harmless favicon.ico 404 errors
                if 'favicon.ico' in entry['message']:
                    continue
                    
                if entry['level'] == 'SEVERE':
                    print(entry)
                    error_found = logs
                    running = False # Exit loop on bug
                    break
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
    return error_found if error_found else "Success"
        
