import pde_descriptions
from prompts import system_prompt,parse_prompt,code_prompt,debug_prompt,refine_prompt
from verify_script.verify_result import *
import json
import ollama
import os
from dotenv import load_dotenv
import re
from openai import OpenAI
import anthropic
from google import genai
from google.genai import types # Required for Gemini config
import numpy as np
import argparse
import pickle

load_dotenv()

class LLMFactory:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    def ask_gpt(self, model, system_prompt, user_prompt):
        response = self.openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        return response.choices[0].message.content

    def ask_claude(self, model, system_prompt, user_prompt):
        # Claude takes 'system' as a separate argument, not inside 'messages'
        message = self.anthropic_client.messages.create(
            model=model,
            max_tokens=1024,
            system=system_prompt, 
            messages=[{"role": "user", "content": user_prompt}]
        )
        return message.content[0].text

    def ask_gemini(self, model, system_prompt, user_prompt):
        # Gemini uses 'config' to pass system instructions
        response = self.gemini_client.models.generate_content(
            model=model,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt
            )
        )
        return response.text

    def ask_ollama(self, model, user_prompt):
        messages = []
        
        messages.append({'role': 'user', 'content': user_prompt})
        
        response = ollama.chat(model=model, messages=messages)
        return response['message']['content']

# --- The Router Function ---
def chat_with(model_name, system_prompt, user_prompt):
    factory = LLMFactory()
    m_lower = model_name.lower()
    
    if "gpt" in m_lower:
        return factory.ask_gpt(model_name, system_prompt, user_prompt)
    elif "claude" in m_lower:
        return factory.ask_claude(model_name, system_prompt, user_prompt)
    elif "gemini" in m_lower:
        return factory.ask_gemini(model_name, system_prompt, user_prompt)
    else:
        return factory.ask_ollama(model_name, user_prompt)


def parse_agent(LLM:str,pde_name:str,pde_paras:dict):
    '''
    Parse the pde description and extract necessary information to a json file.
    '''
    # sanitize LLM
    LLM_original_name = LLM
    LLM = re.sub(r'[.\-:]', '_', LLM)
        
    pde_desc = getattr(pde_descriptions, pde_name.replace('.','_'))
    pde_desc = pde_desc.format(**pde_paras)
    user_prompt = parse_prompt.format(
        user_input=pde_name,
    )
    user_prompt = f"{pde_desc}\n\n{user_prompt}"
    

    
    response_text = chat_with(LLM_original_name, system_prompt, user_prompt)
    
    #deleat ```json at beginning of response.text if exist
    if response_text.startswith("```json"):
        response_text = response_text[len("```json"):]

    #deleat ``` at end of response.text if exist
    if response_text.endswith("```"):
        response_text = response_text[:-3]

    # save json to ./result/{pde_name}/{LLM}/parsed_resp.json
    # create folder it not exist
    os.makedirs(f"./result/{LLM}/{pde_name}", exist_ok=True)
    with open(f"./result/{LLM}/{pde_name}/parsed_resp.json", "w", encoding="utf-8") as f:
        f.write(response_text)
    
    print(f"Parsed response saved to ./result/{LLM}/{pde_name}/parsed_resp.json")

def skeleton_prepare(LLM:str,pde_name:str):
    '''
    Prepare the coding skeleton file (.html) needed by code agent.
    '''
    LLM_original_name = LLM
    LLM = re.sub(r'[.\-:]', '_', LLM)      
    with open(f"./result/{LLM}/{pde_name}/parsed_resp.json", "r", encoding="utf-8") as f:
        parsed_resp = json.load(f)
        
    number_of_state_variables = parsed_resp["number_of_state_variables"]
    texture_size = parsed_resp["texture_size"]
    spatial_step = parsed_resp["spatial_step"]
    temporal_step = parsed_resp["temporal_step"]
    time_horizon = parsed_resp["time_horizon"]
    parameter_values = parsed_resp["parameter_values"]
    parameter_values
    parameter_str = "\n".join([
        f"    const float {k} = {v};"
        for k, v in parameter_values.items()
        ])
    
    coding_skeleton_file = f"./skeleton_script/{parsed_resp['number_of_state_variables']}V/skeleton.html"
    # Load the file
    with open(coding_skeleton_file, 'r') as f:
        html_template = f.read()

    # Replace placeholders with your Python variables
    updated_html = html_template.replace('{{DT_VALUE}}', str(temporal_step)).replace('{{DX_VALUE}}', str(spatial_step))
    updated_html = updated_html.replace('{{TEXTURE_VALUE}}', str(texture_size))
    
    with open(f"./result/{LLM}/{pde_name}/skeleton.html", 'w') as f:
        f.write(updated_html)
    
    with open(f"./skeleton_script/{parsed_resp['number_of_state_variables']}V/march_skeleton.frag", 'r') as f:
        coding_skeleton = f.read()
    updated_coding_skeleton = coding_skeleton.replace('{{PARAMETER_VALUES}}', parameter_str)
    return updated_coding_skeleton

