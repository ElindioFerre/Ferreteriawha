# agent/brain.py — El Indio EN EL BUNKER 5.0 🏹🛡️🦾💎✨
import os, logging, asyncio, datetime, sqlite3, google.generativeai as genai

logger = logging.getLogger("agentkit")
DB_PATH = os.path.join("knowledge", "catalogo.db")

# 🔍 EL MOTOR DE BÚSQUEDA INTEGRADO (SIN IMPORTACIONES EXTERNAS)
def buscar_en_el_catalogo(consulta: str) -> str:
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
        if not where_clauses: return ""
        sql = f"SELECT nombre, precio FROM productos WHERE {' OR '.join(where_clauses)} LIMIT 6"
        c.execute(sql, params)
        res = c.fetchall()
        conn.close()
        if res: return "\n".join([f"- {r[0]}: ${r[1]:,.2f}" for r in res])
        return ""
    except: return ""

raw_keys = os.getenv("GOOGLE_API_KEYS") or os.getenv("GOOGLE_API_KEY") or ""
LISTA_LLAVES = [k.strip() for k in raw_keys.split(",") if k.strip()]

async def generar_respuesta(mensaje_usuario, historial):
    model_names = ["gemini-flash-latest", "gemini-1.5-flash", "gemini-pro"]
    
    # BUSCAMOS DIRECTO EN EL MOTOR INTERNO
    contexto = ""
    try:
        ignorar = ["hola", "buenas", "buen dia", "hola!", "que tal", "como va"]
        if mensaje_usuario.lower().strip() not in ignorar:
            contexto = buscar_en_el_catalogo(mensaje_usuario)
    except: pass

    # 🏹 CONTEXTO Y PERSONALIDAD
    system_prompt = f"""
Sos el experto de mostrador de 'Ferretería El Indio'. Sé directo y profesional. No menciones códigos ni proveedores.
REGLA DE PRECIO: Da el precio exacto si aparece abajo. Si no aparece el precio en los DATOS del catálogo, decí que vas a consultar el stock actualizado.

DATOS DEL CATÁLOGO REAL:
{contexto if contexto else "No hay coincidencias exactas."}
""".strip()

    for api_key in LISTA_LLAVES:
        try:
            genai.configure(api_key=api_key)
            for name in model_names:
                try:
                    model = genai.GenerativeModel(name)
                    response = await model.generate_content_async(f"{system_prompt}\nMensaje: {mensaje_usuario}")
                    if response and hasattr(response, 'text') and response.text:
                        return response.text
                except: continue
        except: continue
    return "¡Hola! Bienvenido a 'El Indio'. ¿En qué fierros te puedo ayudar hoy?"
