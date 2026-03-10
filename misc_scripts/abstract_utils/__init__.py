from abc import ABC, abstractmethod
import os
import json
from typing import Dict, Optional, Tuple


class LLMUtil(ABC):

    def __init__(self, api_key_name: str = "LLM_API_KEY", type: str = "custom", custom_prompt: str = "", max_tokens: int = 1_000, max_retries: int = 2):
        self.api_key_name = api_key_name
        self.key_error_str = "key-error"
        self.relevancy_error_str = "relevancy-error"
        self._api_key = os.getenv(self.api_key_name)
        self._max_tokens = max_tokens
        self._max_retries = max_retries
        self._type = type
        self._full_search_system_prompt = custom_prompt


    def _validate_api_key(self) -> bool:
        if self._api_key is None:
            return False
        return True

    @abstractmethod
    def abstract_generation(self, input_json: str) -> Optional[Dict]:
        pass
