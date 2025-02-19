import os
import subprocess
import sys
from pathlib import Path

import pytest
from repogather.file_filter import filter_code_files

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
    files = list(filter_code_files(fake_repo))
    
    # Convert paths to strings for easier comparison
    file_paths = [str(f) for f in files]
    
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

    files = list(filter_code_files(fake_repo, include_gitignored=True))
    file_paths = [str(f) for f in files]
    
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