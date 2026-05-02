import pde_descriptions
from prompts import system_prompt,parse_prompt,code_prompt,debug_prompt,refine_prompt,validate_parse_prompt
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
        self.ollama_client = ollama.Client(
                    host="https://ollama.com",
                    headers={'Authorization': f"Bearer {os.getenv('OLLAMA_API_KEY')}"}
                )

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
        
        response = self.ollama_client.chat(model=model, messages=messages)
        return response['message']['content']

    def ask_ollama_local(self, model, user_prompt):
        messages = []
        
        messages.append({'role': 'user', 'content': user_prompt})
        
        response = ollama.chat(model=model, messages=messages)
        return response['message']['content']
    
# --- The Router Function ---
def chat_with(model_name, system_prompt, user_prompt):
    factory = LLMFactory()
    m_lower = model_name.lower()
    
    if "gt" in m_lower:
        return factory.ask_gpt(model_name, system_prompt, user_prompt)
    elif "claude" in m_lower:
        return factory.ask_claude(model_name, system_prompt, user_prompt)
    elif "gemini" in m_lower:
        return factory.ask_gemini(model_name, system_prompt, user_prompt)
    elif "cloud" in m_lower:
        return factory.ask_ollama(model_name, user_prompt)
    else:
        return factory.ask_ollama_local(model_name, user_prompt)
        

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
        user_input=pde_desc,
    )
    
    response_text = chat_with(LLM_original_name, system_prompt, user_prompt)
    # deleat <think> *</think> if exist
    response_text = re.sub(r'<think>.*?</think>', '', response_text, flags=re.DOTALL).strip()
    
    # prune the response_text to make it a valid json string between the closest '''json and ''' if exist
    json_pattern = r"```json(.*)```"
    match = re.search(json_pattern, response_text, re.DOTALL)
    if match:
        response_text = match.group(1).strip()
    

    # save json to ./result/{pde_name}/{LLM}/parsed_resp.json
    # create folder it not exist
    os.makedirs(f"./result/{LLM}/{pde_name}", exist_ok=True)
    with open(f"./result/{LLM}/{pde_name}/parsed_resp.json", "w", encoding="utf-8") as f:
        f.write(response_text)
    
    print(f"Parsed response saved to ./result/{LLM}/{pde_name}/parsed_resp.json")

