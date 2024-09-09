import json
from pathlib import Path
from .openai_client import OpenAIClient
from .token_counter import MODELS, split_contents
import time

def query_llm(query: str, file_contents: dict, model: str, client: OpenAIClient):
    max_tokens = MODELS[model]["max_tokens"]
    batches = split_contents(file_contents, max_tokens)

    all_relevance_scores = {}
    all_thoughts = []
    total_llm_time = 0

    for i, batch in enumerate(batches, 1):
        batch_contents = {str(path): content for path, content in batch.items()}

        rendered = ""
        for path_string, content in batch_contents.items():
            rendered += f"-- File: {path_string} --\n\n{content}\n\n"

        prompt = f"""
        Given the following query: "{query}"

        Please analyze the relevance of each file to this query. Consider both direct and indirect relevance.
        For indirect relevance, consider whether a file is necessary to understand how another relevant file works.

        Then, provide a map from each file path to an integer from 0 to 100 representing its relevance to the query.
        100 is most relevant, 0 is not at all relevant.
        Start from listing files that appear to be the MOST relevant, and then make your way to those that are
        the least relevant. If a file has zero relevance, do not include it in the final output, in order
        to save space.

        Produce your output in this format:
        {{
            "relevance_scores": {{
                "<filename>": <integer score from 0 to 100>,
                ...(for all non-zero relevance files)
            }}
        }}

        Here are the files and their contents (paths are relative to the repository root):

        {rendered}
        """

        # Before providing the final output, please explicitly think through your thoughts on which files are most relevant and why.

        response_format = {
            #"thoughts": str,
            "relevance_scores": {

            }
        }

        start_time = time.time()
        response = client.chat(prompt, response_format, model=model)
        end_time = time.time()
        llm_time = end_time - start_time
        total_llm_time += llm_time

        print(f"LLM call {i} took {llm_time:.2f} seconds")
        print(response)

        #import pdb
        #pdb.set_trace()

        # For some reason, the response is either:
        # { "type": "object", "properties": { "relevance_scores": { "<filename>": <relevance_score>, ... } } }
        # OR
        # { "relevance_scores": { "<filename>": <relevance_score>, ... } }

        #all_thoughts.append(response['thoughts'])

        if 'properties' in response:
            all_relevance_scores.update(response['properties']['relevance_scores'])
        else:
            all_relevance_scores.update(response['relevance_scores'])



    print(f"Total LLM processing time: {total_llm_time:.2f} seconds")

    return {
        #"thoughts": "\n\n".join(all_thoughts),
        "relevance_scores": all_relevance_scores
    }
