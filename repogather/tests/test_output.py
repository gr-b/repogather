import pytest
from ..application.output import ClipboardOutput, OutputService
from ..domain.models import Repository, RepositoryFile
from .mocks import MockClipboard
import pyperclip

@pytest.fixture
def mock_clipboard(monkeypatch):
    """Replace pyperclip with mock."""
    mock = MockClipboard()
    monkeypatch.setattr(pyperclip, "copy", mock.copy)
    monkeypatch.setattr(pyperclip, "paste", mock.paste)
    return mock

@pytest.mark.asyncio
async def test_clipboard_output(tmp_path, mock_clipboard):
    """Test clipboard output strategy."""
    # Create test repository
    file = RepositoryFile(
        path=tmp_path / "test.py",
        content="print('hello')",
        token_count=10
    )
    repo = Repository(root=tmp_path, files=[file])
    
    # Test output
    output = ClipboardOutput()
    await output.output_repository(repo)
    
    # Verify clipboard content
    assert "test.py" in mock_clipboard.content
    assert "print('hello')" in mock_clipboard.content 