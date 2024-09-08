import json
from pathlib import Path
from .openai_client import OpenAIClient

def query_llm(query: str, file_contents: dict, model: str, client: OpenAIClient):
    # Convert file paths to strings
    file_contents = {str(path): content for path, content in file_contents.items()}

    prompt = f"""
    Given the following query: "{query}"

    Please analyze the relevance of each file to this query. Consider both direct and indirect relevance.
    For indirect relevance, consider whether a file is necessary to understand how another relevant file works.

    Here are the files and their contents (paths are relative to the repository root):

    {json.dumps(file_contents, indent=2)}

    Before providing the final output, please explicitly think through your thoughts on which files are most relevant and why.

    Then, provide a map from each file path to an integer from 0 to 100 representing its relevance to the query.
    100 is most relevant, 0 is not at all relevant.
    """

    response_format = {
        "thoughts": str,
        "relevance_scores": {

        }
    }

    return client.chat(prompt, response_format, model=model)