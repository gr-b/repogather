from pathlib import Path
from typing import List
from ..domain.models import Repository, RepositoryFile, GatherOptions, AnalysisOptions

class RepositoryService:
    """Service for loading and managing repository files."""
    
    def __init__(self, file_filter, token_counter):
        self.file_filter = file_filter
        self.token_counter = token_counter
    
    async def load_repository(self, path: Path, options: GatherOptions | AnalysisOptions) -> Repository:
        """
        Load a repository from the given path using the specified options.
        
        Args:
            path: Repository root path
            options: Options controlling which files to include
            
        Returns:
            Repository object containing the filtered files
        """
        # If we get AnalysisOptions, use its gather_options
        gather_options = options.gather_options if hasattr(options, 'gather_options') else options
        files = self.file_filter.filter_files(path, gather_options)
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