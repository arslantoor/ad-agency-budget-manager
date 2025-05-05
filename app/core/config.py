import os
from dotenv import load_dotenv

load_dotenv()
class Settings:
    PROJECT_NAME: str = "Ad Agency"
    VERSION: str = "1.0.0"
    DATABASE_URL: str = os.getenv("DATABASE_URL")

settings = Settings()