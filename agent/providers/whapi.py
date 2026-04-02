# agent/providers/whapi.py — Adaptador para Whapi.cloud 🏹
import os, logging, httpx
from fastapi import Request
from agent.providers.base import ProveedorWhatsApp, MensajeEntrante

logger = logging.getLogger("agentkit")

class ProveedorWhapi(ProveedorWhatsApp):
    def __init__(self):
        self.token = os.getenv("WHAPI_TOKEN")
        self.url_envio = "https://gate.whapi.cloud/messages/text"

    async def parsear_webhook(self, request: Request) -> list[MensajeEntrante]:
        try:
            body = await request.json()
            mensajes = []
            for msg in body.get("messages", []):
                mensajes.append(MensajeEntrante(
                    telefono=msg.get("chat_id", ""),
                    texto=msg.get("text", {}).get("body", "") if isinstance(msg.get("text"), dict) else "",
                    mensaje_id=msg.get("id", ""),
                    es_propio=msg.get("from_me", False),
                ))
            return mensajes
        except: return []

    async def enviar_mensaje(self, telefono: str, mensaje: str) -> bool:
        if not self.token: return False
        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        payload = {"to": telefono, "body": mensaje}
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                r = await client.post(self.url_envio, json=payload, headers=headers)
                return r.status_code in [200, 201]
        except: return False
