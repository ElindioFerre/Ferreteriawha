# agent/brain.py — El Indio EXPERTO 5.6 🏹🛡️🦾💎✨🦾
import os, logging, asyncio, datetime, sqlite3, google.generativeai as genai

logger = logging.getLogger("agentkit")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "knowledge", "catalogo.db")

# 🏹 MOTOR DE BÚSQUEDA "GRAN FERRETERO" (Variedad y Filtro de Marca)
def buscar_en_el_catalogo(consulta: str) -> str:
    if not os.path.exists(DB_PATH): return ""
    
    limpia = consulta.lower()
    for char in "?!,.:;()": limpia = limpia.replace(char, "")
    
    # 🏹 RUIDO REFORMADO
    ruido = {
        "estoy", "buscando", "quiero", "necesito", "necesitaria", "tendras", "tenes", "tienen", 
        "venden", "podes", "pasame", "decime", "hola", "buen", "dia", "buenas", "noches", "tardes",
        "precio", "cuanto", "sale", "costo", "valor", "alguna", "algun", "una", "uno", "unos", "unas",
        "para", "que", "con", "los", "las", "por", "sobre", "del", "esta", "esto", "este", "estos", 
        "donde", "estan", "hacer", "cortar", "usar", "algunas", "marca", "marcas",
        "opcion", "opciones", "tenen", "tambien", "tambie", "recomendas", "recomendarme", "recomendame"
    }
    
    vocabulario = {
        "moladora": "amoladora", "moladoras": "amoladora", "amoladora": "amoladora",
        "fresa": "fresadora", "agujereadora": "taladro", "taladro": "taladro",
        "disco": "disco", "discos": "disco", "termofusion": "termofusora",
        "omaha": "omaha", "total": "total"
    }

    palabras_raw = limpia.split()
    palabras_clave = [vocabulario.get(p, p) for p in palabras_raw if p not in ruido and len(p) >= 3]

    if not palabras_clave: return ""

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # 🕵️‍♂️ ESTRATEGIA: Buscamos hasta 25 resultados para que la IA elija marcas (como Omaha)
        res = []
        
        # 1. Priorizamos búsqueda conjunta (ej: amoladora AND omaha)
        if len(palabras_clave) > 1:
            filtros = ["nombre LIKE ?" for _ in palabras_clave]
            params = [f"%{p}%" for p in palabras_clave]
            sql = f"SELECT nombre, precio FROM productos WHERE {' AND '.join(filtros)} LIMIT 15"
            c.execute(sql, params)
            res.extend(c.fetchall())

        # 2. Si hay pocos o no hay, buscamos por cada palabra individualmente
        if len(res) < 5:
            for p in palabras_clave:
                sql = "SELECT nombre, precio FROM productos WHERE nombre LIKE ? LIMIT 15"
                c.execute(sql, [f"%{p}%"])
                res.extend(c.fetchall())
        
        conn.close()
        
        if res:
            # Quitamos duplicados y ordenamos para que el Indio vea variedad
            unique_res = list(dict.fromkeys(res))[:25]
            return "\n".join([f"- {r[0]}: ${r[1]:,.0f}" for r in unique_res])
        return ""
    except Exception as e:
        logger.error(f"Error buscador gran ferretero: {e}")
        return ""

raw_keys = os.getenv("GOOGLE_API_KEYS") or os.getenv("GOOGLE_API_KEY") or ""
LISTA_LLAVES = [k.strip() for k in raw_keys.split(",") if k.strip()]

async def generar_respuesta(mensaje_usuario, historial):
    model_names = ["gemini-flash-latest", "gemini-1.5-flash", "gemini-pro"]
    
    contexto = ""
    try:
        contexto = buscar_en_el_catalogo(mensaje_usuario)
    except: pass

    system_prompt = f"""
Sos el experto de mostrador de 'Ferretería El Indio'. Sé directo y muy profesional.

HORARIOS: Lun-Vie 8-18, Sáb 9-14, Dom/Fér 9-13.

REGLAS DE ORO:
1. NO SALUDES si el historial muestra que ya lo hiciste.
2. PRECIOS: Si hay DATOS abajo, DALOS. 
3. DISCLAIMER DE STOCK: Siempre que des una lista de precios, recordá decirle al cliente que 'Consultamos stock al momento de la compra para asegurar disponibilidad' o similar.
4. VARIEDAD: Si en los datos ves distintas marcas (Omaha, Total, Daewoo), comentale la diferencia si la sabés (Omaha/Total es muy buena relación precio/calidad para el hogar).
5. No inventes precios ni mezcles con repuestos de autos.

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
    return "¡Hola! Bienvenido a 'El Indio'. ¿Cómo te podemos ayudar hoy?"
