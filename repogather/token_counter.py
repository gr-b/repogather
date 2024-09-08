import tiktoken
from pathlib import Path

MODELS = {
    "gpt-4o": {"input_price": 5.00, "output_price": 15.00, "max_tokens": 128000},
    "gpt-4o-2024-08-06": {"input_price": 2.50, "output_price": 10.00, "max_tokens": 128000},
    "gpt-4o-2024-05-13": {"input_price": 5.00, "output_price": 15.00, "max_tokens": 128000},
    "gpt-4o-mini": {"input_price": 0.150, "output_price": 0.600, "max_tokens": 128000},
    "gpt-4o-mini-2024-07-18": {"input_price": 0.150, "output_price": 0.600, "max_tokens": 128000},
}

def count_tokens(root_dir: Path, file_paths):
    encoder = tiktoken.encoding_for_model("gpt-4-0125-preview")
    total_tokens = 0
    file_contents = {}

    for file_path in file_paths:
        full_path = root_dir / file_path
        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            tokens = len(encoder.encode(content))
            total_tokens += tokens
            file_contents[file_path] = (content, tokens)

    return total_tokens, file_contents

def calculate_cost(total_tokens, model):
    if model not in MODELS:
        raise ValueError(f"Unknown model: {model}")

    input_price = MODELS[model]["input_price"]
    return (total_tokens / 1_000_000) * input_price

def split_contents(file_contents, max_tokens):
    batches = []
    current_batch = {}
    current_tokens = 0

    for file_path, (content, tokens) in file_contents.items():
        if current_tokens + tokens > max_tokens:
            batches.append(current_batch)
            current_batch = {}
            current_tokens = 0

        current_batch[file_path] = content
        current_tokens += tokens

        if current_tokens >= max_tokens:
            batches.append(current_batch)
            current_batch = {}
            current_tokens = 0

    if current_batch:
        batches.append(current_batch)

    return batches