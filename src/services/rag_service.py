from openai import OpenAI

from src.config import settings


SYSTEM_PROMPT = (
    "You are a Swiss regulatory compliance advisor. Answer with precise, "
    "source-grounded guidance and call out uncertainty when context is missing."
)


def get_openai_client() -> OpenAI:
    return OpenAI(api_key=settings.openai_api_key)
