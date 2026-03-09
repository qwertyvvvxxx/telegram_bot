from dotenv import load_dotenv
from os import getenv


load_dotenv()



class Config:
    BOT_TOKEN: str = getenv("BOT_TOKEN")
    GPT_API_KEY: str = getenv("GPT_API_KEY")

config = Config()
