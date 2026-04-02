# agent/main.py — Ajuste de orden de envío 🏹
import os, logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import PlainTextResponse
from dotenv import load_dotenv
from agent.brain import generar_respuesta
from agent.memory import inicializar_db, guardar_mensaje, obtener_historial
from agent.providers import obtener_proveedor

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("agentkit")
proveedor = obtener_proveedor()

async def procesar_mensaje_async(msg):
    try:
        if msg.es_propio or not msg.texto: return
        
        # 1. Buscamos historial
        historial = await obtener_historial(msg.telefono)
        
        # 2. Le pedimos la respuesta a la IA (ESTO YA FUNCIONA ✅)
        respuesta = await generar_respuesta(msg.texto, historial)
        
        # 3. ENVIAMOS PRIMERO (Prioridad máxima) 🚀
        enviado = await proveedor.enviar_mensaje(msg.telefono, respuesta)
        
        if enviado:
            logger.info(f"Respuesta enviada a {msg.telefono}")
            # 4. Guardamos todo recién cuando sabemos que salió
            await guardar_mensaje(msg.telefono, "user", msg.texto)
            await guardar_mensaje(msg.telefono, "assistant", respuesta)
        else:
            logger.error(f"Whapi rechazó el mensaje para {msg.telefono}")
            
    except Exception as e:
        logger.error(f"Error crítico en proceso: {e}", exc_info=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await inicializar_db()
    yield

app = FastAPI(title="Ferreteria El Indio", lifespan=lifespan)

@app.get("/")
async def health(): return {"status": "ok"}

@app.get("/webhook")
async def webhook_get(request: Request):
    res = await proveedor.validar_webhook(request)
    return PlainTextResponse(str(res)) if res else {"status": "ok"}

@app.post("/webhook")
async def webhook_post(request: Request, background_tasks: BackgroundTasks):
    try:
        mensajes = await proveedor.parsear_webhook(request)
        for msg in mensajes:
            background_tasks.add_task(procesar_mensaje_async, msg)
        return {"status": "accepted"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
