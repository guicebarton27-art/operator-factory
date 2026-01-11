import os
from typing import Optional

class Config:
    """Configuration class for LLM endpoints and API keys."""
    
    # OpenRouter Configuration
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    
    # Mimo Configuration
    MIMO_BASE_URL = os.getenv("MIMO_BASE_URL", "https://api.mimo.com/v1")
    
    # Default Model
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "anthropic/claude-3.5-sonnet")
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that required configuration is present."""
        if not cls.OPENROUTER_API_KEY:
            print("Warning: OPENROUTER_API_KEY is not set")
            return False
        return True
