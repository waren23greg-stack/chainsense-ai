import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    SECRET_KEY             = os.getenv("SECRET_KEY", None)
    FLASK_ENV              = os.getenv("FLASK_ENV", "production")
    DEBUG                  = False
    MAX_CONTENT_LENGTH     = 10 * 1024 * 1024
    ALLOWED_EXTENSIONS     = {"csv"}
    RATELIMIT_DEFAULT      = "100 per hour"
    RATELIMIT_UPLOAD       = "10 per minute"
    RATELIMIT_AI           = "20 per hour"
    RATELIMIT_STORAGE_URI  = "memory://"
    CORS_ORIGINS           = os.getenv("CORS_ORIGINS", "*").split(",")
    ANTHROPIC_API_KEY      = os.getenv("ANTHROPIC_API_KEY", "")
    CLAUDE_MODEL           = "claude-sonnet-4-20250514"
    CLAUDE_MAX_TOKENS      = 1024
    SESSION_TTL            = 3600

    UPLOAD_FOLDER = os.getenv(
        "UPLOAD_FOLDER",
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
    )

    @staticmethod
    def validate():
        errors = []
        if not Config.SECRET_KEY:
            errors.append("SECRET_KEY must be set in .env")
        if not Config.ANTHROPIC_API_KEY:
            errors.append("ANTHROPIC_API_KEY not set — AI features disabled")
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        return errors

class DevelopmentConfig(Config):
    DEBUG     = True
    FLASK_ENV = "development"

class ProductionConfig(Config):
    DEBUG = False

def get_config():
    env = os.getenv("FLASK_ENV", "production").lower()
    return DevelopmentConfig if env == "development" else ProductionConfig
