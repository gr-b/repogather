import tiktoken
from pathlib import Path
from collections import defaultdict

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
    file_tokens = {}
    dir_tokens = defaultdict(int)

    for file_path in file_paths:
        full_path = root_dir / file_path
        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            tokens = len(encoder.encode(content))
            total_tokens += tokens
            file_contents[file_path] = content
            file_tokens[file_path] = tokens

            # Update directory token counts
            current_dir = file_path.parent
            while current_dir != Path():
                dir_tokens[current_dir] += tokens
                current_dir = current_dir.parent

    return total_tokens, file_contents, file_tokens, dir_tokens

def calculate_cost(total_tokens, model):
    if model not in MODELS:
        raise ValueError(f"Unknown model: {model}")

    # We're only calculating input cost here as we don't know the output tokens yet
    input_price = MODELS[model]["input_price"]
    return (total_tokens / 1_000_000) * input_price

def format_tokens(tokens):
    return f"{tokens:,}"

def analyze_tokens(file_tokens, dir_tokens):
    large_files = []
    large_dirs = []

    for file_path, tokens in file_tokens.items():
        if tokens > 30000:
            large_files.append((file_path, tokens))

    for dir_path, tokens in dir_tokens.items():
        if tokens > 100000:
            large_dirs.append((dir_path, tokens))

    return large_files, large_dirs

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