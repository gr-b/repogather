#!/usr/bin/env python3

import argparse
import os
import sys
from pathlib import Path
import pyperclip
import tiktoken

from file_filter import filter_code_files
from token_counter import count_tokens, calculate_cost, MODELS
from llm_query import query_llm
from output_processor import process_output
from openai_client import OpenAIClient

def get_user_confirmation(total_tokens, cost, num_files, model):
    print(f"\nPreparing to send {total_tokens} tokens from {num_files} files to the LLM.")
    print(f"Estimated cost: ${cost:.4f}")
    print(f"Selected model: {model}")
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
    parser.add_argument("--relevance-threshold", type=int, default=50, help="Relevance threshold (0-100)")
    parser.add_argument("--model", default="gpt-4o-mini-2024-07-18", choices=MODELS.keys(), help="LLM model to use")
    parser.add_argument("--openai-key", help="OpenAI API key")
    parser.add_argument("--all", action="store_true", help="Return all files without using LLM")
    args = parser.parse_args()

    # Get the repository root directory
    repo_root = Path.cwd()

    # Filter code files
    code_files = list(filter_code_files(repo_root, include_test=args.include_test, include_config=args.include_config))

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
            print(f"\nFile contents copied to clipboard. Total tokens: {clipboard_tokens}")
        except pyperclip.PyperclipException:
            print("\nUnable to copy to clipboard. Please copy the output manually.")

        return

    if not args.query:
        print("Error: You must provide a query when not using the --all option.")
        sys.exit(1)

    # Count tokens and calculate cost
    total_tokens, file_contents = count_tokens(repo_root, code_files)
    cost = calculate_cost(total_tokens, args.model)

    # Get user confirmation
    if not get_user_confirmation(total_tokens, cost, len(code_files), args.model):
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
        print(f"\nRelevant file paths and contents copied to clipboard. Total tokens: {clipboard_tokens}")
    except pyperclip.PyperclipException:
        print("\nUnable to copy to clipboard. Please copy the output manually.")

    # Print summary of relevant files
    print("\nSummary of relevant files:")
    for file in relevant_files:
        print(file)

if __name__ == "__main__":
    main()