import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    PHOENIX_API_KEY: str = os.getenv("PHOENIX_API_KEY")
    PHOENIX_PROJECT_NAME: str = os.getenv("PHOENIX_PROJECT_NAME", "fuelyt-agent")
    PHOENIX_ENDPOINT: str = os.getenv("PHOENIX_ENDPOINT", "https://app.phoenix.arize.com/s/johnjazzinaro/v1/traces")

    def __init__(self):
        if not self.OPENAI_API_KEY:
            raise ValueError("Missing required environment variable: OPENAI_API_KEY")
        if not self.PHOENIX_API_KEY:
            raise ValueError("Missing required environment variable: PHOENIX_API_KEY")

settings = Settings()
