# agent/brain.py — El Indio EXPERTO 7.1 (ULTRA-CONCISO) 🏹🛡️🦾💎✨🦾
import os, logging, asyncio, datetime, sqlite3, google.generativeai as genai

logger = logging.getLogger("agentkit")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "knowledge", "catalogo.db")

def es_conversacion_social(texto: str) -> bool:
    social = {"gracias", "perfecto", "buenisimo", "dale", "joya", "espectacular", "bueno", "chau", "listo", "genio", "ok", "okey"}
    palabras = texto.lower().split()
    return any(p in social for p in palabras)

def buscar_en_el_catalogo(consulta: str) -> str:
    if not os.path.exists(DB_PATH) or es_conversacion_social(consulta): return ""
    limpia = consulta.lower()
    for char in "?!,.:;()": limpia = limpia.replace(char, "")
    ruido = {"estoy", "buscando", "quiero", "necesito", "tienen", "venden", "tenes", "podes", "pasame", "decime", "precio", "cuanto", "sale"}
    vocabulario = {"moladora": "amoladora", "moladoras": "amoladora", "fresa": "fresadora", "agujereadora": "taladro"}
    palabras_clave = [vocabulario.get(p, p) for p in limpia.split() if p not in ruido and len(p) >= 3]
    if not palabras_clave: return ""
    try:
        conn = sqlite3.connect(DB_PATH); c = conn.cursor(); res = []
        filtros = ["nombre LIKE ?" for _ in palabras_clave]; params = [f"%{p}%" for p in palabras_clave]
        c.execute(f"SELECT nombre, precio FROM productos WHERE {' AND '.join(filtros)} LIMIT 10", params)
        res.extend(c.fetchall())
        conn.close()
        unique_res = list(dict.fromkeys(res))[:10]
        return "\n".join([f"- {r[0]}: ${r[1]:,.0f}" for r in unique_res])
    except: return ""

raw_keys = os.getenv("GOOGLE_API_KEYS") or os.getenv("GOOGLE_API_KEY") or ""
LISTA_LLAVES = [k.strip() for k in raw_keys.split(",") if k.strip()]

async def generar_respuesta(mensaje_usuario, historial):
    model_names = ["gemini-flash-latest", "gemini-1.5-flash"]
    contexto = buscar_en_el_catalogo(mensaje_usuario)

    # 🏹 REGLAS DE "NO SER PESADO"
    system_prompt = f"""
Sos el experto de mostrador de 'Ferretería El Indio'. Sé ULTRA-CONCISO. 

REGLAS DE ORO:
1. NO mandes los links de Google Maps a menos que te pregunten 'VIVÍ', 'DONDE ESTÁN', 'UBICACIÓN' o 'COMO LLEGO'.
2. Si el cliente agradece o dice algo social, respondé en UNA sola línea (ej: 'De nada, che!').
3. ARIEL REPARACIONES: Respondé cortito: 'Si, Ariel repara máquinas acá en el local. Traela así la ve y te asesora bien.'. Punto. No más que eso.
4. PRECIOS: Tirale los precios directo si los tenés abajo. No digas 'Buen día' si ya se saludaron.
5. NO menciones que sos una IA. Hablá como un ferretero normal.

SUCURSALES (Solo usarlas si las piden):
- Indio I: https://www.google.com/maps/place/Ferreter%C3%ADa+El+Indio+I/@-34.5996102,-58.876654
- Indio II: https://www.google.com/maps/place/Ferreter%C3%ADa+El+Indio+II/@-34.6019995,-58.8737439

ARIEL: Arregla máquinas en mostrador presencial.

DATOS DEL CATÁLOGO REAL:
{contexto if contexto else "Sin resultados específicos."}
""".strip()

    for api_key in LISTA_LLAVES:
        try:
            genai.configure(api_key=api_key)
            for name in model_names:
                try:
                    model = genai.GenerativeModel(name)
                    response = await model.generate_content_async(f"{system_prompt}\n\nhistorial reciente: {historial[-3:] if historial else []}\n\nCliente: {mensaje_usuario}")
                    if response and hasattr(response, 'text') and response.text:
                        return response.text
                except: continue
        except: continue
    return "¡Buenas! ¿En qué te puedo ayudar?"
