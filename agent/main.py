# agent/main.py — Versión FINAL LIMPIA 🏹🦾✨
import os, logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import PlainTextResponse
from dotenv import load_dotenv
from agent.brain import generar_respuesta
from agent.memory import inicializar_db, guardar_mensaje, obtener_historial
from agent.providers import obtener_proveedor

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] agentkit: %(message)s")
logger = logging.getLogger("agentkit")
proveedor = obtener_proveedor()

async def procesar_mensaje_async(msg):
    try:
        historial = await obtener_historial(msg.telefono)
        respuesta = await generar_respuesta(msg.texto, historial)
        if await proveedor.enviar_mensaje(msg.telefono, respuesta):
            await guardar_mensaje(msg.telefono, "user", msg.texto)
            await guardar_mensaje(msg.telefono, "assistant", respuesta)
    except Exception as e:
        logger.error(f"❌ Error en proceso: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    await inicializar_db()
    logger.info("📡 AGENTE EL INDIO ONLINE Y LISTO")
    yield

app = FastAPI(title="Ferreteria El Indio", lifespan=lifespan)

@app.get("/")
async def health(): return {"status": "online"}

@app.get("/webhook")
async def webhook_get(r: Request):
    res = await proveedor.validar_webhook(r)
    return PlainTextResponse(str(res)) if res is not None else {"status": "ok"}

@app.post("/webhook")
async def webhook_post(r: Request, bt: BackgroundTasks):
    mensajes = await proveedor.parsear_webhook(r)
    for msg in mensajes:
        if not msg.es_propio and msg.texto:
            logger.info(f"📥 Mensaje de {msg.telefono}: {msg.texto[:20]}")
            bt.add_task(procesar_mensaje_async, msg)
    return {"status": "accepted"}
