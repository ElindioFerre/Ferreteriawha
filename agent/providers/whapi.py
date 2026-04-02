# agent/providers/whapi.py — Blindaje Nivel Industrial 🛡️🦾
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
                chat_id = msg.get("chat_id") or msg.get("to") or ""
                
                # 🏹 DETECCIÓN MULTI-CAPA
                # 1. Por banderas de Whapi
                es_propio = msg.get("from_me") or msg.get("fromMe") or msg.get("out") or False
                
                # 2. Por contenido del mensaje (Corta-bucle de emergencia)
                texto_body = ""
                if isinstance(msg.get("text"), dict):
                    texto_body = msg.get("text", {}).get("body", "").strip()
                
                # Si el mensaje dice "Aguantame un toque", es el bot. Punto.
                if "Aguantame un toque" in texto_body or "Dame un minutito" in texto_body:
                    es_propio = True

                if es_propio:
                    logger.info(f"🚫 [BUCLE EVITADO] Ignorando mensaje propio ID: {msg.get('id')}")

                mensajes.append(MensajeEntrante(
                    telefono=chat_id,
                    texto=texto_body,
                    mensaje_id=msg.get("id", ""),
                    es_propio=es_propio,
                ))
            return mensajes
        except Exception as e:
            logger.error(f"Error parseando Whapi: {e}")
            return []

    async def enviar_mensaje(self, telefono: str, mensaje: str) -> bool:
        if not self.token: return False
        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        payload = {"to": telefono, "body": mensaje, "typing_time": 0}
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                r = await client.post(self.url_envio, json=payload, headers=headers)
                return r.status_code in [200, 201]
        except Exception as e:
            logger.error(f"Error red: {e}")
            return False
