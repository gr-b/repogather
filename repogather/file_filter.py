from pathlib import Path
import re

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

def is_ignored_path(file_path: Path, include_ecosystem: bool) -> bool:
    if include_ecosystem:
        return False

    str_path = str(file_path)
    return any(re.search(pattern, str_path) for pattern in COMMON_IGNORE_PATTERNS)

def is_code_file(file_path: Path) -> bool:
    code_extensions = {
        '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.c', '.cpp', '.cs', '.go', '.rb', '.php',
        '.swift', '.kt', '.rs', '.scala', '.html', '.css', '.scss', '.sass', '.less', '.sql',
        '.sh', '.bash', '.yml', '.yaml', '.json', '.xml', '.md', '.txt', '.gitignore',
        '.dockerignore', '.env', '.ini', '.cfg', '.conf'
    }
    special_files = {
        'Dockerfile', 'docker-compose.yml', 'package.json', 'requirements.txt', 'Gemfile',
        'Pipfile', 'Cargo.toml', 'pom.xml', 'build.gradle'
    }
    return file_path.suffix.lower() in code_extensions or file_path.name in special_files

def is_test_file(file_path: Path) -> bool:
    test_patterns = [
        'test_', '_test', 'spec_', '_spec', 'Test', 'Spec',
        '/tests/', '/test/', '/specs/', '/spec/',
        '__tests__', '__test__', '__specs__', '__spec__'
    ]
    return any(pattern in str(file_path) for pattern in test_patterns)

def is_config_file(file_path: Path) -> bool:
    config_extensions = {'.yml', '.yaml', '.json', '.xml', '.ini', '.cfg', '.conf'}
    config_names = {'config', 'settings', 'environment'}
    return (file_path.suffix.lower() in config_extensions or
            any(name in file_path.stem.lower() for name in config_names))

def filter_code_files(root_dir: Path, include_test: bool = False, include_config: bool = False, include_ecosystem: bool = False):
    for file_path in root_dir.rglob('*'):
        if file_path.is_file() and is_code_file(file_path):
            relative_path = file_path.relative_to(root_dir)
            if not is_ignored_path(relative_path, include_ecosystem) and \
               (include_test or not is_test_file(relative_path)) and \
               (include_config or not is_config_file(relative_path)):
                yield relative_path