def code_agent(LLM:str,pde_name:str):
    '''
    Code the march shader and save it to march_shader.frag and simulation.html.
    '''
    LLM_original_name = LLM
    LLM = re.sub(r'[.\-:]', '_', LLM)      
    updated_coding_skeleton = skeleton_prepare(LLM, pde_name)
    
    with open(f"./result/{LLM}/{pde_name}/parsed_resp.json", "r", encoding="utf-8") as f:
        parsed_resp = json.load(f)
        
    user_prompt = code_prompt.format(
        PDEs=parsed_resp["PDEs"],
        coding_skeleton = updated_coding_skeleton
    )
    
  
    response_text = chat_with(LLM_original_name, system_prompt, user_prompt)
    
    #deleat ```glsl at beginning of response.text if exist
    if response_text.startswith("```glsl"):
        response_text = response_text[len("```glsl"):]

    # #deleat ``` at end of response.text if exist
    if response_text.endswith("```"):
        response_text = response_text[:-3]  

    with open(f"./result/{LLM}/{pde_name}/march_shader.frag", "w", encoding="utf-8") as f:
        f.write(response_text)
        
    # replace march shader script in skeleton.html with the generated march shader code
    with open(f'./result/{LLM}/{pde_name}/skeleton.html', 'r') as f:
        html_content = f.read()
        
    with open(f'./result/{LLM}/{pde_name}/march_shader.frag', 'r') as f:    
        march_shader_code = f.read()
        
    updated_html = html_content.replace('{{MARCH_SHADER_CODE}}', march_shader_code)

    with open(f'./result/{LLM}/{pde_name}/simulation.html', 'w') as f:
        f.write(updated_html)
    simulation_file_path = f'./result/{LLM}/{pde_name}/simulation.html'
    print(f"Simulation code saved to {simulation_file_path}")
    return simulation_file_path

def verify_agent(LLM,pde_name,simulation_file_path,IC_file_path,download_folder,log_file_path,solution_file_path): # reference data should be ref sol in r channel as 1d array
    def load_csv(csv_path):
        result_data = np.loadtxt(csv_path, delimiter=',')
        # skip first two data points
        result_data = result_data[2:]
        # the remaining data is r,g,b,a,r,g,b,a,..., and we only need r channel
        result_data = result_data[::4]
        return result_data
    LLM_original_name = LLM
    LLM = re.sub(r'[.\-:]', '_', LLM)
            
    with open(f"./result/{LLM}/{pde_name}/parsed_resp.json", "r", encoding="utf-8") as f:
        parsed_resp = json.load(f)
    T_end = parsed_resp["time_horizon"]
    
    logs = verify_result(simulation_file_path, IC_file_path, T_end, download_folder)

    if logs != "Success":
        # create the path
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
        
        with open(log_file_path, "w", encoding="utf-8") as f:
            for entry in logs:
                # Format: [LEVEL] Timestamp - Message
                line = f"[{entry['level']}] {entry['timestamp']} - {entry['message']}\n"
                f.write(line)
        print(f"Verification failed. Logs saved to {log_file_path}")
        return 1e10
    else:
        result = os.path.join(download_folder, "result.csv")
        
        result_data = load_csv(result)
        reference_data = load_csv(solution_file_path)
        
        rmse = np.sqrt(np.mean((result_data - reference_data) ** 2))
        norm = np.sqrt(np.mean(reference_data ** 2))
        normalized_rmse = rmse / norm
        print(f"Verification successful. Normalized RMSE: {normalized_rmse}")
        return normalized_rmse

