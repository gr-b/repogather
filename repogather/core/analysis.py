from typing import List, Dict
from ..domain.models import Repository, AnalysisResult, FileAnalysis, AnalysisOptions

class AnalysisService:
    """Service for analyzing repository files using LLM."""
    
    def __init__(self, openai_client):
        self.openai_client = openai_client
    
    async def analyze_repository(
        self, 
        repo: Repository, 
        options: AnalysisOptions
    ) -> AnalysisResult:
        """
        Analyze repository files using the specified options.
        
        Args:
            repo: Repository to analyze
            options: Analysis options including query and model
            
        Returns:
            AnalysisResult containing relevance scores and thoughts
        """
        # Get analysis from LLM
        analysis_response = await self.openai_client.analyze_files(
            files=repo.files,
            query=options.query,
            model=options.model
        )
        
        # Extract file scores and thoughts
        file_scores = analysis_response.get('file_scores', {})
        thoughts = analysis_response.get('thoughts')
        
        # Create FileAnalysis objects
        analyzed_files = []
        for file in repo.files:
            score = file_scores.get(str(file.path), 0.0)
            analyzed_files.append(
                FileAnalysis(
                    relevance_score=score,
                    file=file
                )
            )
        
        # Sort by relevance score
        analyzed_files.sort(
            key=lambda x: x.relevance_score,
            reverse=True
        )
        
        return AnalysisResult(
            analyzed_files=analyzed_files,
            thoughts=thoughts
        ) 