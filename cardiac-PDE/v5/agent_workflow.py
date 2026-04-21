import pde_descriptions,system_prompt
from parse_agent import parse_prompt
from code_agent import code_prompt
from debug_agent import debug_prompt
from refine_agent import refine_prompt
import json
import ollama
from verify_script.verify_result import *
import os
from dotenv import load_dotenv
from openai import OpenAI
import anthropic
from google import genai
from google.genai import types # Required for Gemini config
import numpy as np
import argparse

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


def parsing(model : str,pde_name : str, paras = {'nu':0.1,'p':0.1}):
    pde_description = getattr(pde_descriptions, pde_name)
    pde_description = pde_description.format(**paras)
    system_prompt = system_prompt.system_prompt
    user_prompt = parse_prompt.format(
        user_input=pde_description,
    )
    response_text = chat_with(model, system_prompt, user_prompt)
    
    #deleat ```json at beginning of response.text if exist
    if response_text.startswith("```json"):
        response_text = response_text[len("```json"):]

    #deleat ``` at end of response.text if exist
    if response_text.endswith("```"):
        response_text = response_text[:-3]

    with open("./result/parsed_resp.json", "w", encoding="utf-8") as f:
        f.write(response_text)

def coding(model:str,pde_name:str):
    with open("./result/parsed_resp.json", "r") as f:
        parsed_resp = json.load(f)
    number_of_state_variables = parsed_resp["number_of_state_variables"]
    texture_size = parsed_resp["texture_size"]
    spatial_step = parsed_resp["spatial_step"]
    temporal_step = parsed_resp["temporal_step"]
    time_horizon = parsed_resp["time_horizon"]
    #initial_condition_file = '"C:\\Users\\xan37\\OneDrive - Georgia Institute of Technology\\Documents\\GitHub\\cardiac-agent\\baselines models\\fk_data\\tau_d_0.5714\\IC.csv"'
    parameter_values = parsed_resp["parameter_values"]
    parameter_values
    parameter_str = "\n".join([
        f"    const float {k:} = {v};" 
        for k, v in parameter_values.items()
    ])

    coding_skeleton_file = f"./skeleton_script/{parsed_resp['number_of_state_variables']}V/skeleton.html"
    # Load the file
    with open(coding_skeleton_file, 'r') as f:
        html_template = f.read()

    # Replace placeholders with your Python variables
    updated_html = html_template.replace('{{DT_VALUE}}', str(temporal_step)).replace('{{DX_VALUE}}', str(spatial_step))
    updated_html = updated_html.replace('{{TEXTURE_VALUE}}', str(texture_size))
    # Optional: Save it back to a new file
    with open('./result/skeleton.html', 'w') as f:
        f.write(updated_html)
        
    with open(f"./skeleton_script/{parsed_resp['number_of_state_variables']}V/march_skeleton.frag", 'r') as f:
        coding_skeleton = f.read()
    updated_coding_skeleton = coding_skeleton.replace('{{PARAMETER_VALUES}}', parameter_str)
    user_prompt = code_prompt.format(
        PDEs=parsed_resp["PDEs"],
        coding_skeleton = updated_coding_skeleton
    )
    
    response_text = chat_with(model, system_prompt, user_prompt)
    
    #deleat ```glsl at beginning of response.text if exist
    if response_text.startswith("```glsl"):
        response_text = response_text[len("```glsl"):]

    # #deleat ``` at end of response.text if exist
    if response_text.endswith("```"):
        response_text = response_text[:-3]  

    with open("./result/march_shader.frag", "w", encoding="utf-8") as f:
        f.write(response_text)
        
    # replace march shader script in skeleton.html with the generated march shader code
    with open('./result/skeleton.html', 'r') as f:
        html_content = f.read()
    with open('./result/march_shader.frag', 'r') as f:    march_shader_code = f.read()
    updated_html = html_content.replace('{{MARCH_SHADER_CODE}}', march_shader_code)
    # save to new html
    if not os.path.exists(f"./result/{model}/{pde_name}"):
        os.makedirs(f"./result/{model}/{pde_name}")
    with open(f'./result/{model}/{pde_name}/simulation.html', 'w') as f:
        f.write(updated_html)
        
def verifying(model:str,pde_name:str,IC_file_relative:str,simulation_file:str,T_end:float,log_file:str,reference_data):
    # create download folder if not exist
    download_folder = f"simulation_downloads/{model}/{pde_name}/{IC_file_relative}"
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)
        
    logs = verify_result(simulation_file,IC_file_relative,T_end,download_folder)

    if logs != "Success":
        with open(f"./result/{model}/{pde_name}/{IC_file_relative}/{log_file}.txt", "w", encoding="utf-8") as f:
            for entry in logs:
                # Format: [LEVEL] Timestamp - Message
                line = f"[{entry['level']}] {entry['timestamp']} - {entry['message']}\n"
                f.write(line)
        return 1e10
    else:
        with open(f"./result/{model}/{pde_name}/{IC_file_relative}/{log_file}.txt", "w", encoding="utf-8") as f:
            f.write("No bugs")

        result = os.path.join(download_folder, "result.csv")
        
        # now calculate normalized rmse between result and reference_solution_file
        result_data = np.loadtxt(result, delimiter=',')
        # skip first two data points
        result_data = result_data[2:]
        # the remaining data is r,g,b,a,r,g,b,a,..., and we only need r channel
        result_data = result_data[::4]
        
        rmse = np.sqrt(np.mean((result_data - reference_data) ** 2))
        norm = np.sqrt(np.mean(reference_data ** 2))
        normalized_rmse = rmse / norm
        return normalized_rmse

