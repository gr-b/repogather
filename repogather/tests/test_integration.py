import os
import subprocess
import sys
from pathlib import Path

import pytest

@pytest.fixture
def fake_repo(tmp_path: Path) -> Path:
    """
    Sets up a fake repository:
      - Creates a .git directory so that repogather considers tmp_path as repo root.
      - Returns the repository root as a Path object.
    """
    (tmp_path / ".git").mkdir()
    return tmp_path

def run_repogather(repo_path: Path, args: list) -> subprocess.CompletedProcess:
    """
    Runs repogather with the given args from the repo_path.
    We use `sys.executable -m repogather ...` so that the module is loaded correctly.
    """
    cmd = [sys.executable, "-m", "repogather"] + args
    return subprocess.run(cmd, cwd=repo_path, capture_output=True, text=True)

def test_all_excludes_gitignored_files(fake_repo: Path):
    """
    Create a repo with a root-level .gitignore that excludes "ignored.txt".
    Then run repogather with the --all option and verify that "ignored.txt" is omitted.
    """
    # Create .gitignore that excludes ignored.txt
    (fake_repo / ".gitignore").write_text("ignored.txt\n")

    # Create two files: one to be included and one to be ignored
    (fake_repo / "included.txt").write_text("This file should be included.")
    (fake_repo / "ignored.txt").write_text("This file should be ignored.")

    # Run repogather in --all mode (without --include-gitignored)
    result = run_repogather(fake_repo, ["--all"])
    assert result.returncode == 0, f"repogather exited with error: {result.stderr}"

    output = result.stdout
    # The output should contain the included file but not the ignored file
    assert "included.txt" in output, "Expected included.txt to appear in output."
    assert "This file should be included." in output, "Expected file contents to be printed."
    assert "ignored.txt" not in output, "Did not expect ignored.txt to be printed."
    assert "This file should be ignored." not in output, "Ignored file's contents should not be printed."

def test_all_includes_gitignored_files_with_flag(fake_repo: Path):
    """
    With the same setup as the previous test, use --include-gitignored.
    Verify that the ignored file is now present in the output.
    """
    (fake_repo / ".gitignore").write_text("ignored.txt\n")
    (fake_repo / "included.txt").write_text("This file should be included.")
    (fake_repo / "ignored.txt").write_text("This file should be ignored.")

    # Run repogather in --all mode with --include-gitignored flag
    result = run_repogather(fake_repo, ["--all", "--include-gitignored"])
    assert result.returncode == 0, f"repogather exited with error: {result.stderr}"

    output = result.stdout
    # Now both files should appear
    assert "included.txt" in output, "Expected included.txt to appear in output."
    assert "ignored.txt" in output, "Expected ignored.txt to appear because --include-gitignored was used."
    assert "This file should be included." in output
    assert "This file should be ignored." in output

def test_all_nested_gitignore(fake_repo: Path):
    """
    Create a nested directory with its own .gitignore.
      - The root .gitignore is empty (or does not exclude the subdirectory).
      - The subdirectory contains a .gitignore that excludes a specific file.
    Verify that repogather --all omits the nested ignored file.
    """
    # Write an empty root .gitignore (or you could omit it)
    (fake_repo / ".gitignore").write_text("")

    # Create a subdirectory with its own .gitignore
    subdir = fake_repo / "subdir"
    subdir.mkdir()
    (subdir / ".gitignore").write_text("nested_ignore.txt\n")

    # Create files inside the subdirectory
    (subdir / "included.txt").write_text("This nested file should be included.")
    (subdir / "nested_ignore.txt").write_text("This nested file should be ignored.")

    # Run repogather in --all mode
    result = run_repogather(fake_repo, ["--all"])
    assert result.returncode == 0, f"repogather exited with error: {result.stderr}"

    output = result.stdout
    # Expect the included file to be present and the nested ignored file to be absent
    assert "subdir/included.txt" in output, "Expected subdir/included.txt to appear in output."
    assert "This nested file should be included." in output
    assert "subdir/nested_ignore.txt" not in output, "Did not expect subdir/nested_ignore.txt in output."
    assert "This nested file should be ignored." not in output

def test_all_nested_gitignore_with_include_flag(fake_repo: Path):
    """
    Like the previous test, but with --include-gitignored specified.
    The nested ignored file should now be present.
    """
    (fake_repo / ".gitignore").write_text("")
    subdir = fake_repo / "subdir"
    subdir.mkdir()
    (subdir / ".gitignore").write_text("nested_ignore.txt\n")
    (subdir / "included.txt").write_text("This nested file should be included.")
    (subdir / "nested_ignore.txt").write_text("This nested file should be ignored.")

    result = run_repogather(fake_repo, ["--all", "--include-gitignored"])
    assert result.returncode == 0, f"repogather exited with error: {result.stderr}"

    output = result.stdout
    # With --include-gitignored, both files should appear
    assert "subdir/included.txt" in output
    assert "This nested file should be included." in output
    assert "subdir/nested_ignore.txt" in output, "Expected nested_ignore.txt to appear when --include-gitignored is used."
    assert "This nested file should be ignored." in output

def test_directory_gitignore_pattern(fake_repo: Path):
    """
    Test that directory patterns in .gitignore (ending with /) work correctly.
    """
    # Create .gitignore that excludes the ignored_dir/ directory
    (fake_repo / ".gitignore").write_text("ignored_dir/\n")

    # Create directories and files
    (fake_repo / "normal_dir").mkdir()
    (fake_repo / "normal_dir/file.txt").write_text("This file should be included.")
    
    (fake_repo / "ignored_dir").mkdir()
    (fake_repo / "ignored_dir/file.txt").write_text("This file should be ignored.")

    # Run repogather
    result = run_repogather(fake_repo, ["--all"])
    assert result.returncode == 0

    output = result.stdout
    # Check that files in normal_dir are included but files in ignored_dir are not
    assert "normal_dir/file.txt" in output
    assert "This file should be included." in output
    assert "ignored_dir/file.txt" not in output
    assert "This file should be ignored." not in output 