# agent/brain.py — El Indio EXPERTO 7.0 🏹🛡️🦾💎✨🦾
import os, logging, asyncio, datetime, sqlite3, google.generativeai as genai

logger = logging.getLogger("agentkit")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "knowledge", "catalogo.db")

# 🕵️‍♂️ FILTRO DE CONTEXTO: Detecta interacciones sociales
def es_conversacion_social(texto: str) -> bool:
    social = {"gracias", "perfecto", "buenisimo", "dale", "joya", "espectacular", "bueno", "chau", "listo", "genio"}
    palabras = texto.lower().split()
    return any(p in social for p in palabras)

# 🔍 MOTOR DE BÚSQUEDA AGRESIVO
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
    palabras_clave = [vocabulario.get(p, p) for p in limpia.split() if p not in ruido and len(p) >= 3]

    if not palabras_clave: return ""

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        res = []
        
        # Priorizamos intersección
        filtros = ["nombre LIKE ?" for _ in palabras_clave]
        params = [f"%{p}%" for p in palabras_clave]
        c.execute(f"SELECT nombre, precio FROM productos WHERE {' AND '.join(filtros)} LIMIT 15", params)
        res.extend(c.fetchall())

        if len(res) < 5:
            for p in palabras_clave:
                c.execute("SELECT nombre, precio FROM productos WHERE nombre LIKE ? LIMIT 10", [f"%{p}%"])
                res.extend(c.fetchall())
        
        conn.close()
        unique_res = list(dict.fromkeys(res))[:25]
        return "\n".join([f"- {r[0]}: ${r[1]:,.0f}" for r in unique_res])
    except Exception as e:
        logger.error(f"Error buscador 7.0: {e}")
        return ""

raw_keys = os.getenv("GOOGLE_API_KEYS") or os.getenv("GOOGLE_API_KEY") or ""
LISTA_LLAVES = [k.strip() for k in raw_keys.split(",") if k.strip()]

async def generar_respuesta(mensaje_usuario, historial):
    model_names = ["gemini-flash-latest", "gemini-1.5-flash", "gemini-pro"]
    
    contexto = buscar_en_el_catalogo(mensaje_usuario)

    # 🏹 IDENTIDAD FERRETERA 7.0 
    system_prompt = f"""
Sos el experto de mostrador de 'Ferretería El Indio'. Sé un ferretero de barrio real, sin vueltas.

NUESTRAS SUCURSALES (Links Reales):
- Indio I: https://www.google.com/maps/place/Ferreter%C3%ADa+El+Indio+I/@-34.5996102,-58.876654
- Indio II: https://www.google.com/maps/place/Ferreter%C3%ADa+El+Indio+II/@-34.6019995,-58.8737439
(NUNCA digas Don Orione ni Claypole, mandá los links y decí Indio I o II).

FORMAS DE PAGO:
- Efectivo.
- Transferencia por Mercado Pago (QR o Alias).

ENVÍOS / FLETES:
- Si preguntan por envíos o fletes, respondé EXCLUSIVAMENTE: 'Te dejo con los encargados y en un rato te contestamos, gracias.' No prometas envíos.

SERVICIO TÉCNICO (Ariel):
- Ariel repara máquinas. Traé la máquina al local para que la vea y te asesore bien. No damos presupuesto por chat.

REGLAS DE ORO:
1. INVITA A MANDAR FOTOS: 'Si podés mandame foto de lo que buscás así te asesoro mejor'.
2. PRECIOS: Si hay DATOS abajo, DALOS. Si no, consultá en sistema.
3. ADAPTACIÓN: Hablá como el cliente (vos, che, etc).
4. HORARIOS: Lun-Vie 8-18, Sáb 9-14, Dom/Fér 9-13.
5. DISCLAIMER: 'Confirmamos stock al momento de la compra'.

DATOS FERRETEROS:
{contexto if contexto else "Buscá asesorarlo si no hay stock exacto."}
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
    return "¡Buenas! Gracias por comunicarte con El Indio. ¿Qué estás necesitando?"
