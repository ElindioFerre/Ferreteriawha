# agent/brain.py — El Indio EXPERTO 5.5 🏹🛡️🦾💎✨🦾
import os, logging, asyncio, datetime, sqlite3, google.generativeai as genai

logger = logging.getLogger("agentkit")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "knowledge", "catalogo.db")

# 🔍 MOTOR DE BÚSQUEDA "FERRETERO VIEJO" (No se come ningún verso)
def buscar_en_el_catalogo(consulta: str) -> str:
    if not os.path.exists(DB_PATH): return ""
    
    limpia = consulta.lower()
    for char in "?!,.:;()": limpia = limpia.replace(char, "")
    
    # 🏹 DICCIONARIO DE RUIDO MASIVO (Verbos y conectores comunes)
    ruido = {
        "estoy", "buscando", "quiero", "necesito", "necesitaria", "tendras", "tenes", "tienen", 
        "venden", "podes", "pasame", "decime", "hola", "buen", "dia", "buenas", "noches", "tardes",
        "precio", "cuanto", "sale", "costo", "valor", "alguna", "algun", "una", "uno", "unos", "unas",
        "para", "que", "con", "los", "las", "por", "sobre", "del", "esta", "esto", "este", "estos", 
        "donde", "estan", "vivi", "casa", "hacer", "cortar", "usar", "algunas", "marca", "marcas",
        "opcion", "opciones", "tenen", "tambien", "tambie", "recomendas", "recomendarme", "recomendame"
    }
    
    vocabulario = {
        "moladora": "amoladora", "moladoras": "amoladora", "amoladora": "amoladora",
        "fresa": "fresadora", "agujereadora": "taladro", "taladro": "taladro",
        "disco": "disco", "discos": "disco", "termofusion": "termofusora"
    }

    palabras_raw = limpia.split()
    palabras_clave = []
    
    # Solo nos quedamos con lo que NO es ruido
    for p in palabras_raw:
        if p in ruido or len(p) < 3: continue
        palabras_clave.append(p)

    if not palabras_clave: return ""

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # 🕵️‍♂️ ESTRATEGIA: Intentamos buscar por cada palabra clave hasta encontrar algo real
        res = []
        for p in palabras_clave:
            # Corregimos palabra (ej: moladora -> amoladora)
            termino = vocabulario.get(p, p)
            sql = "SELECT nombre, precio FROM productos WHERE nombre LIKE ? LIMIT 10"
            c.execute(sql, [f"%{termino}%"])
            found = c.fetchall()
            if found:
                res.extend(found)
                if len(res) >= 10: break # Suficiente contexto
        
        conn.close()
        
        if res:
            # Eliminamos duplicados si los hay y armamos el texto
            unique_res = list(set(res))[:10]
            return "\n".join([f"- {r[0]}: ${r[1]:,.0f}" for r in unique_res])
        return ""
    except Exception as e:
        logger.error(f"Error buscador ferretero: {e}")
        return ""

raw_keys = os.getenv("GOOGLE_API_KEYS") or os.getenv("GOOGLE_API_KEY") or ""
LISTA_LLAVES = [k.strip() for k in raw_keys.split(",") if k.strip()]

async def generar_respuesta(mensaje_usuario, historial):
    model_names = ["gemini-flash-latest", "gemini-1.5-flash", "gemini-pro"]
    
    contexto = ""
    try:
        contexto = buscar_en_el_catalogo(mensaje_usuario)
    except: pass

    # 🏹 REGLA DE NO-HALLUCINATION
    system_prompt = f"""
Sos el experto de mostrador de 'Ferretería El Indio'. Sé directo y muy profesional. No uses placeholders ni digas 'voy a consultar' si tenés DATOS abajo.

HORARIOS: Lun-Vie 8-18, Sáb 9-14, Dom/Fér 9-13.

REGLAS DE ORO:
1. NO SALUDES si el historial muestra que ya lo hiciste.
2. PRECIOS: Si hay DATOS abajo, DALOS. No inventes precios.
3. Si el cliente busca una herramienta y los datos abajo muestran repuestos de auto que no tienen nada que ver, decí que no encontraste stock de esa herramienta específica.
4. Miralos bien: Si el cliente pidió 'amoladora' y en los datos dice 'AMOLADORA 7-MOD.WSL 180: $20,209', decile: 'Tengo la Amoladora 7-MOD de $20.209...'

DATOS DEL CATÁLOGO REAL:
{contexto if contexto else "No se encontraron resultados específicos."}
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
