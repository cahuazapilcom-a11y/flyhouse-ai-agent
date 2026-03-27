import traceback
import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, PlainTextResponse

from app.router import AgentRouter
from app.settings import WHATSAPP_VERIFY_TOKEN
from services.whatsapp_service import WhatsAppService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="FLYHOUSE AI AGENT - WhatsApp Webhook")

router = AgentRouter()
whatsapp = WhatsAppService()

AUTHORIZED_USERS = {
    "51918156548": {"name": "Moises", "role": "admin"},
    "51977745422": {"name": "RRHH", "role": "rrhh"},
    "51999999999": {"name": "Supervisor", "role": "supervisor"},
}

ROLE_PERMISSIONS = {
    "admin": ["rrhh", "logistica", "finanzas", "proyectos", "comercial", "supervisor"],
    "supervisor": ["rrhh", "logistica", "finanzas", "proyectos", "comercial", "supervisor"],
    "rrhh": ["rrhh"],
    "logistica": ["logistica"],
    "finanzas": ["finanzas"],
    "proyectos": ["proyectos"],
    "comercial": ["comercial"],
    "trabajador": ["supervisor"],
}


@app.get("/")
async def root():
    return {"message": "FLYHOUSE AI AGENT webhook activo"}


@app.get("/webhook")
async def verify_webhook(request: Request):
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == WHATSAPP_VERIFY_TOKEN:
        return PlainTextResponse(content=challenge, status_code=200)

    raise HTTPException(status_code=403, detail="Verify token inválido")


@app.post("/webhook")
async def receive_webhook(request: Request):
    body = await request.json()

    try:
        entries = body.get("entry", [])

        for entry in entries:
            changes = entry.get("changes", [])

            for change in changes:
                value = change.get("value", {})
                messages = value.get("messages", [])

                if not messages:
                    # Meta envía notificaciones de estado (leído, entregado)
                    # que no tienen mensajes — ignorar silenciosamente
                    continue

                for msg in messages:
                    from_number = msg.get("from")
                    msg_type = msg.get("type")

                    if not from_number:
                        continue

                    user_text = extract_message_text(msg, msg_type)
                    if not user_text:
                        logger.info(f"[SKIP] Mensaje tipo '{msg_type}' sin texto de {from_number}")
                        continue

                    from_number = normalize_phone(from_number)
                    logger.info(f"[MSG] De: {from_number} | Texto: {user_text}")

                    user_info = AUTHORIZED_USERS.get(from_number)
                    if not user_info:
                        logger.info(f"[DENIED] Número no autorizado: {from_number}")
                        whatsapp.send_text_message(
                            from_number,
                            "Acceso no autorizado. Comunícate con el administrador del sistema."
                        )
                        continue

                    user_role = user_info["role"]
                    user_name = user_info["name"]

                    detected_area = router.detect_area(user_text)
                    logger.info(f"[AREA] Detectada: {detected_area} para rol: {user_role}")

                    allowed_areas = ROLE_PERMISSIONS.get(user_role, [])
                    if detected_area not in allowed_areas:
                        whatsapp.send_text_message(
                            from_number,
                            build_permission_denied_message(
                                user_name=user_name,
                                role=user_role,
                                detected_area=detected_area,
                            )
                        )
                        continue

                    area, response = router.route(user_text)
                    logger.info(f"[RESPONSE] Área: {area} | Respuesta generada OK")

                    final_text = (
                        f"👤 {user_name} ({user_role})\n"
                        f"📂 Área: {area}\n\n"
                        f"{response}"
                    )

                    whatsapp.send_text_message(from_number, final_text)

        return JSONResponse(content={"status": "ok"}, status_code=200)

    except Exception as e:
        # ✅ Siempre retornar 200 a Meta para evitar reintentos
        logger.error(f"❌ ERROR EN WEBHOOK: {e}")
        logger.error(traceback.format_exc())
        return JSONResponse(content={"status": "ok"}, status_code=200)


def extract_message_text(message: dict, msg_type: str) -> str:
    if msg_type == "text":
        return message.get("text", {}).get("body", "").strip()
    if msg_type == "interactive":
        interactive = message.get("interactive", {})
        button_reply = interactive.get("button_reply")
        if button_reply:
            return button_reply.get("title", "").strip()
        list_reply = interactive.get("list_reply")
        if list_reply:
            return list_reply.get("title", "").strip()
    return ""


def normalize_phone(phone: str) -> str:
    return "".join(ch for ch in phone if ch.isdigit())


def build_permission_denied_message(user_name: str, role: str, detected_area: str) -> str:
    return (
        f"Hola {user_name}, tu rol actual es *{role}* y no tiene permiso "
        f"para acceder al área *{detected_area}*.\n\n"
        f"Si necesitas acceso, solicita autorización al administrador."
    )
```

---

## ✅ Después de hacer el cambio

1. **Sube el código** a tu repositorio → Render redesplegará automáticamente
2. **Envía un mensaje** desde tu WhatsApp al número de prueba
3. **Revisa los logs** en Render — ahora verás líneas como:
```
[MSG] De: 51918156548 | Texto: hola
[AREA] Detectada: rrhh para rol: admin
[RESPONSE] Área: rrhh | Respuesta generada OK
