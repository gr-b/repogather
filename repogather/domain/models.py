from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

@dataclass
class RepositoryFile:
    """Represents a single file in the repository with its content and metadata."""
    path: Path
    content: str
    token_count: int

@dataclass
class Repository:
    """Represents a collection of files in a repository."""
    root: Path
    files: List[RepositoryFile]
    
    @property
    def total_tokens(self) -> int:
        return sum(f.token_count for f in self.files)

@dataclass
class FileAnalysis:
    """Analysis results for a single file."""
    relevance_score: float
    file: RepositoryFile

@dataclass
class AnalysisResult:
    """Complete analysis results for a repository."""
    analyzed_files: List[FileAnalysis]
    thoughts: Optional[str] = None

@dataclass
class GatherOptions:
    """Options for gathering files from a repository."""
    include_tests: bool = False
    include_config: bool = False
    include_ecosystem: bool = False
    include_gitignored: bool = False
    exclude_patterns: List[str] = field(default_factory=list)

@dataclass
class AnalysisOptions:
    """Options for analyzing repository files."""
    query: str
    model: str = "gpt-4-turbo-preview"
    relevance_threshold: float = 0.5
    gather_options: GatherOptions = field(default_factory=GatherOptions) 