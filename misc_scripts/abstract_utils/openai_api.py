import openai
from openai.types.chat import ChatCompletionMessageParam
from time import sleep
from typing import Dict, List, Optional
from pprint import pformat
import json
from __init__ import LLMUtil

class OpenAILLMUtil(LLMUtil):

    def __init__(
        self,
        api_key_name: str = "LLM_API_KEY",
        type: str = "custom",
        custom_prompt: str = "",
        max_tokens: int = 1000,
        max_retries: int = 1
    ):
        super().__init__(api_key_name, type, custom_prompt, max_tokens, max_retries)
        self.instance = openai.OpenAI(api_key=self._api_key)
        super().__init__(api_key_name, type, custom_prompt, max_tokens, max_retries)
    
    def abstract_generation(self, input_json: str) -> Optional[Dict]:
        if not self._validate_api_key():
            return {"error": self.key_error_str}

        messages: List[ChatCompletionMessageParam] = [
            {"role": "system", "content": self._full_search_system_prompt},
            {"role": "user", "content": input_json},
        ]
        
        validated_response = None
        for i in range(self._max_retries):
            try:
                response = self.instance.chat.completions.create(
                    model="gpt-4o-mini",
                    # model="gpt-5.4",
                    messages=messages,
                    store=True, # Set to False to prevent storage
                    # max_completion_tokens=1000,
                    max_tokens=1000,
                )

                response_text = response.choices[0].message.content

                if response_text is None:
                    sleep((i + 1) ** 2)
                    continue

                if response_text.strip().lower() == "none":
                    return {"error": self.relevancy_error_str}               
                
                validated_response = response_text
                sleep(0.5)

            except Exception as e:
                sleep((i + 1) ** 2)
                
        return validated_response