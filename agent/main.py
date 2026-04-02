# agent/main.py — Con más visibilidad 🏹🕵️‍♂️⚡
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
        logger.info(f"🧠 Empezando a procesar mensaje de {msg.telefono}")
        
        logger.info("📚 Buscando historial...")
        historial = await obtener_historial(msg.telefono)
        
        logger.info("🤖 Llamando a la IA (con modelos Async)...")
        respuesta = await generar_respuesta(msg.texto, historial)
        
        logger.info(f"📤 Enviando respuesta a {msg.telefono}...")
        enviado = await proveedor.enviar_mensaje(msg.telefono, respuesta)
        
        if enviado:
            logger.info("✨ CICLO COMPLETADO CON ÉXITO")
            await guardar_mensaje(msg.telefono, "user", msg.texto)
            await guardar_mensaje(msg.telefono, "assistant", respuesta)
        else:
            logger.error(f"❌ FALLÓ EL ENVÍO FINAL a {msg.telefono}")
            
    except Exception as e:
        logger.error(f"❌ ERROR EN CICLO: {e}", exc_info=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await inicializar_db()
    logger.info("📡 EL INDIO ESTÁ LISTO")
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/webhook")
async def webhook_get(): 
    return PlainTextResponse("ok")

@app.post("/webhook")
async def webhook_post(r: Request, bt: BackgroundTasks):
    try:
        body = await r.json()
        mensajes = await proveedor.parsear_webhook(raw_body=body)
        if mensajes:
            for msg in mensajes:
                if not msg.es_propio and msg.texto:
                    logger.info(f"📥 MENSAJE ENTRANTE: {msg.telefono}")
                    bt.add_task(procesar_mensaje_async, msg)
    except Exception as e:
        logger.error(f"Error webhook: {e}")
    
    return PlainTextResponse("ok")

@app.get("/")
async def health(): return {"status": "ok"}
