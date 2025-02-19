from abc import ABC, abstractmethod
from typing import Protocol
import pyperclip
from ..domain.models import Repository, AnalysisResult

class OutputStrategy(ABC):
    """Base class for different output methods."""
    
    @abstractmethod
    async def output_repository(self, repo: Repository) -> None:
        """Output the repository files."""
        pass
    
    @abstractmethod
    async def output_analysis(self, analysis: AnalysisResult) -> None:
        """Output the analysis results."""
        pass

class ClipboardOutput(OutputStrategy):
    """Strategy for copying output to clipboard."""
    
    async def output_repository(self, repo: Repository) -> None:
        output_string = self._format_repository(repo)
        pyperclip.copy(output_string)

    async def output_analysis(self, analysis: AnalysisResult) -> None:
        output_string = self._format_analysis(analysis)
        pyperclip.copy(output_string)
        
    def _format_repository(self, repo: Repository) -> str:
        parts = []
        for file in repo.files:
            parts.append(f"\n\n--- {file.path} ---\n{file.content}")
        return "".join(parts).strip()
    
    def _format_analysis(self, analysis: AnalysisResult) -> str:
        parts = []
        for file_analysis in analysis.analyzed_files:
            if file_analysis.relevance_score >= 0.5:  # Default threshold
                file = file_analysis.file
                parts.append(f"\n\n--- {file.path} (Score: {file_analysis.relevance_score:.2f}) ---\n{file.content}")
        if analysis.thoughts:
            parts.append(f"\n\nAnalysis Thoughts:\n{analysis.thoughts}")
        return "".join(parts).strip()

class ConsoleOutput(OutputStrategy):
    """Strategy for printing output to console."""
    
    async def output_repository(self, repo: Repository) -> None:
        for file in repo.files:
            print(f"\n--- {file.path} ---")
            print(file.content)

    async def output_analysis(self, analysis: AnalysisResult) -> None:
        for file_analysis in analysis.analyzed_files:
            if file_analysis.relevance_score >= 0.5:
                print(f"\n--- {file_analysis.file.path} (Score: {file_analysis.relevance_score:.2f}) ---")
                print(file_analysis.file.content)
        if analysis.thoughts:
            print(f"\nAnalysis Thoughts:\n{analysis.thoughts}")

class OutputService:
    """Service for managing output strategies."""
    
    def __init__(self, strategy: OutputStrategy):
        self.strategy = strategy

    async def output_repository(self, repo: Repository) -> None:
        await self.strategy.output_repository(repo)

    async def output_analysis(self, analysis: AnalysisResult) -> None:
        await self.strategy.output_analysis(analysis) 