# agent/catalogo.py — El Nuevo Motor de la Ferretería 🏹🦾✨
import os, sqlite3, requests, logging

logger = logging.getLogger("agentkit")
DB_PATH = os.path.join("knowledge", "catalogo.db")
JSON_URL = "https://ferreteriaelindio.netlify.app/data.json"

def actualizar_stock_indio():
    """Este es el motor que sincroniza los 111k productos"""
    try:
        if not os.path.exists("knowledge"): os.makedirs("knowledge")
        r = requests.get(JSON_URL, timeout=60)
        if r.status_code != 200: return False
        productos = r.json()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("DROP TABLE IF EXISTS productos")
        c.execute("CREATE TABLE productos (nombre TEXT, precio REAL, rubro TEXT, id TEXT PRIMARY KEY)")
        batch = []
        for p in productos:
            batch.append((
                f"{p.get('name','')} {p.get('brand','')}".strip(),
                p.get("price", 0),
                p.get("provider", "GENERAL"),
                p.get("id", "")
            ))
        c.executemany("INSERT OR REPLACE INTO productos VALUES (?,?,?,?)", batch)
        c.execute("CREATE INDEX idx_nombre ON productos(nombre)")
        conn.commit()
        conn.close()
        logger.info(f"✅ {len(productos)} productos indexados.")
        return True
    except Exception as e:
        logger.error(f"Error sincronismo: {e}")
        return False

def buscar_precio(consulta: str) -> str:
    """Buscador inteligente para el Indio"""
    if not os.path.exists(DB_PATH): return ""
    limpia = consulta.lower().replace("?", "").replace("!", "").replace(",", "")
    vocabulario = {"moladora": "amoladora", "moladoras": "amoladora", "fresa": "fresadora", "agujereadora": "taladro"}
    palabras = [p for p in limpia.split() if len(p) > 2]
    busqueda = []
    for p in palabras:
        busqueda.append(p)
        if p.endswith("s"): busqueda.append(p[:-1])
        if p in vocabulario: busqueda.append(vocabulario[p])
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        where_clauses = ["nombre LIKE ?" for _ in set(busqueda)]
        params = [f"%{p}%" for p in set(busqueda)]
        sql = f"SELECT nombre, precio, rubro FROM productos WHERE {' OR '.join(where_clauses)} LIMIT 6"
        c.execute(sql, params)
        res = c.fetchall()
        conn.close()
        if res: return "\n".join([f"- {r[0]}: ${r[1]:,.2f}" for r in res])
        return ""
    except: return ""
