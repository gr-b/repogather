from pathlib import Path
import re
import os
from typing import Iterator, List, Optional
import fnmatch

COMMON_IGNORE_PATTERNS = [
    r'^node_modules/',
    r'^venv/',
    r'^env/',
    r'^.venv/',
    r'^.env/',
    r'^__pycache__/',
    r'^.git/',
    r'^.svn/',
    r'^.hg/',
    r'^.idea/',
    r'^.vscode/',
    r'^build/',
    r'^dist/',
    r'^out/',
    r'^target/',
    r'^bin/',
    r'^obj/',
    r'^packages/',
    r'^vendor/',
    r'^bower_components/',
    r'^.bundle/',
    r'^.pytest_cache/',
    r'^.mypy_cache/',
    r'^.tox/',
    r'^.eggs/',
    r'^.gradle/',
    r'^.next/',
    r'^.nuxt/',
    r'^.output/',
    r'^.cache/',
    r'^.parcel-cache/',
    r'^.yarn/',
    r'\.min\.(js|css)$',
    r'\.bundle\.(js|css)$',
    r'\.map$',
    r'\.pyc$',
    r'\.class$',
    r'\.o$',
    r'\.obj$',
    r'\.dll$',
    r'\.exe$',
    r'\.so$',
    r'\.dylib$',
    r'\.log$',
    r'\.lock$',
    r'package-lock\.json$',
    r'yarn\.lock$',
]

CODE_EXTENSIONS = {
    '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.c', '.cpp', '.cs', '.go', '.rb', '.php',
    '.swift', '.kt', '.rs', '.scala', '.html', '.css', '.scss', '.sass', '.less', '.sql',
    '.sh', '.bash', '.yml', '.yaml', '.json', '.xml', '.md', '.txt', '.gitignore',
    '.dockerignore', '.env', '.ini', '.cfg', '.conf'
}

SPECIAL_FILES = {
    'Dockerfile', 'docker-compose.yml', 'package.json', 'requirements.txt', 'Gemfile',
    'Pipfile', 'Cargo.toml', 'pom.xml', 'build.gradle'
}

CONFIG_EXTENSIONS = {'.yml', '.yaml', '.json', '.xml', '.ini', '.cfg', '.conf'}
CONFIG_NAMES = {'config', 'settings', 'environment'}

import logging

# Set up logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

def read_gitignore_file(directory: Path) -> List[str]:
    """Read a .gitignore file from the given directory and return a list of patterns."""
    patterns = []
    gitignore_path = directory / '.gitignore'
    if gitignore_path.exists():
        with open(gitignore_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    patterns.append(line)
    return patterns

def find_repo_root(start_path: Path) -> Path:
    """Find the repository root by looking for .git directory."""
    current_path = start_path.absolute()
    while current_path != current_path.parent:
        if (current_path / '.git').is_dir():
            return current_path
        current_path = current_path.parent
    return start_path  # If no .git directory found, return the start path

def is_ignored_path(path: Path, include_ecosystem: bool = False) -> bool:
    """Check if a path should be ignored based on common patterns."""
    if include_ecosystem:
        return False
    str_path = str(path)
    return any(re.search(pattern, str_path) for pattern in COMMON_IGNORE_PATTERNS)

def should_include_file(path: Path, include_test: bool = False, include_config: bool = False) -> bool:
    """Determine if a file should be included based on its path and name."""
    if path.suffix.lower() in CODE_EXTENSIONS or path.name in SPECIAL_FILES:
        if not include_test and ('test' in path.stem.lower() or 'spec' in path.stem.lower()):
            return False
        if not include_config and (path.suffix.lower() in CONFIG_EXTENSIONS or
                                   any(name in path.stem.lower() for name in CONFIG_NAMES)):
            return False
        return True
    return False

def is_ignored_by_gitignore(path: Path, gitignore_patterns: List[str], repo_root: Path) -> bool:
    """Check if a path matches any gitignore patterns."""
    repo_root = repo_root.absolute()
    try:
        relative_path = path.relative_to(repo_root)
    except ValueError:
        relative_path = path

    str_path = str(relative_path).replace(os.sep, '/')
    logger.debug(f"Checking if '{str_path}' is ignored by gitignore")

    for pattern in gitignore_patterns:
        if pattern.endswith('/'):
            normalized_pattern = pattern.rstrip('/')
            if str_path == normalized_pattern or str_path.startswith(normalized_pattern + '/'):
                logger.debug(f"'{str_path}' is ignored because it is in directory '{pattern}'")
                return True
        elif pattern.startswith('/'):
            if fnmatch.fnmatch(str_path, pattern.lstrip('/')):
                logger.debug(f"'{str_path}' matches pattern '{pattern}'")
                return True
        else:
            if fnmatch.fnmatch(str_path, pattern):
                logger.debug(f"'{str_path}' matches pattern '{pattern}'")
                return True
            parts = str_path.split('/')
            for i in range(len(parts)):
                if fnmatch.fnmatch('/'.join(parts[:i+1]), pattern):
                    logger.debug(f"'{'/'.join(parts[:i+1])}' matches pattern '{pattern}'")
                    return True

    logger.debug(f"'{str_path}' is not ignored by gitignore")
    return False

def filter_code_files(start_dir: Path, include_test: bool = False, include_config: bool = False,
                     include_ecosystem: bool = False, exclude_patterns: List[str] = None,
                     include_gitignored: bool = False) -> Iterator[Path]:
    """Filter and yield code files based on various criteria."""
    if exclude_patterns is None:
        exclude_patterns = []

    repo_root = find_repo_root(start_dir).absolute()
    logger.debug(f"Repository root: {repo_root}")

    def process_directory(dir_path: Path, inherited_gitignore: List[str]) -> Iterator[Path]:
        # Read local .gitignore unless user wants to include gitignored files
        local_gitignore = read_gitignore_file(dir_path) if not include_gitignored else []
        # Combine parent's patterns with local ones
        current_gitignore = inherited_gitignore + local_gitignore
        logger.debug(f"Processing directory: {dir_path} with gitignore patterns: {current_gitignore}")

        for item in os.scandir(dir_path):
            item_path = Path(item.path)
            try:
                relative_path = item_path.relative_to(repo_root)
            except ValueError:
                relative_path = item_path

            str_rel_path = str(relative_path).replace(os.sep, '/')
            logger.debug(f"Checking item: {str_rel_path}")

            if item.is_file():
                if should_include_file(item_path, include_test, include_config) and \
                   not any(fnmatch.fnmatch(str_rel_path, pattern) for pattern in exclude_patterns) and \
                   (include_gitignored or not is_ignored_by_gitignore(relative_path, current_gitignore, repo_root)):
                    logger.debug(f"Yielding file: {str_rel_path}")
                    yield relative_path
            elif item.is_dir():
                # Check if the directory itself should be processed before recursing
                if not is_ignored_path(item_path, include_ecosystem) and \
                   not any(fnmatch.fnmatch(str_rel_path, pattern) for pattern in exclude_patterns) and \
                   (include_gitignored or not is_ignored_by_gitignore(relative_path, current_gitignore, repo_root)):
                    yield from process_directory(item_path, current_gitignore)
                else:
                    logger.debug(f"Skipping directory: {str_rel_path}")

    yield from process_directory(repo_root, [])