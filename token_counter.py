import tiktoken
from pathlib import Path

MODELS = {
    "gpt-4o": {"input_price": 5.00, "output_price": 15.00},
    "gpt-4o-2024-08-06": {"input_price": 2.50, "output_price": 10.00},
    "gpt-4o-2024-05-13": {"input_price": 5.00, "output_price": 15.00},
    "gpt-4o-mini": {"input_price": 0.150, "output_price": 0.600},
    "gpt-4o-mini-2024-07-18": {"input_price": 0.150, "output_price": 0.600},
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
            file_contents[file_path] = content

    return total_tokens, file_contents

def calculate_cost(total_tokens, model):
    if model not in MODELS:
        raise ValueError(f"Unknown model: {model}")

    # We're only calculating input cost here as we don't know the output tokens yet
    input_price = MODELS[model]["input_price"]
    return (total_tokens / 1_000_000) * input_price