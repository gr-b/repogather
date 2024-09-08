import json
import os
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv

class OpenAIClient:
    OPENAI_API_URL = 'https://api.openai.com/v1/chat/completions'
    DEFAULT_TIMEOUT = 300  # 5 minutes

    def __init__(self, api_key: Optional[str] = None, timeout: int = DEFAULT_TIMEOUT):
        self.api_key = self._get_api_key(api_key)
        self.timeout = timeout

    def _get_api_key(self, provided_key: Optional[str] = None) -> str:
        if provided_key:
            return provided_key

        # Try to get the key from environment variables
        env_key = os.getenv('OPENAI_API_KEY')
        if env_key:
            return env_key

        # If not found in environment, try loading from .env file
        load_dotenv()
        env_key = os.getenv('OPENAI_API_KEY')
        if env_key:
            return env_key

        raise ValueError("API key must be provided either as an argument, environment variable, or in the .env file.")

    def chat(self, prompt: str, response_format: Dict[str, Any], model: str = 'gpt-4o-2024-08-06') -> Dict[str, Any]:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }

        schema = self._hash_to_json_schema(response_format)

        data = {
            'model': model,
            'messages': [{'role': 'user', 'content': prompt}],
            'response_format': {
                'type': 'json_schema',
                'json_schema': {
                    'name': 'sdfsdfsdf',
                    'schema': schema,
                }
            }
        }

        response = requests.post(self.OPENAI_API_URL, headers=headers, json=data, timeout=self.timeout)

        if not response.ok:
            print(response.text)
            response.raise_for_status()

        content = response.json()['choices'][0]['message']['content']

        print(json.loads(content)['thoughts'])

        return json.loads(content)

    def _hash_to_json_schema(self, hash: Dict[str, Any]) -> Dict[str, Any]:
        schema = {'type': 'object', 'properties': {}, 'required': []}

        for key, value in hash.items():
            schema['properties'][key] = self._value_to_schema(value)
            schema['required'].append(str(key))

        schema['additionalProperties'] = False
        return schema

    def _value_to_schema(self, value: Any) -> Dict[str, Any]:
        if isinstance(value, dict):
            return self._hash_to_json_schema(value)
        elif isinstance(value, list):
            return {
                'type': 'array',
                'items': {} if not value else self._value_to_schema(value[0])
            }
        elif isinstance(value, bool):
            return {'type': 'boolean'}
        elif isinstance(value, int):
            return {'type': 'integer'}
        elif isinstance(value, float):
            return {'type': 'number'}
        elif isinstance(value, str):
            return {'type': 'string'}
        elif value is None:
            return {'type': 'null'}
        elif isinstance(value, type):
            if value == int:
                return {'type': 'integer'}
            elif value == float:
                return {'type': 'number'}
            elif value == str:
                return {'type': 'string'}
            elif value == bool:
                return {'type': 'boolean'}
            else:
                return {'type': 'string'}  # Default to string for unknown types
        else:
            return {'type': 'string'}  # Default to string for unknown types