# agent/brain.py — El Indio EXPERTO 6.0 🏹🛡️🦾💎✨🦾
import os, logging, asyncio, datetime, sqlite3, google.generativeai as genai

logger = logging.getLogger("agentkit")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "knowledge", "catalogo.db")

# 🕵️‍♂️ FILTRO DE CONTEXTO: Detecta si el cliente solo esta saludando o agradeciendo
def es_conversacion_social(texto: str) -> bool:
    social = {"gracias", "perfecto", "buenisimo", "dale", "joya", "espectacular", "bueno", "chau", "listo"}
    palabras = texto.lower().split()
    return any(p in social for p in palabras)

# 🔍 MOTOR DE BÚSQUEDA "INDIO 6.0" (Inteligencia de Mostrador)
def buscar_en_el_catalogo(consulta: str) -> str:
    if not os.path.exists(DB_PATH) or es_conversacion_social(consulta): return ""
    
    limpia = consulta.lower()
    for char in "?!,.:;()": limpia = limpia.replace(char, "")
    
    ruido = {
        "estoy", "buscando", "quiero", "necesito", "necesitaria", "tendras", "tenes", "tienen", 
        "venden", "podes", "pasame", "decime", "hola", "buen", "dia", "buenas", "noches", "tardes",
        "precio", "cuanto", "sale", "costo", "valor", "alguna", "algun", "una", "uno", "unos", "unas",
        "para", "que", "con", "los", "las", "por", "sobre", "del", "esta", "esto", "este", "estos", 
        "donde", "estan", "hacer", "cortar", "usar", "algunas", "marca", "marcas", "opcion", "opciones"
    }
    
    vocabulario = {"moladora": "amoladora", "moladoras": "amoladora", "fresa": "fresadora", "agujereadora": "taladro"}

    palabras_raw = limpia.split()
    palabras_clave = [vocabulario.get(p, p) for p in palabras_raw if p not in ruido and len(p) >= 3]

    if not palabras_clave: return ""

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        res = []
        
        # Búsqueda AND (Precisa)
        filtros = ["nombre LIKE ?" for _ in palabras_clave]
        params = [f"%{p}%" for p in palabras_clave]
        c.execute(f"SELECT nombre, precio FROM productos WHERE {' AND '.join(filtros)} LIMIT 15", params)
        res.extend(c.fetchall())

        # Si no hay mucho, búsqueda OR (Amplia)
        if len(res) < 5:
            for p in palabras_clave:
                c.execute("SELECT nombre, precio FROM productos WHERE nombre LIKE ? LIMIT 10", [f"%{p}%"])
                res.extend(c.fetchall())
        
        conn.close()
        unique_res = list(dict.fromkeys(res))[:25]
        return "\n".join([f"- {r[0]}: ${r[1]:,.0f}" for r in unique_res])
    except Exception as e:
        logger.error(f"Error buscador 6.0: {e}")
        return ""

raw_keys = os.getenv("GOOGLE_API_KEYS") or os.getenv("GOOGLE_API_KEY") or ""
LISTA_LLAVES = [k.strip() for k in raw_keys.split(",") if k.strip()]

async def generar_respuesta(mensaje_usuario, historial):
    model_names = ["gemini-flash-latest", "gemini-1.5-flash", "gemini-pro"]
    
    contexto = buscar_en_el_catalogo(mensaje_usuario)

    # 🏹 IDENTIDAD FERRETERA 6.0 (Sin magia, pura realidad)
    system_prompt = f"""
Sos el experto de mostrador de 'Ferretería El Indio'. No sos un bot mágico, sos un ferretero de barrio. 
Adaptá tu forma de hablar al cliente: si el cliente es cortante, sé cortante. Si es amigable, sé amigable. No menciones que sos una IA.

NUESTRAS SUCURSALES:
- Indio I: https://maps.app.goo.gl/95bc91002049054f (Don Orione)
- Indio II: https://maps.app.goo.gl/95bc91004148f913 (Claypole)

SERVICIO TÉCNICO (Ariel):
- Ariel sigue aceptando máquinas para reparar. Pero NO damos presupuestos por acá. Tienen que traer la máquina al mostrador para que Ariel la revise y asesore bien.

HORARIOS: Lun-Vie 8-18, Sáb 9-14, Dom/Fér 9-13.

REGLAS DE ORO:
1. NO SALUDES si ya están hablando.
2. Si el cliente dice 'Gracias' o 'Perfecto', saludalo amigablemente y NO busques productos.
3. PRECIOS: Si hay DATOS abajo, DALOS. Si no hay nada que coincida, decí: 'Eso no me figura en la lista rápida, si querés consulto en el sistema o pasate por el local'.
4. DISCLAIMER: 'Confirmamos stock al momento de la compra'.

DATOS DEL CATÁLOGO REAL:
{contexto if contexto else "Sin resultados específicos para esta frase."}
""".strip()

    for api_key in LISTA_LLAVES:
        try:
            genai.configure(api_key=api_key)
            for name in model_names:
                try:
                    model = genai.GenerativeModel(name)
                    response = await model.generate_content_async(f"{system_prompt}\n\nhistorial: {historial}\n\nCliente: {mensaje_usuario}")
                    if response and hasattr(response, 'text') and response.text:
                        return response.text
                except: continue
        except: continue
    return "¡Buenas! Gracias por comunicarte con El Indio. ¿En qué te puedo ayudar?"
