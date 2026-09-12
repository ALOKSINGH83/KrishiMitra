from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = ""
    supabase_url: str = ""
    supabase_jwks_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    supabase_jwt_issuer: str = ""
    supabase_jwt_audience: str = "authenticated"
    weather_provider_key: str = ""
    market_provider_key: str = ""
    llm_api_key: str = ""
    embedding_model: str = ""
    cors_origins: list[str] = ["http://localhost:5173"]
    sentry_dsn: str = ""
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
