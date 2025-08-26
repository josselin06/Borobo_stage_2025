from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Paramètres de configuration chargés depuis les variables d'environnement.(elles sont sur le serveur)
    """
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    ALLOWED_ORIGINS: list[str]

    class Config:
        env_file = ".env"  # Charge automatiquement les variables depuis un fichier .env si présent

# Instance unique utilisée dans toute l'application
settings = Settings()