def debugging(model:str,pde_name:str,IC_file_relative:str,log_file:str):
    with open(f"./result/{model}/{pde_name}/{IC_file_relative}/{log_file}.txt", "r", encoding="utf-8") as f:
        logs = f.read()
    with open("./result/march_shader.frag", "r", encoding="utf-8") as f:
        shader_codes = f.read()
    debug_prompt = debug_prompt.format(
        shader_codes = shader_codes,
        log_info = logs
    )
    
    reponse_text = chat_with(model, system_prompt, debug_prompt)
    if response_text.startswith("```glsl"):
        response_text = response_text[len("```glsl"):]
    # deleat #version 300 es at beginning of response.text if exist
    if response_text.startswith("#version 300 es"):
        response_text = response_text[len("#version 300 es"):].lstrip()  # also remove leading whitespace

    # #deleat ``` at end of response.text if exist
    if response_text.endswith("```"):
        response_text = response_text[:-3]
    
    # save to html
    with open('./result/skeleton.html', 'r') as f:
        html_content = f.read()
    updated_html = html_content.replace('{{MARCH_SHADER_CODE}}', response_text)
    # save to new html
    if not os.path.exists(f"./result/{model}/{pde_name}"):
        os.makedirs(f"./result/{model}/{pde_name}")
    with open(f'./result/{model}/{pde_name}/simulation.html', 'w') as f:
        f.write(updated_html)

def refining(model:str,pde_name:str,IC_file_relative:str,simulation_file:str,T_end:float,log_file:str,reference_data,nrmse):
    with open(simulation_file, 'r') as f:
        simulation_codes = f.read()
    refine_prompt = refine_prompt.format(
        nrmse = nrmse,
        simulation_codes = simulation_codes
    )
    reponse_text = chat_with(model, system_prompt, refine_prompt)
    if reponse_text.startswith("```html"):
        reponse_text = reponse_text[len("```html"):]
    # #deleat ``` at end of response.text if exist
    if response_text.endswith("```"):
        response_text = response_text[:-3]
    
    # save to new html
    if not os.path.exists(f"./result/{model}/{pde_name}"):
        os.makedirs(f"./result/{model}/{pde_name}")
    with open(f'./result/{model}/{pde_name}/simulation(refined).html', 'w') as f:
        f.write(response_text)
    
    nrmse_refined = verifying(model,pde_name,IC_file_relative,f'./result/{model}/{pde_name}/simulation(refined).html',T_end,log_file,reference_data)
    
    if nrmse_refined < nrmse:
        # replace original html file
        with open(f'./result/{model}/{pde_name}/simulation.html', 'w') as f:
            f.write(response_text)
    else:
        print(f"Refined simulation has higher nRMSE ({nrmse_refined}) than original simulation ({nrmse}). Keeping original simulation.")
    
    return nrmse_refined

def main(model,pde_name,IC_file_relative,simulation_file,T_end,log_file,reference_data):
    debug_trails_left = 5
    refine_trails_left = 5
    parsing(model,pde_name)
    coding(model,pde_name)
    nrmse = verifying(model,pde_name,IC_file_relative,simulation_file,T_end,log_file,reference_data)
    while nrmse > 1 and debug_trails_left > 0:
        debugging(model,pde_name,IC_file_relative,log_file)
        debug_trails_left -= 1
        nrmse = verifying(model,pde_name,IC_file_relative,simulation_file,T_end,log_file,reference_data)
    
    if debug_trails_left == 0 and nrmse > 1:
        print(f"Debugging failed after 5 trails. Final nRMSE: {nrmse}")
        return nrmse,nrmse,debug_trails_left
    nrmse_before_refine = nrmse
    while refine_trails_left > 0:
        nrmse = refining(model,pde_name,IC_file_relative,simulation_file,T_end,log_file,reference_data,nrmse_before_refine)
        refine_trails_left -= 1
    
    return nrmse,nrmse_before_refine,debug_trails_left
    
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="Run the PDE LLM Agent Pipeline")
    parser.add_argument("--model", type=str, default="gpt-4", help="Model name (e.g., gpt-4, claude-3-opus, gemini-1.5-pro,qwen3:8b)")
    parser.add_argument("--pde", type=str, required=True, help="Name of the PDE in pde_descriptions.py")
    parser.add_argument("--ic_file", type=str, required=True, help="Relative path to the Initial Condition CSV file")
    parser.add_argument("--ref_file", type=str, required=True, help="Path to the reference solution .csv or .npy file")
    parser.add_argument("--t_end", type=float, default=10.0, help="End time for the simulation")
    parser.add_argument("--log_name", type=str, default="debug_log", help="Name for the output log file")

    args = parser.parse_args()
    main()