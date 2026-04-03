# agent/main.py — El Indio Blindado 3.2 🏹🛡️🦾✨
import os, logging, threading
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import PlainTextResponse
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s agentkit: %(message)s")
logger = logging.getLogger("agentkit")

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        from agent.memory import inicializar_db
        await inicializar_db()
        logger.info("📡 DB LISTA")
        
        # 🏹 EL ARREGLO FINAL: Importamos el Catalogo Re-bautizado
        def carga_pesada():
            try:
                import agent.catalogo as c
                c.actualizar_stock_indio()
                logger.info("✅ CATALOGO ONLINE")
            except Exception as e:
                logger.error(f"⚠️ Error en carga pesada: {e}")

        threading.Thread(target=carga_pesada, daemon=True).start()
    except Exception as e:
        logger.error(f"⚠️ Error en arranque: {e}")
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/webhook")
async def webhook_get(): return PlainTextResponse("ok")

@app.get("/")
async def health(): return {"status": "online"}

@app.post("/webhook")
async def webhook_post(r: Request, bt: BackgroundTasks):
    try:
        from agent.providers import obtener_proveedor
        from agent.brain import generar_respuesta
        from agent.memory import guardar_mensaje, obtener_historial
        
        body = await r.json()
        proveedor = obtener_proveedor()
        mensajes = await proveedor.parsear_webhook(raw_body=body)
        
        if mensajes:
            for msg in mensajes:
                if not msg.es_propio and msg.texto:
                    async def resp_async():
                        try:
                            h = await obtener_historial(msg.telefono)
                            txt = await generar_respuesta(msg.texto, h)
                            if await proveedor.enviar_mensaje(msg.telefono, txt):
                                await guardar_mensaje(msg.telefono, "user", msg.texto)
                                await guardar_mensaje(msg.telefono, "assistant", txt)
                        except: pass
                    bt.add_task(resp_async)
    except: pass
    return PlainTextResponse("ok")
