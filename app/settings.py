import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "")
WHATSAPP_API_VERSION = os.getenv("WHATSAPP_API_VERSION", "v23.0")

if not OPENAI_API_KEY:
    raise ValueError("Falta OPENAI_API_KEY en el archivo .env")