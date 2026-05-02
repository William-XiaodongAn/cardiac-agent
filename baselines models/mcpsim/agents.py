"""
MCP-SIM agents: Input Clarifier, Parser, Code Builder, Error Diagnosis, Input Rewriter.

Each agent wraps a single LLM call with a specialized prompt template.
The Simulation Executor is handled directly in the orchestrator via executor.py.
"""
import json
import re
import time

import llm_client
import prompts
import executor


class InputClarifierAgent:
    def __init__(self, model: str):
        self.model = model

    def clarify(self, raw_input: str) -> str:
        prompt = prompts.INPUT_CLARIFIER_PROMPT.format(raw_input=raw_input)
        response = llm_client.chat(
            self.model,
            prompts.INPUT_CLARIFIER_SYSTEM,
            prompt,
            temperature=0.2,
        )
        return _strip_think_tags(response).strip()


class ParsingAgent:
    def __init__(self, model: str):
        self.model = model

    def parse(self, clarified_text: str) -> dict:
        prompt = prompts.PARSING_PROMPT.format(clarified_text=clarified_text)
        response = llm_client.chat(
            self.model,
            prompts.PARSING_SYSTEM,
            prompt,
            temperature=0.0,
        )
        cleaned = _strip_think_tags(response).strip()
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if match:
                return json.loads(match.group())
            return {"raw_response": cleaned, "parse_error": True}


class CodeBuilderAgent:
    def __init__(self, model: str):
        self.model = model

    def build_code(self, clarified_text: str, parsed_json: dict) -> str:
        prompt = prompts.CODE_BUILDER_PROMPT.format(
            clarified_text=clarified_text,
            parsed_json=json.dumps(parsed_json, indent=2),
        )
        response = llm_client.chat(
            self.model,
            prompts.CODE_BUILDER_SYSTEM,
            prompt,
            temperature=0.0,
        )
        return executor.extract_code(response)


class ErrorDiagnosisAgent:
    def __init__(self, model: str):
        self.model = model

    def diagnose_execution_error(
        self,
        error_message: str,
        simulation_output: str,
        code: str,
        error_history: str,
        iteration: int,
    ) -> dict:
        prompt = prompts.ERROR_DIAGNOSIS_PROMPT.format(
            error_message=error_message[:3000],
            simulation_output=simulation_output[:2000],
            code=code,
            error_history=error_history[:2000],
            iteration=iteration,
        )
        response = llm_client.chat(
            self.model,
            prompts.ERROR_DIAGNOSIS_SYSTEM,
            prompt,
            temperature=0.0,
        )
        return self._parse_diagnosis(response)

    def diagnose_numerical_error(
        self,
        nrmse: float,
        simulation_output: str,
        code: str,
        parsed_json: dict,
        error_history: str,
        iteration: int,
    ) -> dict:
        prompt = prompts.NUMERICAL_DIAGNOSIS_PROMPT.format(
            nrmse=nrmse,
            simulation_output=simulation_output[:2000],
            code=code,
            parsed_json=json.dumps(parsed_json, indent=2),
            error_history=error_history[:2000],
            iteration=iteration,
        )
        response = llm_client.chat(
            self.model,
            prompts.ERROR_DIAGNOSIS_SYSTEM,
            prompt,
            temperature=0.0,
        )
        return self._parse_diagnosis(response)

    def _parse_diagnosis(self, response: str) -> dict:
        cleaned = _strip_think_tags(response).strip()
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        try:
            result = json.loads(cleaned)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if match:
                try:
                    result = json.loads(match.group())
                except json.JSONDecodeError:
                    result = {
                        "fix_type": "code",
                        "hint": "Failed to parse diagnosis response",
                        "confidence": 0.0,
                        "after_code": "",
                    }
            else:
                result = {
                    "fix_type": "code",
                    "hint": "Failed to parse diagnosis response",
                    "confidence": 0.0,
                    "after_code": "",
                }

        if "after_code" in result and result["after_code"]:
            result["after_code"] = executor.extract_code(result["after_code"])

        return result


class InputRewriterAgent:
    def __init__(self, model: str):
        self.model = model

    def rewrite(self, original_input: str, hint: str) -> str:
        prompt = prompts.INPUT_REWRITER_PROMPT.format(
            original_input=original_input,
            hint=hint,
        )
        response = llm_client.chat(
            self.model,
            prompts.INPUT_REWRITER_SYSTEM,
            prompt,
            temperature=0.2,
        )
        return _strip_think_tags(response).strip()


def _strip_think_tags(text: str) -> str:
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
