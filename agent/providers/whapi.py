# agent/providers/whapi.py — Versión Indio 11.0 (OJOS Y CARRO) 🏹📸🎙️🤫🦾
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
                
                # 🎙️ AUDIO
                if tipo in ["voice", "audio"]:
                    media = m.get("voice", {}) or m.get("audio", {})
                    link = media.get("link", "")
                    if link:
                        mensajes_obj.append(MensajeWhapi(chat_id, f"[AUDIO_LINK:{link}]", msg_id, de_mi))
                
                # 📸 IMAGEN (OJOS)
                elif tipo == "image":
                    link = m.get("image", {}).get("link", "")
                    if link:
                        mensajes_obj.append(MensajeWhapi(chat_id, f"[IMAGE_LINK:{link}]", msg_id, de_mi))
                        logger.info(f"📸 Foto recibida de {chat_id}")
                
                # 📝 TEXTO
                elif tipo == "text":
                    texto = m.get("text", {}).get("body", "")
                    mensajes_obj.append(MensajeWhapi(chat_id, texto, msg_id, de_mi))

            return mensajes_obj
        except Exception as e:
            logger.error(f"Error Whapi 11.0: {e}")
            return []

    async def enviar_mensaje(self, telefono, texto):
        try:
            url = f"{self.url_base}/messages/text"
            destinatario = telefono.split("@")[0]
            payload = {"to": destinatario, "body": texto}
            headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
            async with httpx.AsyncClient() as client:
                resp = await client.post(url, json=payload, headers=headers)
                return resp.status_code == 200
        except: return False
