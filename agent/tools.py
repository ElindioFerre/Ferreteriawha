# agent/tools.py — Motor de Alta Potencia (Sincronismo de 111k productos) 🏹🦾📚✨
import os, sqlite3, requests, logging, json

logger = logging.getLogger("agentkit")
DB_PATH = os.path.join("knowledge", "catalogo.db")
JSON_URL = "https://ferreteriaelindio.netlify.app/data.json"

def sincronizar_catalogo():
    """Descarga los 111k productos y los guarda con eficiencia de memoria"""
    try:
        if not os.path.exists("knowledge"): os.makedirs("knowledge")
        
        logger.info("📡 Descargando catálogo masivo desde la web...")
        r = requests.get(JSON_URL, timeout=60, stream=True)
        if r.status_code != 200:
            logger.error(f"❌ Error al descargar catálogo: {r.status_code}")
            return False

        # Cargamos el JSON (Aquí es donde se consume RAM, cuidado)
        productos = r.json()
        total = len(productos)
        logger.info(f"📊 Procesando {total} productos...")
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("DROP TABLE IF EXISTS productos")
        c.execute("""CREATE TABLE productos (
                        nombre TEXT, 
                        precio REAL, 
                        rubro TEXT, 
                        id TEXT PRIMARY KEY
                    )""")
        
        # 🏹 INSERTAMOS EN TANDAS DE 5000 (Batch mode)
        # Esto evita que la base de datos se bloquee o use demasiada memoria
        for i in range(0, total, 5000):
            batch = []
            for p in productos[i:i+5000]:
                batch.append((
                    f"{p.get('category','')} {p.get('name','')}".strip(),
                    p.get("price", 0),
                    p.get("provider", "GENERAL"),
                    p.get("id", "")
                ))
            c.executemany("INSERT OR REPLACE INTO productos VALUES (?,?,?,?)", batch)
            conn.commit()
            # liberamos un poco el objeto batch
            del batch 
        
        c.execute("CREATE INDEX IF NOT EXISTS idx_nombre ON productos(nombre)")
        conn.commit()
        conn.close()
        
        # 🏹 Limpiamos la lista gigante de memoria para no clavar el bot
        del productos 
        
        logger.info(f"✨ ¡Sincronizado! {total} productos listos en la DB.")
        return True
    except Exception as e:
        logger.error(f"❌ Falló el sincronismo: {e}")
        return False

def buscar_precio(consulta: str) -> str:
    """Busca en el Bibliotecario SQLite (Ultra-rápido)"""
    if not os.path.exists(DB_PATH):
        return ""

    ignorar = ["cuanto", "sale", "tenes", "precio", "de", "del", "la", "el", "quisiera", "saber"]
    limpia = consulta.lower().replace("?", "").replace("!", "")
    palabras = [p for p in limpia.split() if p not in ignorar and len(p) > 2]
    
    if not palabras: return ""

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Búsqueda SQL Multiclave
        where = " AND nombre LIKE ? " * len(palabras)
        params = [f"%{p}%" for p in palabras]
        
        query = f"SELECT nombre, precio, rubro FROM productos WHERE {where} LIMIT 4"
        c.execute(query, params)
        res = c.fetchall()
        conn.close()

        if res:
            return "\n".join([f"- {r[0]}: ${r[1]:,.2f} ({r[2]})" for r in res])
        return ""
    except Exception as e:
        logger.error(f"Error en buscador: {e}")
        return ""
