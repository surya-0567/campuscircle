from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://campuscircle:campuscircle_dev_pw@127.0.0.1:5432/campuscircle"
    jwt_secret: str = "dev_secret_change_me"
    jwt_algorithm: str = "HS256"
    jwt_expires_minutes: int = 10080  # 7 days
    client_origin: str = "*"
    admin_email: str = "admin@campuscircle.edu"
    admin_password: str = "Admin@12345"

    class Config:
        env_file = ".env"


settings = Settings()
