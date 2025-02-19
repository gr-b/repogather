from typing import Dict, List, Optional
import openai
from ..domain.models import RepositoryFile

class OpenAIClient:
    """Client for interacting with OpenAI API."""
    
    async def analyze_files(
        self,
        files: List[RepositoryFile],
        query: str,
        model: str
    ) -> Dict:
        """
        Analyze files using OpenAI's API.
        
        Args:
            files: List of files to analyze
            query: Natural language query
            model: Model to use for analysis
            
        Returns:
            Dict containing file scores and thoughts
        """
        # Construct the prompt
        file_contents = "\n\n".join([
            f"=== {f.path} ===\n{f.content}"
            for f in files
        ])
        
        prompt = f"""
        Analyze these files in relation to this query: {query}
        
        Files:
        {file_contents}
        
        For each file, provide:
        1. A relevance score (0-1)
        2. Brief explanation of relevance
        
        Also provide overall thoughts about how these files relate to the query.
        """
        
        # Call OpenAI API
        response = await openai.ChatCompletion.acreate(
            model=model,
            messages=[
                {"role": "system", "content": "You are a code analysis assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        
        # Parse response and extract scores
        # This is a simplified implementation - would need proper response parsing
        analysis_text = response.choices[0].message.content
        
        # Mock implementation - replace with actual parsing
        return {
            'file_scores': {
                str(f.path): 0.8 for f in files  # Mock scores
            },
            'thoughts': analysis_text
        } 