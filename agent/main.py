# agent/main.py — Versión DEFINITIVA (Sin errores de segundo plano) 🏹🦾⚡
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
        historial = await obtener_historial(msg.telefono)
        respuesta = await generar_respuesta(msg.texto, historial)
        if await proveedor.enviar_mensaje(msg.telefono, respuesta):
            await guardar_mensaje(msg.telefono, "user", msg.texto)
            await guardar_mensaje(msg.telefono, "assistant", respuesta)
    except Exception as e:
        logger.error(f"❌ Error proceso: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    await inicializar_db()
    logger.info("📡 EL INDIO ESTÁ LISTO")
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/webhook")
async def webhook_get(): 
    return PlainTextResponse("ok", status_code=200)

@app.post("/webhook")
async def webhook_post(r: Request, bt: BackgroundTasks):
    try:
        # 🏹 LEEMOS EL JSON ACÁ (Obligatorio antes de responder 200 OK)
        body = await r.json()
        mensajes = await proveedor.parsear_webhook_manual(body) # Nueva función manual
        
        if mensajes:
            for msg in mensajes:
                if not msg.es_propio and msg.texto:
                    logger.info(f"📥 MSG de {msg.telefono}")
                    bt.add_task(procesar_mensaje_async, msg)
    except Exception as e:
        logger.error(f"Error webhook: {e}")
    
    return PlainTextResponse("ok", status_code=200)

@app.get("/")
async def health(): return {"status": "ok"}

