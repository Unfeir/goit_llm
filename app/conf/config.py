from dotenv import find_dotenv
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

dotenv_path = find_dotenv(filename='.env', raise_error_if_not_found=False, usecwd=True)


class Settings(BaseSettings):
    uvicorn_host: str = 'address'
    uvicorn_port: int = 0
    postgres_db: str = 'db_name'
    postgres_user: str = 'user'
    postgres_password: str = 'password'
    postgres_host: str = 'POSTGRES_HOST'
    postgres_port: int = 0
    sqlalchemy_database_url: str = 'address'
    cloudinary_name: str = 'name'
    cloudinary_api_key: int = 1
    cloudinary_api_secret: str = 'secret'
    secret_key: str = 'secretkey'
    algorithm: str = 'algorithm'
    access_token_timer: int = 60
    audience: str = 'auth0 url'
    client_id: str = 'auth0 client_id'
    domain: str = 'auth0 domain'
    auth0_algorithm: str = 'algorithm type'
    kid: str = 'key'

    # model_config = ConfigDict(extra='forbid')
    model_config = SettingsConfigDict(env_file=dotenv_path, extra='forbid')


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
