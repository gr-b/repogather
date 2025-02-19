from pathlib import Path
from ..domain.models import (
    Repository, 
    AnalysisResult, 
    GatherOptions, 
    AnalysisOptions
)

class GatherRepositoryUseCase:
    """Use case for gathering repository files."""
    
    def __init__(self, repo_service, output_service):
        self.repo_service = repo_service
        self.output_service = output_service
    
    async def execute(self, path: Path, options: GatherOptions) -> Repository:
        """
        Gather repository files and output them.
        
        Args:
            path: Repository root path
            options: Options for file gathering
            
        Returns:
            Repository object containing gathered files
        """
        repo = await self.repo_service.load_repository(path, options)
        await self.output_service.output_repository(repo)
        return repo

class AnalyzeRepositoryUseCase:
    """Use case for analyzing repository files."""
    
    def __init__(self, repo_service, analysis_service, output_service):
        self.repo_service = repo_service
        self.analysis_service = analysis_service
        self.output_service = output_service
    
    async def execute(
        self, 
        path: Path, 
        options: AnalysisOptions
    ) -> AnalysisResult:
        """
        Analyze repository files and output results.
        
        Args:
            path: Repository root path
            options: Options for analysis
            
        Returns:
            Analysis results
        """
        repo = await self.repo_service.load_repository(path, options)
        analysis = await self.analysis_service.analyze_repository(repo, options)
        await self.output_service.output_analysis(analysis)
        return analysis 