from google import genai
from google.genai import types
from credentials import config


class ChatGeminiService:
    def __init__(self):
        self.client = genai.Client(api_key=config.GEMINI_API_KEY)
        self.chat = None
        self.system_prompt = None

    async def add_message(self, message_text: str) -> str:
        if self.chat is None:
            config_obj = types.GenerateContentConfig(
                system_instruction=self.system_prompt if self.system_prompt else None,
                temperature=1.0
            )
            self.chat = self.client.aio.chats.create(
                model='gemini-2.5-flash',
                config=config_obj
            )

        response = await self.chat.send_message(message_text)
        return response.text

    async def send_message_list(self) -> str:
        if self.chat is None:
            config_obj = types.GenerateContentConfig(
                system_instruction=self.system_prompt if self.system_prompt else None,
                temperature=1.0
            )
            self.chat = self.client.aio.chats.create(
                model='gemini-2.5-flash',
                config=config_obj
            )

        response = await self.chat.send_message("")
        return response.text

    def set_prompt(self, prompt_text: str) -> None:
        self.system_prompt = prompt_text
        self.chat = None

    async def send_question(self, prompt_text: str, message_text: str) -> str:
        config_obj = types.GenerateContentConfig(
            system_instruction=prompt_text,
            temperature=1.0
        )

        response = await self.client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents=message_text,
            config=config_obj
        )
        return response.text