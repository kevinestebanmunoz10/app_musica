import os
from functools import lru_cache


class Settings:
    # Spotify
    SPOTIFY_CLIENT_ID: str = os.getenv("SPOTIFY_CLIENT_ID", "")
    SPOTIFY_CLIENT_SECRET: str = os.getenv("SPOTIFY_CLIENT_SECRET", "")
    SPOTIFY_REDIRECT_URI: str = os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:8000/auth/callback")

    # Base de datos
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./musica.db")

    # App
    APP_NAME: str = "App Musica Personal"
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"


@lru_cache
def get_settings() -> Settings:
    return Settings()
