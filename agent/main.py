# agent/main.py — El Indio Blindado v2.0 🏹🛡️🦾⚡
import os, logging, threading
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import PlainTextResponse
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s agentkit: %(message)s")
logger = logging.getLogger("agentkit")

# 🚀 PASO 1: DEFINICIÓN INMEDIATA DEL APP (Para que Railway lo vea de una)
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # Importamos las piezas pesadas ADENTRO del arranque
        from agent.memory import inicializar_db
        from agent.tools import sincronizar_catalogo
        
        await inicializar_db()
        logger.info("📡 BASE DE MENSAJES LISTA")
        
        # Sincronismo en segundo plano
        threading.Thread(target=sincronizar_catalogo, daemon=True).start()
    except Exception as e:
        logger.error(f"⚠️ Error en arranque: {e}")
    yield

app = FastAPI(lifespan=lifespan)

# 🚀 PASO 2: LOS ENDPOINTS RÁPIDOS
@app.get("/webhook")
async def webhook_get(): return PlainTextResponse("ok")

@app.get("/")
async def health(): return {"status": "online"}

# 🚀 PASO 3: LÓGICA DE PROCESAMIENTO
@app.post("/webhook")
async def webhook_post(r: Request, bt: BackgroundTasks):
    try:
        # Importamos el resto acá para no clavar el arranque inicial
        from agent.providers import obtener_proveedor
        from agent.brain import generar_respuesta
        from agent.memory import guardar_mensaje, obtener_historial
        
        body = await r.json()
        proveedor = obtener_proveedor()
        mensajes = await proveedor.parsear_webhook(raw_body=body)
        
        if mensajes:
            for msg in mensajes:
                if not msg.es_propio and msg.texto:
                    async def responder():
                        try:
                            hist = await obtener_historial(msg.telefono)
                            resp = await generar_respuesta(msg.texto, hist)
                            if await proveedor.enviar_mensaje(msg.telefono, resp):
                                await guardar_mensaje(msg.telefono, "user", msg.texto)
                                await guardar_mensaje(msg.telefono, "assistant", resp)
                        except: pass
                    
                    bt.add_task(responder)
    except: pass
    return PlainTextResponse("ok")
