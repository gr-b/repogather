# repogather

repogather is a command-line tool that copies all relevant files (with their relative paths) in a repository to the clipboard.
It is intended to be used in LLM code understanding or code generation workflows. It uses gpt-4o-mini (configurable)
to decide file relevance, but can also be used without an LLM to return all files, with non-AI filters (such
as excluding tests or config files).

## Features

- Filters and analyzes code files in a repository
- Excludes test and configuration files by default (with options to include them)
- Estimates token count and API usage cost before processing
- Uses OpenAI's GPT models to evaluate file relevance
- Supports various methods of providing the OpenAI API key
- Outputs a list of relevant files, ranked by relevance score

## Installation

Install repogather using pip:

```
pip install repogather
```

## Setup

Set up your OpenAI API key using one of the following methods:
- As an environment variable: `export OPENAI_API_KEY=your_api_key_here`
- In a `.env` file in your current working directory:
  ```
  OPENAI_API_KEY=your_api_key_here
  ```
- Provide it as a command-line argument when running the tool (see Usage section)

## Usage

After installation, you can run repogather from the command line:

```
repogather "Your query here" [OPTIONS]
```

### Options

- `--include-test`: Include test files in the analysis
- `--include-config`: Include configuration files in the analysis
- `--relevance-threshold THRESHOLD`: Set the relevance threshold (0-100, default: 50)
- `--model MODEL`: Specify the OpenAI model to use (default: gpt-4o-mini-2024-07-18)
- `--openai-key KEY`: Provide the OpenAI API key directly

### Example

```
repogather "Find files related to user authentication" --include-config --relevance-threshold 70 --model gpt-4o-2024-08-06
```

This command will:
1. Search for files related to user authentication
2. Include configuration files in the search
3. Only return files with a relevance score of 70 or higher
4. Use the GPT-4o model from August 2024 for analysis

## How It Works

repogather performs the following steps:

1. Scans the current directory and its subdirectories for code files
2. Filters out test and configuration files (unless included via options)
3. Counts the tokens in the filtered files and estimates the API usage cost
4. Sends the file contents and the query to the specified OpenAI model
5. Processes the model's response to rank files by relevance
6. Outputs the list of relevant files, filtered by the specified threshold


## Note

repogather requires an active OpenAI API key to function. It will prompt you to confirm the expected cost of the 
query (in input tokens) before progressing.