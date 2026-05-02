import subprocess
import argparse
import re
import os
import glob
import shutil
import json

LLMs = ["gemma4:26b", "gemini-2.5-flash", "gpt-oss:20b"]
PDEs = ["advection_beta0.1","advection_beta1.0", "burgers_nu0.001","burgers_nu1.0","fenton_karma"]
def main():    
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--debug_times",
        default=5,
        type=int,
    )

    parser.add_argument(
        "--scale",
        default=5,
        type=int,
    )
    
    args = parser.parse_args()
    debug_trail_times = args.debug_trail_times
    scale = args.scale

    result = {}
    
    for i in range(scale):
        for LLM in LLMs:
            for PDE in PDEs:
                command = [
                    "python", 
                    "script.py", 
                    "--mode", "full_train", 
                    "--LLM", LLM, 
                    "--pde", PDE, 
                    "--debug_trail_times", str(debug_trail_times)
                ]
                subprocess.run(command)
                
                # Sanitize and fetch
                LLM_sanitized = re.sub(r'[.\-:]', '_', args.LLM)
                folders = glob.glob(f"./result/{LLM_sanitized}/{PDE}/*_debugged_times")

                # Get the latest folder (returns None if folders list is empty)
                debugged_folder = max(folders, key=lambda x: int(os.path.basename(x).split('_')[0]), default=None)
                max_debugged_times = int(os.path.basename(debugged_folder).split('_')[0])
                nRMSE_lst = []
                
                # now find all IC_* folder
                IC_folders = glob.glob(os.path.join(debugged_folder, "IC_*"))
                for IC_folder in IC_folders:
                    log_file = os.path.join(IC_folder, "log.txt")
                    with open(log_file, 'r') as f:
                        # if start with "nRMSE:", then get the nRMSE value
                        for line in f:
                            if line.startswith("nRMSE:"):
                                nRMSE_lst.append(float(line.split("nRMSE:")[1].strip()))
                                break
                            else:
                                nRMSE_lst.append(float('inf'))  # if no nRMSE found, set it to inf
                
                result[scale][LLM][PDE]['nRMSE'] = nRMSE_lst
                result[scale][LLM][PDE]['max_debugged_times'] = max_debugged_times
                
                # now move debugged_folder to destination_folder
                destination_folder = f"./result/{LLM_sanitized}/{PDE}/scale_{i}"
                os.makedirs(destination_folder, exist_ok=True)
                shutil.move(debugged_folder, destination_folder)
                
                
                
    # Run the command
    subprocess.run(command, capture_output=True, text=True)
    
    # save result
    with open("experiment_result.json", "w") as f:
        json.dump(result, f, indent=4)
if __name__ == "__main__":
    main()