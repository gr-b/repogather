import json

def process_output(response, relevance_threshold):
    #print("LLM Thoughts:")
    #print(response['thoughts'])
    print("\nRelevance Scores:")

    relevant_files = []

    relevance_scores = response['relevance_scores']
    if type(relevance_scores) == str:
        relevance_scores = json.loads(relevance_scores)

    for file_path, score in relevance_scores.items():
        print(f"{file_path}: {score}")
        if score >= relevance_threshold:
            relevant_files.append(file_path)

    return relevant_files