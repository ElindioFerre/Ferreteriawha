# agent/tools.py — El Bibliotecario del Indio (Búsqueda de 111k productos) 🏹🦾📚✨
import os, sqlite3, requests, logging, json

logger = logging.getLogger("agentkit")
DB_PATH = os.path.join("knowledge", "catalogo.db")
JSON_URL = "https://ferreteriaelindio.netlify.app/data.json"

def sincronizar_catalogo():
    """Descarga el JSON de la web y lo vuelca a una base de datos SQLite rápida"""
    try:
        logger.info("📡 Iniciando sincronismo con la web (111k productos)...")
        r = requests.get(JSON_URL, timeout=30)
        productos = r.json()
        
        # Conexión y limpieza de la base
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("DROP TABLE IF EXISTS productos")
        c.execute("""CREATE TABLE productos (
                        nombre TEXT, 
                        precio REAL, 
                        rubro TEXT, 
                        id TEXT PRIMARY KEY
                    )""")
        
        # Carga masiva (Batch Insert) para máxima velocidad
        batch = []
        for p in productos:
            batch.append((
                f"{p['category']} - {p['name']}", # Combinamos para que la IA entienda qué es
                p.get("price", 0),
                p.get("provider", ""),
                p.get("id", "")
            ))
        
        c.executemany("INSERT OR REPLACE INTO productos VALUES (?,?,?,?)", batch)
        # Creamos un índice para que la búsqueda vuele
        c.execute("CREATE INDEX IF NOT EXISTS idx_nombre ON productos(nombre)")
        conn.commit()
        conn.close()
        logger.info(f"✨ ¡Sincronizado! {len(productos)} productos listos.")
        return True
    except Exception as e:
        logger.error(f"❌ Error sincronizando: {e}")
        return False

def buscar_precio(consulta: str) -> str:
    """Busca en el Bibliotecario de SQLite de forma ultra-rápida"""
    if not os.path.exists(DB_PATH):
        # Si no existe la DB, intentamos crearla al vuelo (solo si no es muy pesado)
        sincronizar_catalogo()

    # Limpiamos pregunta
    ignorar = ["cuanto", "sale", "tenes", "precio", "de", "del"]
    palabras = [p.lower() for p in consulta.lower().replace("?", "").split() if p not in ignorar and len(p) > 2]
    
    if not palabras: return ""

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Búsqueda tipo SQL: Nombre LIKE %p1% AND Nombre LIKE %p2%...
        where_clause = " AND nombre LIKE ? " * len(palabras)
        params = [f"%{p}%" for p in palabras]
        
        query = f"SELECT nombre, precio, rubro FROM productos WHERE {where_clause} LIMIT 3"
        c.execute(query, params)
        res = c.fetchall()
        conn.close()

        if res:
            return "\n".join([f"- {r[0]}: ${r[1]:,.2f} ({r[2]})" for r in res])
        return ""
    except Exception as e:
        logger.error(f"Error buscando en DB: {e}")
        return ""
