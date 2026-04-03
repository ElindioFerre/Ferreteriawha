# agent/main.py — El Indio EN EL BUNKER 9.0 (CON PACIENCIA) 🏹🛰️🦾💎✨🦾
import os, logging, threading, sqlite3, requests, datetime, asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import PlainTextResponse, JSONResponse
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s agentkit: %(message)s")
logger = logging.getLogger("agentkit")

DB_PATH = os.path.join("knowledge", "catalogo.db")

# 🤫 BÚFER DE MENSAJES (Anti-Spam)
message_buffer = {} # {telefono: {"messages": [], "task": task}}
buffer_lock = asyncio.Lock()

def sincronizar_bunker():
    try:
        url = "https://ferreteriaelindio.netlify.app/data.json"
        if not os.path.exists("knowledge"): os.makedirs("knowledge")
        r = requests.get(url, timeout=60)
        if r.status_code != 200: return
        productos = r.json()
        conn = sqlite3.connect(DB_PATH); c = conn.cursor()
        c.execute("DROP TABLE IF EXISTS productos")
        c.execute("CREATE TABLE productos (nombre TEXT, precio REAL)")
        batch = [(f"{p.get('name','')} {p.get('brand','')}".strip(), p.get("price", 0)) for p in productos]
        c.executemany("INSERT INTO productos VALUES (?,?)", batch)
        c.execute("CREATE INDEX IF NOT EXISTS idx_n ON productos(nombre)")
        conn.commit(); conn.close()
        logger.info(f"✅ BUNKER CARGADO: {len(productos)} productos.")
    except: pass

@asynccontextmanager
async def lifespan(app: FastAPI):
    from agent.memory import inicializar_db
    await inicializar_db()
    threading.Thread(target=sincronizar_bunker, daemon=True).start()
    yield

app = FastAPI(lifespan=lifespan)

async def delayed_process(telefono):
    """Espera 3 segundos de silencio antes de procesar."""
    await asyncio.sleep(4) # Bajamos a 4 seg para estar seguros frente a bursts rapidos
    
    async with buffer_lock:
        if telefono not in message_buffer: return
        data = message_buffer.pop(telefono)
    
    try:
        from agent.providers import obtener_proveedor
        from agent.brain import generar_respuesta
        from agent.memory import guardar_mensaje, obtener_historial
        
        texto_completo = " ".join(data["messages"]).strip()
        if not texto_completo: return
        
        proveedor = obtener_proveedor()
        h = await obtener_historial(telefono)
        txt = await generar_respuesta(texto_completo, h)
        
        if await proveedor.enviar_mensaje(telefono, txt):
            await guardar_mensaje(telefono, "user", texto_completo)
            await guardar_mensaje(telefono, "assistant", txt)
            logger.info(f"✅ RESPUESTA ENVIADA A {telefono}")
    except Exception as e:
        logger.error(f"Error procesando buffer: {e}")

@app.post("/webhook")
async def webhook_post(r: Request):
    try:
        from agent.providers import obtener_proveedor
        body = await r.json()
        proveedor = obtener_proveedor()
        mensajes = await proveedor.parsear_webhook(raw_body=body)
        
        if mensajes:
            for msg in mensajes:
                if not msg.es_propio and msg.texto:
                    telefono = msg.telefono
                    async with buffer_lock:
                        if telefono not in message_buffer:
                            message_buffer[telefono] = {"messages": [], "task": None}
                        
                        # Guardar el nuevo mensaje
                        message_buffer[telefono]["messages"].append(msg.texto)
                        
                        # Cancelar tarea anterior si existia (para reiniciar los 4 seg)
                        if message_buffer[telefono]["task"]:
                            message_buffer[telefono]["task"].cancel()
                        
                        # Crear nueva tarea
                        message_buffer[telefono]["task"] = asyncio.create_task(delayed_process(telefono))
    except: pass
    return PlainTextResponse("ok")

@app.get("/debug")
async def debug():
    try:
        conn = sqlite3.connect(DB_PATH)
        count = conn.execute("SELECT count(*) FROM productos").fetchone()[0]
        conn.close()
        return {"productos": count, "buffer_size": len(message_buffer)}
    except: return {"error": "db not found"}

@app.get("/")
async def health(): return {"status": "bunker_online"}
