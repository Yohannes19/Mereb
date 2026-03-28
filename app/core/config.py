from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    SECRET_KEY: str = "dev-secret-key-change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    PBKDF2_ITERATIONS: int = 600000

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
