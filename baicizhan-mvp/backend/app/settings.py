from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "mysql+pymysql://bcz:bczpass@localhost:3306/baicizhan?charset=utf8mb4"
    cors_origins: str = "http://localhost:5173"
    seed_on_startup: bool = True


settings = Settings()
