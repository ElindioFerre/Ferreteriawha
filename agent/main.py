# agent/main.py — Versión Súper Veloz 🏹⚡
import os, logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import PlainTextResponse
from dotenv import load_dotenv
from agent.brain import generar_respuesta
from agent.memory import inicializar_db, guardar_mensaje, obtener_historial
from agent.providers import obtener_proveedor

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s agentkit: %(message)s")
logger = logging.getLogger("agentkit")
proveedor = obtener_proveedor()

async def procesar_mensaje_async(msg):
    try:
        if msg.es_propio or not msg.texto: return
        historial = await obtener_historial(msg.telefono)
        respuesta = await generar_respuesta(msg.texto, historial)
        if await proveedor.enviar_mensaje(msg.telefono, respuesta):
            await guardar_mensaje(msg.telefono, "user", msg.texto)
            await guardar_mensaje(msg.telefono, "assistant", respuesta)
    except Exception as e:
        logger.error(f"❌ Error: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    await inicializar_db()
    logger.info("📡 EL INDIO ESTÁ LISTO")
    yield

app = FastAPI(lifespan=lifespan)

# 🚀 VALIDACIÓN ULTRA RÁPIDA PARA WHAPI
@app.get("/webhook")
async def webhook_get(): 
    return PlainTextResponse("ok", status_code=200)

@app.post("/webhook")
async def webhook_post(r: Request, bt: BackgroundTasks):
    try:
        # Respondemos 'ok' al toque para evitar timeouts
        bt.add_task(procesar_webhook_inner, r)
    except: pass
    return PlainTextResponse("ok", status_code=200)

async def procesar_webhook_inner(request):
    try:
        mensajes = await proveedor.parsear_webhook(request)
        if mensajes:
            for msg in mensajes:
                if not msg.es_propio and msg.texto:
                    logger.info(f"📥 Mensaje de {msg.telefono}")
                    await procesar_mensaje_async(msg)
    except Exception as e:
        logger.error(f"Error webhook inner: {e}")

@app.get("/")
async def health(): return {"status": "ok"}
