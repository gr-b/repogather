import tiktoken

class TokenCounter:
    """Counts tokens in text using tiktoken."""
    
    def __init__(self, model: str = "gpt-4-turbo-preview"):
        self.encoding = tiktoken.encoding_for_model(model)
    
    def count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in the given text.
        
        Args:
            text: Text to count tokens in
            
        Returns:
            Number of tokens
        """
        return len(self.encoding.encode(text)) 