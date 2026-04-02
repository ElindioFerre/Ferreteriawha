# agent/main.py — El Corazón del Indio (Con Espionaje) 🏹🕵️‍♂️
import os, logging
import google.generativeai as genai
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import PlainTextResponse
from dotenv import load_dotenv
from agent.brain import generar_respuesta
from agent.memory import inicializar_db, guardar_mensaje, obtener_historial
from agent.providers import obtener_proveedor

# 1. Configuración de Logs y Entorno
load_dotenv()
log_level = logging.INFO
logging.basicConfig(level=log_level, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("agentkit")

# 2. Inicializar Proveedor
proveedor = obtener_proveedor()

# 3. Lógica de Procesamiento Asíncrono
async def procesar_mensaje_async(msg):
    try:
        if msg.es_propio or not msg.texto: return
        
        logger.info(f"🚀 PROCESANDO MENSAJE de {msg.telefono}")
        historial = await obtener_historial(msg.telefono)
        
        respuesta = await generar_respuesta(msg.texto, historial)
        enviado = await proveedor.enviar_mensaje(msg.telefono, respuesta)
        
        if enviado:
            logger.info(f"✅ RESPUESTA ENVIADA a {msg.telefono}")
            await guardar_mensaje(msg.telefono, "user", msg.texto)
            await guardar_mensaje(msg.telefono, "assistant", respuesta)
        else:
            logger.error(f"❌ FALLO EL ENVÍO a {msg.telefono}")
            
    except Exception as e:
        logger.error(f"❌ ERROR CRÍTICO: {e}", exc_info=True)

# 4. Configuración de la App (FastAPI)
@asynccontextmanager
async def lifespan(app: FastAPI):
    await inicializar_db()
    
    # 🕵️‍♂️ ESPIONAJE DE MODELOS
    try:
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        available_models = [m.name for m in genai.list_models()]
        logger.info(f"🔍 MODELOS DISPONIBLES EN TU CUENTA: {available_models}")
    except Exception as e:
        logger.error(f"❌ No pude listar los modelos: {e}")

    logger.info("📡 BASE DE DATOS Y AGENTE INICIALIZADOS")
    yield

app = FastAPI(title="Ferreteria El Indio Agent", lifespan=lifespan)

# 5. Endpoints (Rutas)
@app.get("/")
async def health():
    return {"status": "ok", "agente": "Ferreteria El Indio"}

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
        if not mensajes:
            return {"status": "ok"}

        for msg in mensajes:
            if msg.es_propio or not msg.texto:
                continue
            
            logger.info(f"📥 MENSAJE RECIBIDO de {msg.telefono}: {msg.texto[:30]}...")
            background_tasks.add_task(procesar_mensaje_async, msg)
        
        return {"status": "accepted"}
    except Exception as e:
        logger.error(f"❌ ERROR WEBHOOK: {e}", exc_info=True)
        return {"status": "error"}
