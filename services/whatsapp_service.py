import requests

from app.settings import (
    WHATSAPP_TOKEN,
    WHATSAPP_PHONE_NUMBER_ID,
    WHATSAPP_API_VERSION,
)


class WhatsAppService:
    def __init__(self):
        self.base_url = (
            f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/"
            f"{WHATSAPP_PHONE_NUMBER_ID}/messages"
        )
        self.headers = {
            "Authorization": f"Bearer {WHATSAPP_TOKEN}",
            "Content-Type": "application/json",
        }

    def send_text_message(self, to: str, body: str) -> dict:
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {
                "body": body[:4096]
            },
        }

        response = requests.post(
            self.base_url,
            headers=self.headers,
            json=payload,
            timeout=30,
        )

        print("STATUS:", response.status_code)
        print("RESPUESTA META:", response.text)

        response.raise_for_status()
        return response.json()