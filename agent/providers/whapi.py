# agent/providers/whapi.py — Versión Indio 10.0 (Oídos y Sentido Común) 🏹🎙️🤫🦾
import os, httpx, logging

logger = logging.getLogger("agentkit")

class MensajeWhapi:
    def __init__(self, telefono, texto, id_mensaje, es_propio=False):
        self.telefono = telefono
        self.texto = texto
        self.id_mensaje = id_mensaje
        self.es_propio = es_propio

class ProveedorWhapi:
    def __init__(self):
        self.url_base = "https://gate.whapi.cloud"
        self.token = os.getenv("WHAPI_TOKEN")

    async def validar_webhook(self, request): return "ok"

    async def parsear_webhook(self, request=None, raw_body=None):
        try:
            datos = raw_body if raw_body is not None else await request.json()
            mensajes_obj = []
            if not datos or "messages" not in datos: return []
            
            for m in datos["messages"]:
                tipo = m.get("type", "text")
                de_mi = m.get("from_me", False)
                chat_id = m.get("chat_id", "")
                msg_id = m.get("id", "")
                
                # 🎙️ DETECCIÓN DE AUDIO
                if tipo in ["voice", "audio"]:
                    # Whapi manda el link de descarga en el objeto del audio
                    media = m.get("voice", {}) or m.get("audio", {})
                    link = media.get("link", "")
                    if link:
                        texto_audio = f"[AUDIO_LINK:{link}]"
                        mensajes_obj.append(MensajeWhapi(chat_id, texto_audio, msg_id, de_mi))
                        logger.info(f"🎙️ Audio recibido de {chat_id}")
                
                # 📝 DETECCIÓN DE TEXTO
                elif tipo == "text":
                    texto = m.get("text", {}).get("body", "")
                    mensajes_obj.append(MensajeWhapi(chat_id, texto, msg_id, de_mi))
                    if de_mi:
                        logger.info(f"🕵️‍♂️ Dante respondió en el chat de {chat_id}")
                    else:
                        logger.info(f"📥 Mensaje de {chat_id}: {texto[:30]}...")

            return mensajes_obj
        except Exception as e:
            logger.error(f"Error parseando Whapi 10.0: {e}")
            return []

    async def enviar_mensaje(self, telefono, texto):
        try:
            url = f"{self.url_base}/messages/text"
            destinatario = telefono.split("@")[0]
            payload = {"to": destinatario, "body": texto}
            headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
            
            async with httpx.AsyncClient() as client:
                resp = await client.post(url, json=payload, headers=headers)
                logger.info(f"📤 Enviando a {destinatario} | Status: {resp.status_code}")
                return resp.status_code == 200
        except Exception as e:
            logger.error(f"Error enviando: {e}")
            return False
