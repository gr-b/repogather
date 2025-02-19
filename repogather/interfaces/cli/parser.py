import argparse
from typing import Optional
from pathlib import Path

def create_parser() -> argparse.ArgumentParser:
    """Create the command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Gather and analyze repository files."
    )
    
    # Common arguments
    parser.add_argument(
        "--path",
        type=Path,
        default=Path.cwd(),
        help="Repository root path (default: current directory)"
    )
    
    parser.add_argument(
        "--include-tests",
        action="store_true",
        help="Include test files"
    )
    
    parser.add_argument(
        "--include-config",
        action="store_true",
        help="Include configuration files"
    )
    
    parser.add_argument(
        "--include-ecosystem",
        action="store_true",
        help="Include ecosystem files (package.json, requirements.txt, etc.)"
    )
    
    parser.add_argument(
        "--include-gitignored",
        action="store_true",
        help="Include files that are git ignored"
    )
    
    parser.add_argument(
        "--exclude",
        nargs="*",
        default=[],
        help="Glob patterns to exclude"
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest="command")
    
    # Analyze command
    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Analyze files using LLM"
    )
    
    analyze_parser.add_argument(
        "query",
        help="Natural language query to filter files"
    )
    
    analyze_parser.add_argument(
        "--model",
        default="gpt-4-turbo-preview",
        help="LLM model to use"
    )
    
    analyze_parser.add_argument(
        "--relevance-threshold",
        type=float,
        default=0.5,
        help="Minimum relevance score (0-1) for files"
    )
    
    return parser 