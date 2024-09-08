import argparse
import os
import sys
from pathlib import Path
import pyperclip
import tiktoken

from .file_filter import filter_code_files, parse_gitignore, is_ignored_by_gitignore, find_repo_root
from .token_counter import count_tokens, calculate_cost, MODELS, format_tokens, analyze_tokens
from .llm_query import query_llm
from .output_processor import process_output
from .openai_client import OpenAIClient

def get_user_confirmation(total_tokens, cost, num_files, model, large_files, large_dirs):
    print(f"\nPreparing to send {format_tokens(total_tokens)} tokens from {num_files} files to the LLM.")
    print(f"Estimated cost: ${cost:.4f}")
    print(f"Selected model: {model}")

    if large_files:
        print("\nLarge files (>30,000 tokens):")
        for file_path, tokens in large_files:
            print(f"  {file_path}: {format_tokens(tokens)} tokens")

    if large_dirs:
        print("\nLarge directories (>100,000 tokens):")
        for dir_path, tokens in large_dirs:
            print(f"  {dir_path}: {format_tokens(tokens)} tokens")

    while True:
        response = input("Do you want to proceed? (y/n): ").lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print("Please enter 'y' for yes or 'n' for no.")

def count_clipboard_tokens(text):
    encoder = tiktoken.encoding_for_model("gpt-4-0125-preview")
    return len(encoder.encode(text))

def main():
    parser = argparse.ArgumentParser(description="Gather and analyze repository files based on relevance to a query.")
    parser.add_argument("query", nargs='?', default=None, help="Natural language query to filter files")
    parser.add_argument("--include-test", action="store_true", help="Include test files")
    parser.add_argument("--include-config", action="store_true", help="Include configuration files")
    parser.add_argument("--include-ecosystem", action="store_true", help="Include ecosystem-specific files and directories")
    parser.add_argument("--include-gitignored", action="store_true", help="Include files that are gitignored")
    parser.add_argument("--exclude", action="append", default=[], help="Exclude files containing the specified path fragment")
    parser.add_argument("--relevance-threshold", type=int, default=50, help="Relevance threshold (0-100)")
    parser.add_argument("--model", default="gpt-4o-mini-2024-07-18", choices=MODELS.keys(), help="LLM model to use")
    parser.add_argument("--openai-key", help="OpenAI API key")
    parser.add_argument("--all", action="store_true", help="Return all files without using LLM")
    args = parser.parse_args()

    # Get the repository root directory
    try:
        repo_root = find_repo_root(Path.cwd())
    except ValueError:
        print("Error: Not a git repository (or any of the parent directories)")
        sys.exit(1)

    # Filter code files
    code_files = list(filter_code_files(repo_root,
                                            include_test=args.include_test,
                                            include_config=args.include_config,
                                            include_ecosystem=args.include_ecosystem,
                                            exclude_patterns=args.exclude,
                                            include_gitignored=args.include_gitignored))

    # If --include-gitignored is not set, filter out gitignored files
    #if not args.include_gitignored:
    #    gitignore_patterns = parse_gitignore(repo_root)
    #    code_files = [f for f in code_files if not is_ignored_by_gitignore(f, gitignore_patterns)]

    if args.all:
        output_string = ""
        for file_path in code_files:
            full_path = repo_root / file_path
            output_string += f"\n\n--- {file_path} ---\n"
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    output_string += f.read()
            except Exception as e:
                output_string += f"Error reading file: {e}\n"

        print("\nAll Files:")
        print(output_string)

        try:
            pyperclip.copy(output_string)
            clipboard_tokens = count_clipboard_tokens(output_string)
            print(f"\nFile contents copied to clipboard. Total tokens: {format_tokens(clipboard_tokens)}")
        except pyperclip.PyperclipException:
            print("\nUnable to copy to clipboard. Please copy the output manually.")

        return

    if not args.query:
        print("Error: You must provide a query when not using the --all option.")
        sys.exit(1)

    # Count tokens and calculate cost
    total_tokens, file_contents, file_tokens, dir_tokens = count_tokens(repo_root, code_files)
    cost = calculate_cost(total_tokens, args.model)

    # Analyze token distribution
    large_files, large_dirs = analyze_tokens(file_tokens, dir_tokens)

    # Get user confirmation
    if not get_user_confirmation(total_tokens, cost, len(code_files), args.model, large_files, large_dirs):
        print("Operation cancelled by user.")
        sys.exit(0)

    # Initialize OpenAIClient
    client = OpenAIClient(api_key=args.openai_key)

    # Query LLM
    response = query_llm(args.query, file_contents, args.model, client)

    # Process output
    relevant_files, output_string = process_output(response, args.relevance_threshold, repo_root)

    # Copy relevant file paths and contents to clipboard
    try:
        pyperclip.copy(output_string)
        clipboard_tokens = count_clipboard_tokens(output_string)
        print(f"\nRelevant file paths and contents copied to clipboard. Total tokens: {format_tokens(clipboard_tokens)}")
    except pyperclip.PyperclipException:
        print("\nUnable to copy to clipboard. Please copy the output manually.")

    # Print summary of relevant files
    print("\nSummary of relevant files:")
    for file in relevant_files:
        print(file)

if __name__ == "__main__":
    main()