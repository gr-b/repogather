from pathlib import Path
from repogather.domain.models import Repository, RepositoryFile

def test_repository_total_tokens():
    """Test Repository.total_tokens property."""
    files = [
        RepositoryFile(Path('a.py'), 'content', 100),
        RepositoryFile(Path('b.py'), 'content', 200)
    ]
    repo = Repository(Path('.'), files)
    assert repo.total_tokens == 300 