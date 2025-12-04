"""
Configuration module for Personal Vault Backend.

Centralizes all environment variables and configuration constants.
Follows the 12-factor app methodology for configuration management.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """
    Application configuration loaded from environment variables.
    
    All sensitive data (API keys, database URLs) should be set via environment
    variables and never committed to version control.
    """
    
    # Supabase Configuration
    SUPABASE_URL: Optional[str] = os.getenv("SUPABASE_URL")
    SUPABASE_KEY: Optional[str] = os.getenv("SUPABASE_KEY")
    
    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # Server Configuration
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    
    # Application Settings
    APP_NAME: str = "Personal Vault API"
    APP_VERSION: str = "2.1.0"
    APP_DESCRIPTION: str = "Medical Compliance Microservice - Upload Once, Standardize Many Times"
    
    # Feature Flags
    MOCK_AI: bool = os.getenv("MOCK_AI", "false").lower() == "true"
    
    # File Upload Limits
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_FILE_TYPES: list = ["image/jpeg", "image/png", "image/jpg", "application/pdf"]
    
    # Supabase Storage
    STORAGE_BUCKET_NAME: str = "vaccine-records"
    
    # Supported Compliance Standards
    VALID_STANDARDS: list = ["cornell_tech", "us_cdc", "uk_nhs", "canada_health"]
    
    @classmethod
    def validate(cls) -> list[str]:
        """
        Validate that all required configuration is present.
        
        Returns:
            List of missing configuration keys (empty if all valid)
        """
        missing = []
        
        if not cls.SUPABASE_URL:
            missing.append("SUPABASE_URL")
        if not cls.SUPABASE_KEY:
            missing.append("SUPABASE_KEY")
        if not cls.OPENAI_API_KEY:
            missing.append("OPENAI_API_KEY")
            
        return missing
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production environment."""
        return os.getenv("ENVIRONMENT", "development").lower() == "production"


# Create a singleton instance
config = Config()
