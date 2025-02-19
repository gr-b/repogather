import os
import subprocess
import sys
from pathlib import Path

import pytest
from repogather.file_filter import filter_code_files
from repogather.domain.models import GatherOptions, AnalysisOptions
from repogather.application.use_cases import GatherRepositoryUseCase, AnalyzeRepositoryUseCase
from repogather.core.repository import RepositoryService
from repogather.core.analysis import AnalysisService
from repogather.core.file_filter import FileFilter
from repogather.core.token_counter import TokenCounter
from repogather.core.openai import OpenAIClient
from repogather.application.output import OutputService, ConsoleOutput
from .mocks import MockOpenAIClient

@pytest.fixture
def fake_repo(tmp_path: Path) -> Path:
    """
    Sets up a fake repository:
      - Creates a .git directory so that repogather considers tmp_path as repo root.
      - Returns the repository root as a Path object.
    """
    (tmp_path / ".git").mkdir()
    return tmp_path

def test_all_excludes_gitignored_files(fake_repo: Path):
    """
    Create a repo with a root-level .gitignore that excludes "ignored.txt".
    Verify that "ignored.txt" is omitted from the results.
    """
    # Create .gitignore that excludes ignored.txt
    (fake_repo / ".gitignore").write_text("ignored.py\n")

    # Create two files with .py extension
    (fake_repo / "included.py").write_text("This file should be included.")
    (fake_repo / "ignored.py").write_text("This file should be ignored.")

    # Get filtered files
    file_filter = FileFilter()
    options = GatherOptions()
    files = file_filter.filter_files(fake_repo, options)
    
    # Convert paths to strings for easier comparison
    file_paths = [str(f.name) for f in files]
    
    assert "included.py" in file_paths, "Expected included.py to appear in results."
    assert "ignored.py" not in file_paths, "Did not expect ignored.py in results."

def test_all_includes_gitignored_files_with_flag(fake_repo: Path):
    """
    With the same setup as the previous test, use include_gitignored=True.
    Verify that the ignored file is now present in the results.
    """
    (fake_repo / ".gitignore").write_text("ignored.py\n")
    (fake_repo / "included.py").write_text("This file should be included.")
    (fake_repo / "ignored.py").write_text("This file should be ignored.")

    file_filter = FileFilter()
    options = GatherOptions(include_gitignored=True)
    files = file_filter.filter_files(fake_repo, options)
    file_paths = [str(f.name) for f in files]
    
    assert "included.py" in file_paths, "Expected included.py to appear in results."
    assert "ignored.py" in file_paths, "Expected ignored.py to appear when include_gitignored=True."

def test_all_nested_gitignore(fake_repo: Path):
    """
    Create a nested directory with its own .gitignore.
    Verify that files ignored by the nested .gitignore are omitted.
    """
    # Write an empty root .gitignore
    (fake_repo / ".gitignore").write_text("")

    # Create a subdirectory with its own .gitignore
    subdir = fake_repo / "subdir"
    subdir.mkdir()
    (subdir / ".gitignore").write_text("nested_ignore.py\n")

    # Create files inside the subdirectory
    (subdir / "included.py").write_text("This nested file should be included.")
    (subdir / "nested_ignore.py").write_text("This nested file should be ignored.")

    # Get filtered files
    files = list(filter_code_files(fake_repo))
    file_paths = [str(f) for f in files]
    
    assert "subdir/included.py" in file_paths, "Expected subdir/included.py to appear in results."
    assert "subdir/nested_ignore.py" not in file_paths, "Did not expect subdir/nested_ignore.py in results."

def test_directory_gitignore_pattern(fake_repo: Path):
    """
    Test that directory patterns in .gitignore (ending with /) work correctly.
    """
    # Create .gitignore that excludes the ignored_dir/ directory
    (fake_repo / ".gitignore").write_text("ignored_dir/\n")

    # Create directories and files
    (fake_repo / "normal_dir").mkdir()
    (fake_repo / "normal_dir/file.py").write_text("This file should be included.")
    
    (fake_repo / "ignored_dir").mkdir()
    (fake_repo / "ignored_dir/file.py").write_text("This file should be ignored.")

    # Get filtered files
    files = list(filter_code_files(fake_repo))
    file_paths = [str(f) for f in files]
    
    assert "normal_dir/file.py" in file_paths, "Expected normal_dir/file.py to appear in results."
    assert "ignored_dir/file.py" not in file_paths, "Did not expect ignored_dir/file.py in results."

@pytest.fixture
def sample_repo(tmp_path):
    """Create a sample repository structure."""
    # Create main code files
    (tmp_path / "src").mkdir()
    (tmp_path / "src/main.py").write_text("def main():\n    print('hello')")
    (tmp_path / "src/utils.py").write_text("def helper():\n    return True")
    
    # Create test files
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests/test_main.py").write_text("def test_main():\n    assert True")
    
    # Create config files
    (tmp_path / "pyproject.toml").write_text("[tool.poetry]\nname = 'test'")
    
    return tmp_path

@pytest.fixture
def services():
    """Create service instances for testing."""
    file_filter = FileFilter()
    token_counter = TokenCounter()
    openai_client = MockOpenAIClient()  # Use mock instead of real client
    
    repo_service = RepositoryService(file_filter, token_counter)
    analysis_service = AnalysisService(openai_client)
    output_service = OutputService(ConsoleOutput())
    
    return repo_service, analysis_service, output_service

@pytest.mark.asyncio
async def test_gather_repository(sample_repo, services):
    """Test gathering repository files."""
    repo_service, _, output_service = services
    options = GatherOptions()
    
    use_case = GatherRepositoryUseCase(repo_service, output_service)
    repo = await use_case.execute(sample_repo, options)
    
    # Verify only non-test files are included by default
    file_names = [f.path.name for f in repo.files]
    assert "main.py" in file_names
    assert "utils.py" in file_names
    assert "test_main.py" not in file_names
    assert "pyproject.toml" not in file_names

@pytest.mark.asyncio
async def test_analyze_repository(sample_repo, services):
    """Test analyzing repository files."""
    repo_service, analysis_service, output_service = services
    options = AnalysisOptions(
        query="Find files related to the main application logic",
        model="gpt-4-turbo-preview"
    )
    
    use_case = AnalyzeRepositoryUseCase(repo_service, analysis_service, output_service)
    result = await use_case.execute(sample_repo, options)
    
    assert len(result.analyzed_files) > 0
    assert result.thoughts is not None 