def debug_agent(LLM,pde_name,log_file_path,bugged_html_path,debugged_html_path):
    
    LLM_original_name = LLM
    LLM = re.sub(r'[.\-:]', '_', LLM)
    
    with open(log_file_path, "r", encoding="utf-8") as f:
        logs = f.read()
    with open(bugged_html_path, "r") as f:
        # find codes between
        # <script id='march' type='shader'>#version 300 es
        # </script>
        html_content = f.read()
        pattern = r"<script id='march' type='shader'>(.*?)</script>"
        match = re.search(pattern, html_content, re.DOTALL)
        march_shader_code = match.group(1).strip()
        
    debug_prompt_text = debug_prompt.format(
        shader_codes = march_shader_code,
        log_info = logs
    )

    response_text = chat_with(LLM_original_name, system_prompt, debug_prompt_text)
    if response_text.startswith("```glsl"):
        response_text = response_text[len("```glsl"):]
    # deleat #version 300 es at beginning of response.text if exist
    if response_text.startswith("#version 300 es"):
        response_text = response_text[len("#version 300 es"):].lstrip()  # also remove leading whitespace

    # #deleat ``` at end of response.text if exist
    if response_text.endswith("```"):
        response_text = response_text[:-3]
    
    # save to html
    with open(f"./result/{LLM}/{pde_name}/skeleton.html", 'r') as f:
        html_content = f.read()
    updated_html = html_content.replace('{{MARCH_SHADER_CODE}}', response_text)
    with open(debugged_html_path, 'w') as f:
        f.write(updated_html)
        
    
def main():    
    parser = argparse.ArgumentParser()
    
    parser.add_argument("--LLM", help="The name of LLM")
    parser.add_argument(
            "--pde", 
            choices=["advection_beta0.1","advection_beta1.0", "burgers_nu0.001","burgers_nu1.0","twoD_reaction_diffusion","fenton_karma"], 
            help="pde has to be one of advection, burgers, twoD_reaction_diffusion, or fenton_karma."
        )
    parser.add_argument(
            "--mode",
            choices=["full_train","no_refine_train","dry_run"],
        )
    
    parser.add_argument(
        "--debug_trail_times",
        default=5,
        type=int,
        help="The number of debugging trials when the simulation fails. Default is 5."
    )
    
    args = parser.parse_args()
    LLM_sanitized = re.sub(r'[.\-:]', '_', args.LLM)
    if args.mode == "dry_run":
        print("Testing imports and environment setup...")
        print("✓ All imports loaded successfully")
        print("✓ Environment variables loaded")
        print("Dry run complete!")
        return

    if args.mode == "full_train":
        pde_paras_file_path = f"./data/{args.pde}/{args.pde}_paras.pkl"
        with open(pde_paras_file_path, 'rb') as f:
            pde_paras = pickle.load(f)
        
        IC_folder = f"./data/{args.pde}/train"
        IC_files = [f for f in os.listdir(IC_folder) if f.endswith(('.csv')) and f.startswith("IC_")] # IC_0.csv,IC_1.csv,...
        solution_folder = f"./data/{args.pde}/train"
        solution_files = [f for f in os.listdir(solution_folder) if f.endswith(('.csv')) and f.startswith("solution_")] # solution_0.csv,solution_1.csv,...
        
        parse_agent(args.LLM,args.pde,pde_paras)
        simulation_file_path = code_agent(args.LLM,args.pde)
        debugged_file_path = simulation_file_path
        debugged_times_used = 0
        
        nrmse_list = []
        for IC_file in IC_files:
            index = IC_file.split('_')[1].split('.')[0] # get 0 from IC_0.csv
            IC_file = os.path.join(IC_folder, IC_file)
            
            solution_file = f"solution_{index}.csv"
            solution_file = os.path.join(solution_folder, solution_file)
            
            download_folder = f"./result/{LLM_sanitized}/{args.pde}/{debugged_times_used}_debug_times/IC_{index}"
            log_file_path = f"{download_folder}/log.txt"
            normalized_rmse = verify_agent(args.LLM,args.pde,simulation_file_path,IC_file,download_folder,log_file_path,solution_file)
            # save the normalized_rmse to a txt file
            with open(f"./result/{LLM_sanitized}/{args.pde}/{debugged_times_used}_debug_times/IC_{index}/normalized_rmse.txt", "w") as f:
                f.write(str(normalized_rmse))
            
            while normalized_rmse > 0.1 and debugged_times_used < args.debug_trail_times:
                debugged_times_used += 1
                bugged_file_path = debugged_file_path
                debugged_file_path = f"./result/{LLM_sanitized}/{args.pde}/{debugged_times_used}_debug_times/IC_{index}/simulation.html"
                download_folder = f"./result/{LLM_sanitized}/{args.pde}/{debugged_times_used}_debug_times/IC_{index}"
                log_file_path = f"{download_folder}/log.txt"
                debug_agent(args.LLM,args.pde,log_file_path,bugged_file_path,debugged_file_path)
                normalized_rmse = verify_agent(args.LLM,args.pde,debugged_file_path,IC_file,download_folder,log_file_path,solution_file)

            nrmse_list.append(normalized_rmse)
        print(debugged_times_used, nrmse_list)
        
if __name__ == "__main__":
    main()
