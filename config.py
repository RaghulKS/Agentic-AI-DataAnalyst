# API Keys and Configuration

# OpenAI API Key (required)
OPENAI_API_KEY = "sk-your-openai-api-key-here"

# Model Configuration
OPENAI_MODEL = "gpt-4-turbo-preview"

# Optional: Other API keys for future enhancements
ANTHROPIC_API_KEY = "your-anthropic-key-here"
HUGGINGFACE_API_KEY = "your-huggingface-key-here"

# Database configuration
DATABASE_URL = "sqlite:///autoanalyst.db"

# Email configuration for report delivery
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_USER = "your-email@gmail.com"
EMAIL_PASSWORD = "your-app-password"

# API Server configuration
API_HOST = "0.0.0.0"
API_PORT = 8000

# Redis configuration (for caching)
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0

# Streamlit configuration
STREAMLIT_PORT = 8501