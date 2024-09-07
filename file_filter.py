from pathlib import Path

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

def filter_code_files(root_dir: Path, include_test: bool = False, include_config: bool = False):
    for file_path in root_dir.rglob('*'):
        if file_path.is_file() and is_code_file(file_path):
            if (include_test or not is_test_file(file_path)) and (include_config or not is_config_file(file_path)):
                yield file_path.relative_to(root_dir)