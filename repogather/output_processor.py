import json
from pathlib import Path

def process_output(response, relevance_threshold, root_dir):
    print("\nRelevance Scores:")

    relevant_files = []
    output_string = ""

    relevance_scores = response['relevance_scores']
    if isinstance(relevance_scores, str):
        relevance_scores = json.loads(relevance_scores)

    for file_path, score in relevance_scores.items():
        print(f"{file_path}: {score}")
        if score >= relevance_threshold:
            relevant_files.append(file_path)

    print("\nRelevant Files and Contents:")
    for file_path in relevant_files:
        full_path = root_dir / file_path
        print(f"\n--- {file_path} ---")
        output_string += f"\n\n--- {file_path} ---\n"
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print(content)
                output_string += content
        except Exception as e:
            error_message = f"Error reading file: {e}"
            print(error_message)
            output_string += error_message

    return relevant_files, output_string.strip()