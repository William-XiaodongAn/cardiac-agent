import subprocess
import argparse

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

command = [
    "python", 
    "script.py", 
    "--mode", "1", 
    "--LLM", "gemini"
]

for i in range(scale):
    subprocess.run(command)

# Run the command
result = subprocess.run(command, capture_output=True, text=True)