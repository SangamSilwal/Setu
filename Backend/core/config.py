from pydantic_settings import BaseSettings , SettingsConfigDict 
from functools import lru_cache

class Settings(BaseSettings):

    #MongoDB 
    mongodb_url: str 
    database_name: str
    secret_key: str 
    access_token_expire_minutes: int 
    algorithm: str
    frontend_url: str

    ## To get all the values 
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()