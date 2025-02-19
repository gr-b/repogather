import os
import sys
from pathlib import Path
import pytest

# Add the parent directory to PYTHONPATH so we can import repogather
repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root))

@pytest.fixture
def temp_repo_path(tmp_path):
    """Create a temporary repository with some files."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    
    # Create some source files
    src_path = repo_path / "src"
    src_path.mkdir()
    
    (src_path / "main.py").write_text("""
def main():
    print("Hello, world!")
    """)
    
    (src_path / "utils.py").write_text("""
def helper():
    return True
    """)
    
    # Create some test files
    test_path = repo_path / "tests"
    test_path.mkdir()
    
    (test_path / "test_main.py").write_text("""
def test_main():
    assert True
    """)
    
    # Create some config files
    (repo_path / ".gitignore").write_text("*.pyc\n__pycache__")
    (repo_path / "setup.py").write_text("""
from setuptools import setup
setup(name="test")
    """)
    
    return repo_path

@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    return {
        "choices": [
            {
                "message": {
                    "content": """
Analysis of files:

main.py (Score: 0.9)
- Contains main application logic
- High relevance to core functionality

utils.py (Score: 0.7)
- Contains helper functions
- Moderate relevance to core functionality

Overall thoughts:
The main.py file is most relevant as it contains the primary application logic.
                    """
                }
            }
        ]
    } 