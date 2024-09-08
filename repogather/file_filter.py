from pathlib import Path
import re
import os
from typing import Iterator, List
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

def find_repo_root(start_path: Path) -> Path:
    current_path = start_path.absolute()
    while current_path != current_path.parent:
        if (current_path / '.git').is_dir():
            return current_path
        current_path = current_path.parent
    return start_path  # If no .git directory found, return the start path

def parse_gitignore(repo_root: Path) -> List[str]:
    gitignore_patterns = []
    gitignore_path = repo_root / '.gitignore'
    if gitignore_path.exists():
        with open(gitignore_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    gitignore_patterns.append(line)
    return gitignore_patterns

def is_ignored_by_gitignore(path: Path, gitignore_patterns: List[str], repo_root: Path) -> bool:
    repo_root = repo_root.absolute()
    try:
        relative_path = path.relative_to(repo_root)
    except ValueError:
        # If path is already relative, use it as is
        relative_path = path

    str_path = str(relative_path).replace(os.sep, '/')
    logger.debug(f"Checking if '{str_path}' is ignored by gitignore")

    for pattern in gitignore_patterns:
        if pattern.startswith('/'):
            # If the pattern starts with '/', it should match from the root of the repo
            if fnmatch.fnmatch(str_path, pattern.lstrip('/')):
                logger.debug(f"'{str_path}' matches pattern '{pattern}'")
                return True
        else:
            # If the pattern doesn't start with '/', it can match at any level
            if fnmatch.fnmatch(str_path, pattern):
                logger.debug(f"'{str_path}' matches pattern '{pattern}'")
                return True
            # Also check if it matches any parent directory
            parts = str_path.split('/')
            for i in range(len(parts)):
                if fnmatch.fnmatch('/'.join(parts[:i+1]), pattern):
                    logger.debug(f"'{'/'.join(parts[:i+1])}' matches pattern '{pattern}'")
                    return True

    logger.debug(f"'{str_path}' is not ignored by gitignore")
    return False

def is_ignored_path(path: Path, include_ecosystem: bool) -> bool:
    if include_ecosystem:
        return False
    str_path = str(path)
    return any(re.search(pattern, str_path) for pattern in COMMON_IGNORE_PATTERNS)

def should_include_file(file_path: Path, include_test: bool, include_config: bool) -> bool:
    if file_path.suffix.lower() in CODE_EXTENSIONS or file_path.name in SPECIAL_FILES:
        if not include_test and ('test' in file_path.stem.lower() or 'spec' in file_path.stem.lower()):
            return False
        if not include_config and (file_path.suffix.lower() in CONFIG_EXTENSIONS or
                                   any(name in file_path.stem.lower() for name in CONFIG_NAMES)):
            return False
        return True
    return False


def filter_code_files(start_dir: Path, include_test: bool = False, include_config: bool = False,
                      include_ecosystem: bool = False, exclude_patterns: List[str] = None,
                      include_gitignored: bool = False) -> Iterator[Path]:
    if exclude_patterns is None:
        exclude_patterns = []

    repo_root = find_repo_root(start_dir).absolute()
    logger.debug(f"Repository root: {repo_root}")
    gitignore_patterns = parse_gitignore(repo_root) if not include_gitignored else []
    logger.debug(f"Gitignore patterns: {gitignore_patterns}")

    def should_process_dir(dir_path: Path) -> bool:
        relative_path = dir_path.relative_to(repo_root)
        logger.debug(f"Checking if directory should be processed: {relative_path}")
        return not is_ignored_path(relative_path, include_ecosystem) and \
               not any(fnmatch.fnmatch(str(relative_path), pattern) for pattern in exclude_patterns) and \
               (include_gitignored or not is_ignored_by_gitignore(relative_path, gitignore_patterns, repo_root))

    def process_directory(dir_path: Path) -> Iterator[Path]:
        logger.debug(f"Processing directory: {dir_path}")
        for item in os.scandir(dir_path):
            relative_path = Path(item.path).relative_to(repo_root)
            logger.debug(f"Checking item: {relative_path}")

            if item.is_file():
                if should_include_file(Path(item.path), include_test, include_config) and \
                   not any(fnmatch.fnmatch(str(relative_path), pattern) for pattern in exclude_patterns) and \
                   (include_gitignored or not is_ignored_by_gitignore(relative_path, gitignore_patterns, repo_root)):
                    logger.debug(f"Yielding file: {relative_path}")
                    yield relative_path
            elif item.is_dir():
                if should_process_dir(Path(item.path)):
                    yield from process_directory(Path(item.path))
                else:
                    logger.debug(f"Skipping directory: {relative_path}")

    yield from process_directory(repo_root)