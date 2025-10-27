"""
Core configuration module for the ChatBot application
Handles environment variables, CORS settings, and AI provider configuration
"""
import os
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application settings loaded from environment variables"""
    
    def __init__(self):
        # Database configuration
        self.mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        self.mongodb_db_name = os.getenv("MONGODB_DB_NAME", "chatbotdb")
        
        # CORS configuration
        self.cors_allowed_origins = os.getenv(
            "CORS_ALLOWED_ORIGINS", 
            "http://localhost:3000,http://localhost:5173,http://127.0.0.1:5173"
        )
        self.cors_allow_credentials = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"
        self.cors_allow_methods = os.getenv(
            "CORS_ALLOW_METHODS", 
            "GET,POST,PUT,DELETE,OPTIONS"
        ).split(",")
        self.cors_allow_headers = os.getenv("CORS_ALLOW_HEADERS", "*").split(",")
        
        # AI Provider configuration
        self.ai_provider = os.getenv("AI_PROVIDER", "gemini").lower()
        
        # Gemini configuration
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        
        # OpenAI configuration
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        
        # Application configuration
        self.app_name = os.getenv("APP_NAME", "ChatBot API")
        self.app_version = os.getenv("APP_VERSION", "1.0.0")
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        
        # Server configuration
        self.host = os.getenv("HOST", "127.0.0.1")
        self.port = int(os.getenv("PORT", "8000"))
        self.reload = os.getenv("RELOAD", "true").lower() == "true"
        
        # Chat configuration
        self.max_history_messages = int(os.getenv("MAX_HISTORY_MESSAGES", "15"))
        self.system_prompt = os.getenv(
            "SYSTEM_PROMPT", 
            "Bạn là một AI Assistant thông minh và hữu ích. Hãy trả lời câu hỏi của người dùng một cách chính xác và thân thiện bằng tiếng Việt."
        )

# Global settings instance
settings = Settings()

def get_settings() -> Settings:
    """Get application settings"""
    return settings
