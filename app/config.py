from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_username: str
    database_password: str
    database_name: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    razorpay_key_id: str
    razorpay_key_secret: str
    razorpay_webhook_secret: str

    model_config = ConfigDict(env_file = ".env")
    
settings = Settings()