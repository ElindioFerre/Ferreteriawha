# agent/main.py — Servidor FastAPI + Webhook WhatsApp
import os, logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
from dotenv import load_dotenv
from agent.brain import generar_respuesta
from agent.memory import inicializar_db, guardar_mensaje, obtener_historial
from agent.providers import obtener_proveedor

load_dotenv()
log_level = logging.DEBUG if os.getenv("ENVIRONMENT") == "development" else logging.INFO
logging.basicConfig(level=log_level, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("agentkit")
proveedor = obtener_proveedor()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await inicializar_db()
    logger.info("Base de datos lista")
    logger.info(f"Proveedor: {proveedor.__class__.__name__}")
    yield

app = FastAPI(title="Ferreteria El Indio — WhatsApp Agent", version="1.0.0", lifespan=lifespan)

@app.get("/")
async def health():
    return {"status": "ok", "agente": "Ferreteria El Indio Agent"}

@app.get("/webhook")
async def webhook_get(request: Request):
    resultado = await proveedor.validar_webhook(request)
    if resultado is not None:
        return PlainTextResponse(str(resultado))
    return {"status": "ok"}

@app.post("/webhook")
async def webhook_post(request: Request):
    try:
        mensajes = await proveedor.parsear_webhook(request)
        for msg in mensajes:
            if msg.es_propio or not msg.texto:
                continue
            logger.info(f"Mensaje de {msg.telefono}: {msg.texto[:60]}")
            historial = await obtener_historial(msg.telefono)
            respuesta = await generar_respuesta(msg.texto, historial)
            await guardar_mensaje(msg.telefono, "user", msg.texto)
            await guardar_mensaje(msg.telefono, "assistant", respuesta)
            enviado = await proveedor.enviar_mensaje(msg.telefono, respuesta)
            if enviado:
                logger.info(f"Respuesta enviada a {msg.telefono}")
            else:
                logger.warning(f"No se pudo enviar a {msg.telefono}")
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error webhook: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
