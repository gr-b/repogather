from typing import Dict, List
from ..domain.models import RepositoryFile

class MockOpenAIClient:
    """Mock OpenAI client for testing."""
    
    async def analyze_files(
        self,
        files: List[RepositoryFile],
        query: str,
        model: str
    ) -> Dict:
        """Return mock analysis results."""
        return {
            'file_scores': {
                str(f.path): 0.8 for f in files
            },
            'thoughts': "Mock analysis thoughts"
        } 

class MockClipboard:
    """Mock clipboard for testing."""
    
    def __init__(self):
        self.content = ""
    
    def copy(self, text: str):
        self.content = text
    
    def paste(self) -> str:
        return self.content 