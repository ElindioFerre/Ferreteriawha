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
log_level = logging.DEBUG if os.getenv("ENVIRONMENT") == "development" else logging.INFO
logging.basicConfig(level=log_level, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("agentkit")
proveedor = obtener_proveedor()

async def procesar_mensaje_async(msg):
    try:
        if msg.es_propio or not msg.texto: return
        
        logger.info(f"Procesando en segundo plano mensaje de {msg.telefono}")
        historial = await obtener_historial(msg.telefono)
        
        # 1. Le pedimos la respuesta a la IA (ESTO YA FUNCIONA ✅)
        respuesta = await generar_respuesta(msg.texto, historial)
        
        # 2. ENVIAMOS PRIMERO (Prioridad máxima) 🚀
        enviado = await proveedor.enviar_mensaje(msg.telefono, respuesta)
        
        if enviado:
            logger.info(f"Respuesta enviada con éxito a {msg.telefono}")
            # 3. Guardamos todo recién cuando sabemos que salió
            await guardar_mensaje(msg.telefono, "user", msg.texto)
            await guardar_mensaje(msg.telefono, "assistant", respuesta)
        else:
            logger.error(f"Whapi rechazó el mensaje o hubo error de red para {msg.telefono}")
            
    except Exception as e:
        logger.error(f"Error crítico en proceso de {msg.telefono}: {e}", exc_info=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await inicializar_db()
    logger.info("Base de datos lista")
    yield

app = FastAPI(title="Ferreteria El Indio — WhatsApp Agent", version="1.0.1", lifespan=lifespan)

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
async def webhook_post(request: Request, background_tasks: BackgroundTasks):
    try:
        data = await request.json()
        logger.info(f"📥 WEBHOOK RECIBIDO: Keys={list(data.keys())}")
        
        mensajes = await proveedor.parsear_webhook(request)
        if not mensajes:
            logger.info("ℹ️ Webhook sin mensajes (posible status o lectura).")
            return {"status": "ok"}

        for msg in mensajes:
            logger.info(f"💬 Mensaje detectado de {msg.telefono}. Propio? {msg.es_propio}")
            if msg.es_propio or not msg.texto:
                continue
            
            logger.info(f"🚀 Disparando procesamiento para: {msg.texto[:20]}...")
            background_tasks.add_task(procesar_mensaje_async, msg)
        
        return {"status": "accepted"}
    except Exception as e:
        logger.error(f"❌ ERROR WEBHOOK: {e}", exc_info=True)
        return {"status": "error", "detail": str(e)}
