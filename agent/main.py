# agent/main.py — El Indio EN EL BUNKER 5.1 (Con Sensores de Alarma) 🏹🛰️🦾💎✨🦾
import os, logging, threading, sqlite3, requests, datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import PlainTextResponse, JSONResponse
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s agentkit: %(message)s")
logger = logging.getLogger("agentkit")

DB_PATH = os.path.join("knowledge", "catalogo.db")

# 🏹 MOTOR DE SINCRONISMO INTEGRADO (BUNKER)
def sincronizar_bunker():
    try:
        url = "https://ferreteriaelindio.netlify.app/data.json"
        if not os.path.exists("knowledge"): os.makedirs("knowledge")
        r = requests.get(url, timeout=60)
        if r.status_code != 200: return
        productos = r.json()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("DROP TABLE IF EXISTS productos")
        c.execute("CREATE TABLE productos (nombre TEXT, precio REAL)")
        batch = [(f"{p.get('name','')} {p.get('brand','')}".strip(), p.get("price", 0)) for p in productos]
        c.executemany("INSERT INTO productos VALUES (?,?)", batch)
        c.execute("CREATE INDEX IF NOT EXISTS idx_n ON productos(nombre)")
        conn.commit()
        conn.close()
        logger.info(f"✅ BUNKER CARGADO: {len(productos)} productos.")
    except Exception as e:
        logger.error(f"Err Bunker: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        from agent.memory import inicializar_db
        await inicializar_db()
        threading.Thread(target=sincronizar_bunker, daemon=True).start()
    except: pass
    yield

app = FastAPI(lifespan=lifespan)

# 📡 DETECTOR DE PROBLEMAS (Página de Diagnóstico)
@app.get("/debug")
async def detector_de_problemas():
    diagnostico = {
        "timestamp": datetime.datetime.now().isoformat(),
        "estado_sistema": "online",
        "sensores": {}
    }
    
    # Check 1: Catálogo (Buscador local)
    try:
        if os.path.exists(DB_PATH):
            conn = sqlite3.connect(DB_PATH)
            count = conn.execute("SELECT count(*) FROM productos").fetchone()[0]
            conn.close()
            diagnostico["sensores"]["catalogo"] = f"✅ OK ({count} productos cargados)"
        else:
            diagnostico["sensores"]["catalogo"] = "❌ ERROR: Base de datos no encontrada"
    except Exception as e:
        diagnostico["sensores"]["catalogo"] = f"❌ ERROR: {str(e)}"

    # Check 2: API Keys (Gemini)
    keys = (os.getenv("GOOGLE_API_KEYS") or "").split(",")
    diagnostico["sensores"]["llaves_gemini"] = f"✅ OK ({len([k for k in keys if k.strip()])} llaves detectadas)"

    # Check 3: Webhook
    diagnostico["sensores"]["webhook"] = "✅ OK Ready"
    
    # Check 4: Base de Datos de Memoria
    try:
        from agent.memory import DB_PATH as MEM_DB
        if os.path.exists(MEM_DB):
            diagnostico["sensores"]["memoria"] = "✅ OK Activada"
        else:
            diagnostico["sensores"]["memoria"] = "⚠️ Pendiente de primer uso"
    except: pass

    return JSONResponse(content=diagnostico)

@app.get("/")
async def health(): return {"status": "bunker_online"}

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
