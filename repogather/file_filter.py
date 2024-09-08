from pathlib import Path
import re
import os

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

def find_repo_root(start_path: Path) -> Path:
    current_path = start_path.absolute()
    while current_path != current_path.parent:
        if (current_path / '.git').is_dir():
            return current_path
        current_path = current_path.parent
    return start_path  # If no .git directory found, return the start path

def parse_gitignore(repo_root):
    gitignore_patterns = []
    gitignore_path = repo_root / '.gitignore'
    if gitignore_path.exists():
        with open(gitignore_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    pattern = re.escape(line).replace(r'\*', '.*').replace(r'\?', '.')
                    if pattern.endswith('/'):
                        pattern += '.*'
                    else:
                        pattern += '$'
                    gitignore_patterns.append(re.compile(pattern))
    return gitignore_patterns

def is_ignored_by_gitignore(path, gitignore_patterns):
    str_path = str(path).replace(os.sep, '/')
    for pattern in gitignore_patterns:
        if pattern.match(str_path):
            return True
        if '/' in str_path:
            parent_path = '/'.join(str_path.split('/')[:-1]) + '/'
            if pattern.match(parent_path):
                return True
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
                      include_ecosystem: bool = False, exclude_patterns: list = None,
                      include_gitignored: bool = False):
    if exclude_patterns is None:
        exclude_patterns = []

    repo_root = find_repo_root(start_dir)
    gitignore_patterns = parse_gitignore(repo_root) if not include_gitignored else []
    gitignore_cache = {}

    for root, dirs, files in os.walk(repo_root):
        rel_root = Path(root).relative_to(repo_root)

        # Early directory filtering
        dirs[:] = [d for d in dirs if not is_ignored_path(rel_root / d, include_ecosystem)]

        # Check gitignore for the current directory
        if not include_gitignored:
            if str(rel_root) not in gitignore_cache:
                gitignore_cache[str(rel_root)] = is_ignored_by_gitignore(rel_root, gitignore_patterns)
            if gitignore_cache[str(rel_root)]:
                dirs[:] = []  # Skip all subdirectories
                continue

        for file in files:
            file_path = Path(root) / file
            relative_path = file_path.relative_to(repo_root)
            if should_include_file(file_path, include_test, include_config) and \
               not any(pattern in str(relative_path) for pattern in exclude_patterns) and \
               (include_gitignored or not is_ignored_by_gitignore(relative_path, gitignore_patterns)):
                yield relative_path