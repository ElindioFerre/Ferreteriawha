# agent/main.py — Servidor FastAPI con Background Tasks 🏹
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

# TAREA EN SEGUNDO PLANO: Para que Whapi no espere a la IA
async def procesar_mensaje_async(msg):
    try:
        if msg.es_propio or not msg.texto: return
        
        logger.info(f"Procesando en segundo plano mensaje de {msg.telefono}")
        historial = await obtener_historial(msg.telefono)
        
        # Hablamos con la IA
        respuesta = await generar_respuesta(msg.texto, historial)
        
        # Guardamos y enviamos la respuesta
        await guardar_mensaje(msg.telefono, "user", msg.texto)
        await guardar_mensaje(msg.telefono, "assistant", respuesta)
        
        enviado = await proveedor.enviar_mensaje(msg.telefono, respuesta)
        if enviado:
            logger.info(f"Respuesta enviada con éxito a {msg.telefono}")
        else:
            logger.warning(f"No se pudo enviar respuesta a {msg.telefono}")
            
    except Exception as e:
        logger.error(f"Error procesando mensaje de {msg.telefono}: {e}", exc_info=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await inicializar_db()
    logger.info("Base de datos lista")
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
async def webhook_post(request: Request, background_tasks: BackgroundTasks):
    try:
        mensajes = await proveedor.parsear_webhook(request)
        for msg in mensajes:
            if msg.es_propio or not msg.texto:
                continue
            # Mandamos la tarea a la cola y respondemos OK rápido
            background_tasks.add_task(procesar_mensaje_async, msg)
        
        return {"status": "accepted"} # Whapi recibe esto al toque
    except Exception as e:
        logger.error(f"Error webhook: {e}")
        return {"status": "error", "detail": str(e)}
