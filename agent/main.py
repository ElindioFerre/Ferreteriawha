# agent/main.py — El Indio Blindado 4.0 🏹🛡️🦾💎✨
import os, logging, threading, sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import PlainTextResponse
from dotenv import load_dotenv

# 🏹 AGREGAMOS LA RUTA AL MOTOR PARA QUE NO SE PIERDA
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s agentkit: %(message)s")
logger = logging.getLogger("agentkit")

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        from agent import memory as m
        await m.inicializar_db()
        logger.info("📡 DB LISTA")
        
        def carga_pesada():
            try:
                # 🔦 LINTERNA: Buscamos el catálogo por nombre completo
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
                        except Exception as e:
                            logger.error(f"Err proc: {e}")
                    bt.add_task(resp_async)
    except Exception as e:
        logger.error(f"Err global: {e}")
    return PlainTextResponse("ok")
