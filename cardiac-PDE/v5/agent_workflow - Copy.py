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


def parse_agent(LLM:str,pde_description:str,pde_paras:dict,IC_array:np.ndarray):
    pde_description = pde_description.format(**input_paras)
    system_prompt = system_prompt.system_prompt
    user_prompt = parse_prompt.format(
        user_input=pde_description,
    )
    response_text = chat_with(LLM, system_prompt, user_prompt)
    
    #deleat ```json at beginning of response.text if exist
    if response_text.startswith("```json"):
        response_text = response_text[len("```json"):]

    #deleat ``` at end of response.text if exist
    if response_text.endswith("```"):
        response_text = response_text[:-3]

    with open("./result/parsed_resp.json", "w", encoding="utf-8") as f:
        f.write(response_text)

def main(LLM:str,pde_description:str,pde_paras:dict,IC_array:np.ndarray):
    pde_description = getattr(pde_descriptions, pde_name)
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument("--LLM", help="The name of LLM")
    parser.add_argument(
            "--pde", 
            choices=["advection", "burgers","twoD_reaction_diffusion","fenton_karma"], 
            help="pde has to be one of advection, burgers, twoD_reaction_diffusion, or fenton_karma."
        )
    parser.add_argument(
            "--IC", 
            help="Initial condition array for the PDE."
        )
    
    args = parser.parse_args()

    LLM = args.LLM
    pde_description = getattr(pde_descriptions, args.pde)
    
    for _ in range(args.repeat):
        print(f"Hello, {args.name}!")