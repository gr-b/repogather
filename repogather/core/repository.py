from pathlib import Path
from typing import List
from ..domain.models import Repository, RepositoryFile, GatherOptions

class RepositoryService:
    """Service for loading and managing repository files."""
    
    def __init__(self, file_filter, token_counter):
        self.file_filter = file_filter
        self.token_counter = token_counter
    
    async def load_repository(self, path: Path, options: GatherOptions) -> Repository:
        """
        Load a repository from the given path using the specified options.
        
        Args:
            path: Root path of the repository
            options: Options controlling which files to include
            
        Returns:
            Repository object containing the filtered files
        """
        files = self.file_filter.filter_files(path, options)
        repo_files = [await self._create_repository_file(f) for f in files]
        
        return Repository(
            root=path,
            files=repo_files
        )
    
    async def _create_repository_file(self, path: Path) -> RepositoryFile:
        """Create a RepositoryFile object from a path."""
        content = path.read_text()
        token_count = self.token_counter.count_tokens(content)
        return RepositoryFile(
            path=path,
            content=content,
            token_count=token_count
        ) 