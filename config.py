import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from backend root
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings:
    PORT: int = int(os.getenv("PORT", "8080"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./tripwise.db")
    DB_PATH: str = str(BASE_DIR / "tripwise.db")

    JWT_SECRET: str = os.getenv(
        "JWT_SECRET",
        "tripwise_super_secure_jwt_secret_token_key_change_in_production_32chars!"
    )
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRATION_MINUTES: int = int(os.getenv("JWT_EXPIRATION_MINUTES", "1440"))

    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEOAPIFY_API_KEY: str = os.getenv("GEOAPIFY_API_KEY", "")
    NEWS_API_KEY: str = os.getenv("NEWS_API_KEY", "")

    PAYMENT_KEY_ID: str = os.getenv("PAYMENT_KEY_ID", "rzp_test_tripwise_mock_id")
    PAYMENT_KEY_SECRET: str = os.getenv("PAYMENT_KEY_SECRET", "rzp_test_tripwise_mock_secret")

    CACHE_TTL_SECONDS: int = int(os.getenv("CACHE_TTL_SECONDS", "1800"))

settings = Settings()
