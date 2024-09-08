
import json
from pathlib import Path
from .openai_client import OpenAIClient
from .token_counter import MODELS, split_contents

def query_llm(query: str, file_contents: dict, model: str, client: OpenAIClient):
    max_tokens = MODELS[model]["max_tokens"]
    batches = split_contents(file_contents, max_tokens)
    
    all_relevance_scores = {}
    all_thoughts = []

    for batch in batches:
        batch_contents = {str(path): content for path, content in batch.items()}

        prompt = f"""
        Given the following query: "{query}"

        Please analyze the relevance of each file to this query. Consider both direct and indirect relevance.
        For indirect relevance, consider whether a file is necessary to understand how another relevant file works.

        Here are the files and their contents (paths are relative to the repository root):

        {json.dumps(batch_contents, indent=2)}

        Before providing the final output, please explicitly think through your thoughts on which files are most relevant and why.

        Then, provide a map from each file path to an integer from 0 to 100 representing its relevance to the query.
        100 is most relevant, 0 is not at all relevant.
        """

        response_format = {
            "thoughts": str,
            "relevance_scores": {
                "type": "object",
                "additionalProperties": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 100
                }
            }
        }

        response = client.chat(prompt, response_format, model=model)
        
        all_relevance_scores.update(response['relevance_scores'])
        all_thoughts.append(response['thoughts'])

    return {
        "thoughts": "\n\n".join(all_thoughts),
        "relevance_scores": all_relevance_scores
    }