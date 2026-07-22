import openai
from openai.types.chat import ChatCompletionMessageParam
from flask import current_app
from time import sleep
from typing import Dict, List, Optional

from . import LLM
from ..db import cast_app


class OpenAILLM(LLM):

    def __init__(
        self,
        api_key_name: str = "LLM_API_KEY",
        type: str = "glycan",
        max_tokens: int = 1000,
        max_retries: int = 2
    ):
        super().__init__(api_key_name, type, max_tokens, max_retries)
        self.instance = openai.OpenAI( base_url="http://localhost:3000/api", api_key=self._api_key)
        # self.instance = openai.OpenAI( base_url="http://localhost:11434/v1", api_key=self._api_key)
        # self.instance = openai.OpenAI( base_url="http://localhost:1234/v1", api_key=self._api_key)
        super().__init__(api_key_name, type, max_tokens, max_retries)

    def advanced_search(self, query: str) -> Optional[Dict]:

        if not self._validate_api_key():
            return {"error": self.key_error_str}

        messages: List[ChatCompletionMessageParam] = [
            {"role": "system", "content": self._full_search_system_prompt},
            {"role": "user", "content": query},
        ]
        validated_response = None
        for i in range(self._max_retries):
            try:
                response = self.instance.chat.completions.create(
                    # model="gpt-4o-mini",
                    model="llama3.1:latest",
                    # model="meta-llama-3.1-8b-instruct",
                    messages=messages,
                    store=False, # Set to False to prevent storage
                    max_tokens=self._max_tokens,
                    timeout=500.0,
                    stream=False
                )

                response_text = response.choices[0].message.content
                if response_text is None:
                    sleep((i + 1) ** 2)
                    continue

                if response_text.strip().lower() == "none":
                    return {"error": self.relevancy_error_str}

                validated, validated_response, error_message = (
                    self.validate_advanced_search_response(llm_response=response_text)
                )
                if validated:
                    break

                feedback_message: ChatCompletionMessageParam = {
                    "role": "user",
                    "content": f"Your response could not be validated. Please correct the folowing issues and provide valid JSON: {error_message}",
                }
                messages.append(feedback_message)
                sleep(0.5)

            except Exception as e:
                sleep((i + 1) ** 2)

        return validated_response
