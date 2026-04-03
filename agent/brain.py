# agent/brain.py — El Indio EXPERTO 5.3 🏹🛡️🦾💎✨🦾
import os, logging, asyncio, datetime, sqlite3, google.generativeai as genai

logger = logging.getLogger("agentkit")
# 🏹 RUTA ABSOLUTA PARA NO FALLAR EN RAILWAY
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "knowledge", "catalogo.db")

# 🔍 EL MOTOR DE BÚSQUEDA AGRESIVO (BUNKER)
def buscar_en_el_catalogo(consulta: str) -> str:
    """Buscador hiper-agresivo para que el Indio no se guarde nada"""
    if not os.path.exists(DB_PATH): return ""
    limpia = consulta.lower().replace("?", "").replace("!", "").replace(",", "").replace(".", "")
    vocabulario = {
        "moladora": "amoladora", "moladoras": "amoladora", 
        "fresa": "fresadora", "agujereadora": "taladro",
        "amoladora": "amoladora", "taladro": "taladro"
    }
    # Filtramos palabras vacias y cortas (pero permitimos de 3 letras como 'pvc')
    palabras = [p for p in limpia.split() if len(p) >= 3]
    busqueda = []
    for p in palabras:
        busqueda.append(p)
        if p.endswith("s"): busqueda.append(p[:-1]) # plurales
        if p in vocabulario: busqueda.append(vocabulario[p])
    
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # 🛡️ NORMALIZACIÓN DE BÚSQUEDA: Buscamos coincidencias que tengan alguna de las palabras clave
        unique_words = list(set(busqueda))
        if not unique_words: return ""
        
        where_clauses = ["nombre LIKE ?" for _ in unique_words]
        params = [f"%{p}%" for p in unique_words]
        
        # Buscamos un poco más para tener de dónde elegir (10 resultados)
        sql = f"SELECT nombre, precio FROM productos WHERE {' OR '.join(where_clauses)} LIMIT 10"
        c.execute(sql, params)
        res = c.fetchall()
        conn.close()
        
        if res:
            # Mostramos el nombre real y el precio para que la IA actúe
            return "\n".join([f"- {r[0]}: ${r[1]:,.0f}" for r in res])
        return ""
    except Exception as e:
        logger.error(f"Error buscador interno: {e}")
        return ""

raw_keys = os.getenv("GOOGLE_API_KEYS") or os.getenv("GOOGLE_API_KEY") or ""
LISTA_LLAVES = [k.strip() for k in raw_keys.split(",") if k.strip()]

async def generar_respuesta(mensaje_usuario, historial):
    model_names = ["gemini-flash-latest", "gemini-1.5-flash", "gemini-pro"]
    
    # BUSCAMOS DIRECTO EN EL MOTOR INTERNO
    contexto = ""
    try:
        contexto = buscar_en_el_catalogo(mensaje_usuario)
    except: pass

    # 🏹 LOS HORARIOS SON SAGRADOS
    # Lunes a viernes de 8 a 18, Sabados de 9 a 14, domingos y Feriados de 9 a 13
    
    system_prompt = f"""
Sos el experto de mostrador de 'Ferretería El Indio'. Sé un ferretero directo, técnico y comercial.

HORARIOS OFICIALES:
- Lunes a Viernes: 8:00 a 18:00
- Sábados: 9:00 a 14:00
- Domingos y Feriados: 9:00 a 13:00

REGLAS DE ORO:
1. NO SALUDES si el cliente ya te habló en el historial. No seas repetitivo.
2. PRECIOS: Si el cliente pide precio, mirá los DATOS reales abajo y dale opciones con el nombre tal cual aparece.
3. SI HAY DATOS: No digas "voy a consultar", decí "Tengo estas opciones..." y dale el precio.
4. SI NO HAY DATOS: Ahí sí decile que vas a consultar el stock exacto para no fallarle.
5. NO menciones códigos internos ni proveedores.

DATOS DEL CATÁLOGO REAL PARA ESTA CONSULTA:
{contexto if contexto else "No se encontraron coincidencias exactas en el catálogo local."}
""".strip()

    for api_key in LISTA_LLAVES:
        try:
            genai.configure(api_key=api_key)
            for name in model_names:
                try:
                    model = genai.GenerativeModel(name)
                    response = await model.generate_content_async(f"{system_prompt}\n\nCliente: {mensaje_usuario}")
                    if response and hasattr(response, 'text') and response.text:
                        return response.text
                except: continue
        except: continue
    return "¡Hola! Bienvenido a 'El Indio'. ¿En qué te puedo asesorar hoy?"