def check_parsed_response(LLM:str,pde_name:str):
    '''
    Check if the parsed response json file is valid.
    Let LLM review parameters and save the returned JSON.
    '''
    
    LLM_original_name = LLM
    LLM_sanitized = re.sub(r'[.\-:]', '_', LLM)
    if not os.path.exists(f"./result/{LLM_sanitized}/{pde_name}/parsed_resp.json"):
        return False

    
    with open(f"./result/{LLM_sanitized}/{pde_name}/parsed_resp.json", "r", encoding="utf-8") as f:
        parsed_resp = json.load(f)
    
    # Get PDE description
    pde_desc = getattr(pde_descriptions, pde_name.replace('.','_'))
    pde_paras_file_path = f"./data/{pde_name}/{pde_name}_paras.pkl"

    with open(pde_paras_file_path, 'rb') as f:
        pde_paras = pickle.load(f)
    pde_desc = pde_desc.format(**pde_paras)

    
    # Ask LLM to review and return JSON
    validation_prompt_text = validate_parse_prompt.format(
        pde_desc=pde_desc,
        json=json.dumps(parsed_resp, indent=2)
    )
    
    response_text = chat_with(LLM_original_name, system_prompt, validation_prompt_text)
    
    # Extract and save JSON response
    json_pattern = r"```json\s*(.*?)\s*```|{.*}"
    json_pattern = r"```json(.*)```"
    match = re.search(json_pattern, response_text, re.DOTALL)
    if match:
        json_str = match.group(1).strip()

    
    try:
        updated_resp = json.loads(json_str)
        with open(f"./result/{LLM_sanitized}/{pde_name}/parsed_resp.json", "w", encoding="utf-8") as f:
            json.dump(updated_resp, f, indent=2)
    except:
        print(f"Warning: Could not parse LLM response, keeping original.")
    
    
    # Check required fields
    required_dict = {"PDEs": str, "number_of_state_variables": int, "texture_size": int, "spatial_step": float, "domain_size": float, "temporal_step": float, "time_horizon": float, "boundary_conditions": object, "parameter_values": dict}
    for key in required_dict.keys():
        if key not in parsed_resp:
            return False
        val = parsed_resp[key]
        expected_type = required_dict[key]
        if not isinstance(val, expected_type):
            return False
        
    print(f"Parsed response for {LLM_original_name} and {pde_name} is valid.")
    return True

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
    with open(coding_skeleton_file, 'r', encoding='utf-8') as f:
        html_template = f.read()

    # Replace placeholders with your Python variables
    updated_html = html_template.replace('{{DT_VALUE}}', str(temporal_step)).replace('{{DX_VALUE}}', str(spatial_step))
    updated_html = updated_html.replace('{{TEXTURE_VALUE}}', str(texture_size))
    
    with open(f"./result/{LLM}/{pde_name}/skeleton.html", 'w', encoding='utf-8') as f:
        f.write(updated_html)
    
    with open(f"./skeleton_script/{parsed_resp['number_of_state_variables']}V/march_skeleton.frag", 'r', encoding='utf-8') as f:
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
        coding_skeleton = updated_coding_skeleton,
        bc = parsed_resp["boundary_conditions"],
        notes = parsed_resp.get("notes", "null")
    )
    
  
    response_text = chat_with(LLM_original_name, system_prompt, user_prompt)
    
    # find codes between ```glsl and ``` if exist
    glsl_pattern = r"```glsl(.*)```"
    match = re.search(glsl_pattern, response_text, re.DOTALL)
    if match:
        response_text = match.group(1).strip()

    with open(f"./result/{LLM}/{pde_name}/march_shader.frag", "w", encoding="utf-8") as f:
        f.write(response_text)
        
    # replace march shader script in skeleton.html with the generated march shader code
    with open(f'./result/{LLM}/{pde_name}/skeleton.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
        
    with open(f'./result/{LLM}/{pde_name}/march_shader.frag', 'r', encoding='utf-8') as f:    
        march_shader_code = f.read()
        
    updated_html = html_content.replace('{{MARCH_SHADER_CODE}}', march_shader_code)

    with open(f'./result/{LLM}/{pde_name}/simulation.html', 'w', encoding='utf-8') as f:
        f.write(updated_html)
    simulation_file_path = f'./result/{LLM}/{pde_name}/simulation.html'
    print(f"Simulation code saved to {simulation_file_path}")
    return simulation_file_path

def verify_agent(LLM,pde_name,simulation_file_path,IC_file_path,download_folder,log_file_path,solution_file_path): # reference data should be ref sol in r channel as 1d array
    def load_csv(csv_path):
        result_data = np.loadtxt(csv_path, delimiter=',')
        # skip first two data points
        result_data = result_data[2:]
        return result_data
    LLM_original_name = LLM
    LLM = re.sub(r'[.\-:]', '_', LLM)
            
    with open(f"./result/{LLM}/{pde_name}/parsed_resp.json", "r", encoding="utf-8") as f:
        parsed_resp = json.load(f)
    T_end = parsed_resp["time_horizon"]
    
    logs = verify_result(LLM,simulation_file_path, IC_file_path, T_end, download_folder)
    # create the path
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
    if logs != "Success":
        with open(log_file_path, "w", encoding="utf-8") as f:
            for entry in logs:
                # Format: [LEVEL] Timestamp - Message
                line = f"[{entry['level']}] {entry['timestamp']} - {entry['message']}\n"
                f.write(line)
        print(f"Verification failed. Logs saved to {log_file_path}")
        return 1e10
    else:

        result = os.path.join(download_folder, "result.csv")

        
        result_data = np.loadtxt(result, delimiter=',')
        result_data = result_data[::4]
        reference_data = load_csv(solution_file_path)
        reference_data = reference_data[::4]

        rmse = np.sqrt(np.mean((result_data - reference_data) ** 2))
        norm = np.sqrt(np.mean(reference_data ** 2))
        normalized_rmse = rmse / norm
        if not np.isfinite(normalized_rmse):
            normalized_rmse = 1e10
        with open(log_file_path, "w", encoding="utf-8") as f:
            f.write("nRMSE: " + str(normalized_rmse))
        print(f"Verification successful. Normalized RMSE: {normalized_rmse}")
        return normalized_rmse

def debug_agent(LLM,pde_name,log_file_path,bugged_html_path,debugged_html_path):
    
    LLM_original_name = LLM
    LLM = re.sub(r'[.\-:]', '_', LLM)
    
    with open(log_file_path, "r", encoding="utf-8") as f:
        logs = f.read()
    with open(bugged_html_path, "r", encoding='utf-8') as f:
        # find codes between
        # <script id='march' type='shader'>#version 300 es
        # </script>
        html_content = f.read()
        pattern = r"<script id='march' type='shader'>(.*?)</script>"
        match = re.search(pattern, html_content, re.DOTALL)
        march_shader_code = match.group(1).strip()
    
    if logs.startswith("nRMSE:"):
        context = f"Current {logs}. The output is numerically inaccurate compared to the ground truth."
    else:
        context = f"Execution Logs: {logs}"
        
    with open(f"./result/{LLM}/{pde_name}/parsed_resp.json", "r", encoding="utf-8") as f:
        parsed_resp = json.load(f)      
        
    debug_prompt_text = debug_prompt.format(
        shader_codes = march_shader_code,
        context_info = context,
        PDEs = parsed_resp["PDEs"],
        bc= parsed_resp["boundary_conditions"]
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
    os.makedirs(os.path.dirname(debugged_html_path), exist_ok=True)
    with open(f"./result/{LLM}/{pde_name}/skeleton.html", 'r', encoding='utf-8') as f:
        html_content = f.read()
    updated_html = html_content.replace('{{MARCH_SHADER_CODE}}', response_text)
    
    
    with open(debugged_html_path, 'w', encoding='utf-8') as f:
        f.write(updated_html)
        
    
def main():    
    parser = argparse.ArgumentParser()
    
    parser.add_argument("--LLM", help="The name of LLM")
    parser.add_argument(
            "--pde", 
            choices=["advection_beta0.1","advection_beta1.0", "burgers_nu0.001","burgers_nu1.0","twoD_reaction_diffusion","oneD_reaction_diffusion_Nu0.5_Rho1.0","fenton_karma","TNNP"], 
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
    
    parser.add_argument(
        "--scale_times",
        default=5,
        type=int,
        help = "scaling times to repeat"
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
        
        # delete original parsed_response:
        os.remove(f"./result/{LLM_sanitized}/{args.pde}/parsed_resp.json") if os.path.exists(f"./result/{LLM_sanitized}/{args.pde}/parsed_resp.json") else None
        
        while not check_parsed_response(args.LLM,args.pde):
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
            with open(f"./result/{LLM_sanitized}/{args.pde}/{debugged_times_used}_debug_times/IC_{index}/normalized_rmse.txt", "w", encoding="utf-8") as f:
                f.write(str(normalized_rmse))
            
            while normalized_rmse > 0.1 and debugged_times_used < args.debug_trail_times:
                debugged_times_used += 1
                bugged_file_path = debugged_file_path
                debugged_file_path = f"./result/{LLM_sanitized}/{args.pde}/{debugged_times_used}_debug_times/IC_{index}/simulation.html"
                debug_agent(args.LLM,args.pde,log_file_path,bugged_file_path,debugged_file_path)
                
                # Update download_folder and log_file_path for the new verification
                download_folder = f"./result/{LLM_sanitized}/{args.pde}/{debugged_times_used}_debug_times/IC_{index}"
                new_log_file_path = f"{download_folder}/log.txt"
                normalized_rmse = verify_agent(args.LLM,args.pde,debugged_file_path,IC_file,download_folder,new_log_file_path,solution_file)
                log_file_path = new_log_file_path  # Update for next debug iteration if needed
                simulation_file_path = debugged_file_path  # Update simulation file path for next verification
            nrmse_list.append(normalized_rmse)
        print(debugged_times_used, nrmse_list)
        
if __name__ == "__main__":
    main()
    