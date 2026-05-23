from dotenv import load_dotenv
from os import getenv

load_dotenv()

class Config:
    BOT_TOKEN: str = getenv("BOT_TOKEN", "")
    GEMINI_API_KEY: str = getenv("GEMINI_API_KEY", "")

config = Config()
