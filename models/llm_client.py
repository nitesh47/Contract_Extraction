import logging
import os
from pydantic import BaseModel
from openai import AsyncOpenAI
from dotenv import load_dotenv
load_dotenv()


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL")
TEMPERATURE = float(os.getenv("TEMPERATURE"))

log = logging.getLogger(__name__)

class ChatMessage(BaseModel):
    role: str
    content: str

class LLMClient:
    def __init__(self, model: str = DEFAULT_MODEL):
        self.model = model
        self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.client.close()

    async def chat_completion(self, messages: list[ChatMessage]) -> str:
        formatted_messages = [m.model_dump() for m in messages]
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=formatted_messages,
            temperature=TEMPERATURE,
        )
        return response.choices[0].message.content
