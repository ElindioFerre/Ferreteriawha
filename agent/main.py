# agent/main.py — El Indio Blindado 3.3 🏹🛡️🦾⚡
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
        from . import memory as m # Importación de vecino
        await m.inicializar_db()
        logger.info("📡 DB LISTA")
        
        def carga_pesada():
            try:
                from . import catalogo as c # Importación de vecino
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
        from . import providers as p
        from . import brain as b
        from . import memory as m
        
        body = await r.json()
        proveedor = p.obtener_proveedor()
        mensajes = await proveedor.parsear_webhook(raw_body=body)
        
        if mensajes:
            for msg in mensajes:
                if not msg.es_propio and msg.texto:
                    async def resp_async():
                        try:
                            h = await m.obtener_historial(msg.telefono)
                            txt = await b.generar_respuesta(msg.texto, h)
                            if await proveedor.enviar_mensaje(msg.telefono, txt):
                                await m.guardar_mensaje(msg.telefono, "user", msg.texto)
                                await m.guardar_mensaje(msg.telefono, "assistant", txt)
                        except Exception as e:
                            logger.error(f"Err proc: {e}")
                    bt.add_task(resp_async)
    except Exception as e:
        logger.error(f"Err global: {e}")
    return PlainTextResponse("ok")
