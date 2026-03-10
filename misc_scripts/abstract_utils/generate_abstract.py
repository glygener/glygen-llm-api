from typing import Tuple, Dict, Optional
from pprint import pformat
import json
import math
import os
from __init__ import LLMUtil
from openai_api import OpenAILLMUtil

class GenerateAbstract():

    def __init__(
        self,
        custom_prompt: str = "",
        type: str = "custom",
    ):
        LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
        self.llm_client: LLMUtil
        if LLM_PROVIDER == "openai":
            self.llm_client = OpenAILLMUtil(type=type, custom_prompt=custom_prompt)
        else:
            self.llm_client = OpenAILLMUtil(type=type, custom_prompt=custom_prompt)

    def generate_abstract(self, input_id: str, input_json: str) -> Tuple[Dict, int]:
        """Entry point for the AI-assisted search endpoint."""

        # Generate structured search parameters using OpenAI
        ai_abstract, search_params_http_code = self.ai_abstract_generation(input_json)
        if search_params_http_code != 200:
            return ai_abstract, search_params_http_code

        # ai_abstract_metadata = {
        #     "input_id": input_id,
        #     "input_json": input_json,
        #     "ai_abstract": ai_abstract
        # }

        return ai_abstract, search_params_http_code


    def ai_abstract_generation(self, input_json: str) -> Tuple[Dict, int]:
        """Parse a natural language query into structured search parameters using OpenAI."""

        try:
            ai_abstract = self.llm_client.abstract_generation(input_json)

            if ai_abstract is None:
                error_obj = {
                    "error_log":f"Unable to parse query using LLM provider",
                    "error_msg":"unable-to-parse-query-using-llm",
                    "origin":"ai_abstract_generation",
                }
                return error_obj, 400

            if "error" in ai_abstract:
                if ai_abstract["error"] == self.llm_client.key_error_str:
                    error_obj = {
                        "error_log":"Unable to find LLM API key",
                        "error_msg":"llm-key-error",
                        "origin":"ai_abstract_generation",
                    }
                    return error_obj, 401
                elif ai_abstract["error"] == self.llm_client.relevancy_error_str:
                    error_obj = {
                        "error_log":f"User made non-glycan",
                        "error_msg":"non-glycan-related-query",
                        "origin":"ai_abstract_generation",
                    }
                    return error_obj, 400

            return ai_abstract, 200

        except Exception as e:
            error_obj = {
                "error_log":f"Unable to parse query using LLM provider \nerror: {e}",
                "error_msg":"unable-to-parse-query-using-llm",
                "origin":"ai_abstract_generation",
            }
            return error_obj, 400
