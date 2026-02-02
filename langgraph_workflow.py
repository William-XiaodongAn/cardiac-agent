import json
import os
import re
from typing import TypedDict, Annotated

from langgraph.graph import StateGraph, END

# --- LangChain and Pydantic Imports for the LLM-Powered Agent ---
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field

# --- LLM-Powered ParameterAgent ---

# 1. Define the desired output structure with Pydantic
class FKModelParameters(BaseModel):
    """Data model for FitzHugh-Nagumo simulation parameters."""
    epsilon: float = Field(description="The epsilon parameter of the FK model.", default=0.01)
    beta: float = Field(description="The beta parameter of the FK model.", default=0.5)
    gamma: float = Field(description="The gamma parameter of the FK model.", default=1.0)
    pacing_frequency: float = Field(description="The pacing frequency in Hz.", default=1.0)
    pacing_duration: int = Field(description="The total simulation duration in ms.", default=1000)
    pacing_amplitude: float = Field(description="The amplitude of the pacing stimulus.", default=1.0)

class ParameterAgent:
    """
    An LLM-powered agent to extract FitzHugh-Nagumo (FK) model
    parameters from a raw text input using langchain.
    """
    def __init__(self):
        """
        Initializes the ParameterAgent with an LLM and a prompt template.
        """
        # NOTE: Ensure the OPENAI_API_KEY environment variable is set.
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set. The ParameterAgent cannot function.")
            
        # Create a ChatOpenAI model instance with structured output capabilities
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=api_key).with_structured_output(FKModelParameters)
        
        self.prompt_template = PromptTemplate(
            input_variables=["raw_input"],
            template="""
You are an expert assistant specializing in cardiac electrophysiology simulations.
Your task is to extract the parameters for a FitzHugh-Nagumo (FK) model simulation based on a user's request.

Carefully analyze the user's request below. Identify any specified values for the following parameters:
- epsilon
- beta
- gamma
- pacing_frequency (in Hz)
- pacing_duration (in ms)
- pacing_amplitude

If a parameter is not mentioned in the request, use its default value.
Pay close attention to units. If the user says "run for 2 seconds", the duration is 2000 ms. If they mention "fast pacing", a frequency of 2.0 Hz is appropriate.

User Request: "{raw_input}"

Extract the parameters and provide them in the required format.
"""
        )
        self.chain = self.prompt_template | self.llm
        print("LLM-Powered ParameterAgent initialized.")

    def extract_parameters(self, raw_input: str) -> dict:
        """
        Uses an LLM to extract FK simulation parameters from the user's request.
        """
        print(f"ParameterAgent processing raw input with LLM: '{raw_input}'")
        
        # Invoke the LLM chain
        try:
            extracted_params_model = self.chain.invoke({"raw_input": raw_input})
            # Convert the Pydantic model to a dictionary
            params = extracted_params_model.dict()
            print(f"ParameterAgent extracted parameters: {params}")
            return params
        except Exception as e:
            print(f"An error occurred during LLM-based parameter extraction: {e}")
            # Fallback to default parameters in case of an error
            return FKModelParameters().dict()


# --- 1. Define the State ---
class SimulationState(TypedDict):
    raw_input: str
    parameters: dict
    simulation_output_path: str
    error: str

# --- 2. Define the Agent Nodes ---
def run_parameter_agent_node(state: SimulationState) -> SimulationState:
    print("--- Running Parameter Agent Node ---")
    raw_input = state["raw_input"]
    
    try:
        parameter_agent = ParameterAgent()
        params = parameter_agent.extract_parameters(raw_input)
        
        parameters_file_path = "cardiac-agent/parameters.json"
        with open(parameters_file_path, "w") as f:
            json.dump(params, f, indent=4)
        print(f"Saved parameters to {parameters_file_path}")
        
        return {"parameters": params, "error": ""}
    except ValueError as e:
        print(f"ERROR: {e}")
        return {"parameters": {}, "error": str(e)}

def run_simulation_agent_node(state: SimulationState) -> SimulationState:
    print("\n--- Running Simulation Agent Node ---")
    if state.get("error"):
        print(f"Skipping simulation due to error in previous step: {state['error']}")
        return {}
        
    params = state["parameters"]
    print(f"Running simulation with parameters: {params}")
    output_path = "cardiac-agent/simulation_output.html"
    
    with open(output_path, "w") as f:
        f.write("<html><body><h1>Cardiac Simulation Result</h1>")
        f.write(f"<p>Based on parameters:</p>")
        f.write(f"<pre>{json.dumps(params, indent=4)}</pre>")
        f.write("</body></html>")
        
    print(f"Simulation complete. Output saved to: {output_path}")
    return {"simulation_output_path": output_path}

# --- 3. Define the Graph ---
workflow = StateGraph(SimulationState)

workflow.add_node("parameter_extraction", run_parameter_agent_node)
workflow.add_node("simulation_execution", run_simulation_agent_node)

workflow.set_entry_point("parameter_extraction")
workflow.add_edge("parameter_extraction", "simulation_execution")
workflow.add_edge("simulation_execution", END)

app = workflow.compile()

# --- 4. Run the Workflow ---
if __name__ == "__main__":
    initial_state = {
        "raw_input": "Run a fast-paced simulation for 500 ms with an epsilon of 0.02.",
        "parameters": {},
        "simulation_output_path": "",
        "error": ""
    }
    
    print("Starting cardiac simulation workflow...")
    # The `stream` method allows us to see the output of each step.
    for output in app.stream(initial_state):
        for key, value in output.items():
            print(f"Finished node: {key}")
            print(f"Updated state: {value}\n")
            
    print("Workflow finished!")