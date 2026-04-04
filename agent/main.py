# agent/main.py — El Indio 11.8 (MULTIMODAL Y SILENCIO) 🏹🛰️🦾💎✨🦾
import os, logging, threading, sqlite3, requests, datetime, asyncio, time, httpx
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse, JSONResponse
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s agentkit: %(message)s")
logger = logging.getLogger("agentkit")

DB_PATH = os.path.join("knowledge", "catalogo.db")

# 🤫 GESTOR DE SILENCIO Y BÚFER
message_buffer = {} 
silence_timers = {} 
buffer_lock = asyncio.Lock()

def sincronizar_bunker():
    try:
        url = "https://ferreteriaelindio.netlify.app/data.json"
        r = requests.get(url, timeout=30)
        if r.status_code == 200:
            productos = r.json()
            conn = sqlite3.connect(DB_PATH); c = conn.cursor()
            c.execute("DROP TABLE IF EXISTS productos")
            c.execute("CREATE TABLE productos (nombre TEXT, precio REAL)")
            batch = [(f"{p.get('name','')} {p.get('brand','')}".strip(), p.get("price", 0)) for p in productos]
            c.executemany("INSERT INTO productos VALUES (?,?)", batch)
            c.execute("CREATE INDEX IF NOT EXISTS idx_n ON productos(nombre)")
            conn.commit(); conn.close()
            logger.info(f"✅ BUNKER SINCRONIZADO: {len(productos)} productos.")
    except: pass

@asynccontextmanager
async def lifespan(app: FastAPI):
    from agent.memory import inicializar_db
    await inicializar_db()
    threading.Thread(target=sincronizar_bunker, daemon=True).start()
    yield

app = FastAPI(lifespan=lifespan)

async def delayed_process(telefono):
    await asyncio.sleep(4) 
    now = time.time()
    if now < silence_timers.get(telefono, 0):
        async with buffer_lock: message_buffer.pop(telefono, None)
        return

    async with buffer_lock:
        if telefono not in message_buffer: return
        data = message_buffer.pop(telefono)
    
    try:
        from agent.providers import obtener_proveedor
        from agent.brain import generar_respuesta
        from agent.memory import guardar_mensaje, obtener_historial
        
        texto_recibido = " ".join(data["messages"]).strip()
        if not texto_recibido: return
        
        proveedor = obtener_proveedor()
        h = await obtener_historial(telefono)
        txt = await generar_respuesta(texto_recibido, h)
        
        if await proveedor.enviar_mensaje(telefono, txt):
            await guardar_mensaje(telefono, "user", texto_recibido)
            await guardar_mensaje(telefono, "assistant", txt)
            logger.info(f"✅ Respuesta 11.8 enviada a {telefono}")
    except Exception as e:
        logger.error(f"Error Main 11.8: {e}")

@app.post("/webhook")
async def webhook_post(r: Request):
    try:
        from agent.providers import obtener_proveedor
        body = await r.json()
        proveedor = obtener_proveedor()
        mensajes = await proveedor.parsear_webhook(raw_body=body)
        
        if mensajes:
            for msg in mensajes:
                telefono = msg.telefono
                now = time.time()
                
                # 🕵️‍♂️ Dante intervino (es_propio detectado en whapi.py)
                if msg.es_propio:
                    silence_timers[telefono] = now + 600
                    logger.info(f"🤫 Dante intervino en {telefono}. Bot silenciado 10m.")
                    continue
                
                if now < silence_timers.get(telefono, 0):
                    continue

                async with buffer_lock:
                    if telefono not in message_buffer:
                        message_buffer[telefono] = {"messages": [], "task": None}
                    message_buffer[telefono]["messages"].append(msg.texto)
                    if message_buffer[telefono]["task"]:
                        message_buffer[telefono]["task"].cancel()
                    message_buffer[telefono]["task"] = asyncio.create_task(delayed_process(telefono))
    except: pass
    return PlainTextResponse("ok")

@app.get("/debug")
async def debug():
    return {"status": "online", "version": "11.8", "silenciados": len(silence_timers)}

@app.get("/")
async def health(): return {"status": "indio_11_8_online"}
