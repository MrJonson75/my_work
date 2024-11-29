import os
from dotenv import load_dotenv

from pathlib import Path

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)


class Settings:
    PROJECT_NAME: str = "Post MrJonson"
    PROJECT_VERSION: str = "0.0.1"
    DATABASE_URL = "sqlite:///./sql_app.db"
    SECRET_KEY: str = "supersecretkeyhere"  # os.getenv("SECRET_KEY")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30


settings = Settings()
