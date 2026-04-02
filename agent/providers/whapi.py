# agent/providers/whapi.py — Adaptador Blindado 🏹🦾
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
            
            # Whapi manda los mensajes en una lista llamada 'messages'
            for msg in body.get("messages", []):
                chat_id = msg.get("chat_id") or msg.get("to") or ""
                
                # 🏹 DETECTOR DE ORIGEN ROBUSTO
                # Miramos todas las formas posibles en que Whapi nos dice que el mensaje es nuestro
                es_propio = msg.get("from_me", msg.get("fromMe", False))
                
                # Algunos webhooks vienen con el campo 'from_me' pero 'messages' vacío
                # Si el mensaje no trae texto real o dice que salió de nosotros, lo marcamos
                texto_body = ""
                if isinstance(msg.get("text"), dict):
                    texto_body = msg.get("text", {}).get("body", "")
                
                if es_propio:
                    logger.info(f"🚫 Mensaje SALIENTE (id: {msg.get('id')}) detectado. Ignorando para evitar bucle.")

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
        if not self.token:
            logger.warning("¡ALERTA! WHAPI_TOKEN no está configurado")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.token}", 
            "Content-Type": "application/json"
        }
        
        payload = {
            "to": telefono, 
            "body": mensaje,
            "typing_time": 0
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                r = await client.post(self.url_envio, json=payload, headers=headers)
                if r.status_code in [200, 201]:
                    return True
                logger.error(f"Error Whapi ({r.status_code}): {r.text}")
                return False
        except Exception as e:
            logger.error(f"Error de red Whapi: {e}")
            return False
