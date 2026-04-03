# agent/brain.py — El Indio EXPERTO 9.0 (RELOJ EN HORA) 🏹🛡️🦾💎✨🦾
import os, logging, asyncio, datetime, sqlite3, google.generativeai as genai

logger = logging.getLogger("agentkit")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "knowledge", "catalogo.db")

def es_conversacion_social(texto: str) -> bool:
    social = {"gracias", "perfecto", "buenisimo", "dale", "joya", "espectacular", "bueno", "chau", "listo", "genio", "ok", "okey", "maestro"}
    palabras = texto.lower().split()
    return any(p in social for p in palabras)

def buscar_en_el_catalogo(consulta: str) -> str:
    if not os.path.exists(DB_PATH) or es_conversacion_social(consulta): return ""
    limpia = consulta.lower()
    for char in "?!,.:;()": limpia = limpia.replace(char, "")
    ruido = {"buscando", "quiero", "necesito", "tienen", "venden", "tenes", "podes", "precio", "cuanto", "sale"}
    palabras_clave = [p for p in limpia.split() if p not in ruido and len(p) >= 3]
    if not palabras_clave: return ""
    try:
        conn = sqlite3.connect(DB_PATH); c = conn.cursor(); res = []
        filtros = ["nombre LIKE ?" for _ in palabras_clave]; params = [f"%{p}%" for p in palabras_clave]
        c.execute(f"SELECT nombre, precio FROM productos WHERE {' AND '.join(filtros)} LIMIT 10", params)
        res.extend(c.fetchall())
        conn.close()
        unique_res = list(dict.fromkeys(res))[:15]
        return "\n".join([f"- {r[0]}: ${r[1]:,.0f}" for r in unique_res])
    except: return ""

raw_keys = os.getenv("GOOGLE_API_KEYS") or os.getenv("GOOGLE_API_KEY") or ""
LISTA_LLAVES = [k.strip() for k in raw_keys.split(",") if k.strip()]

async def generar_respuesta(mensaje_usuario, historial):
    model_names = ["gemini-flash-latest", "gemini-1.5-flash"]
    contexto = buscar_en_el_catalogo(mensaje_usuario)

    # 🏹 IDENTIDAD FERRETERA 9.0 (RELOJ SUIZO) 
    system_prompt = f"""
Sos el experto de mostrador de 'Ferretería El Indio'. ULTRA-CONCISO. 

HORARIOS SAGRADOS (No inventes otros nunca):
- Lunes a Viernes: 8:00 a 18:00 (largo).
- Sábados: 9:00 a 14:00.
- Domingos y Feriados: 9:00 a 13:00.

MOSTRADOR REAL:
1. TONO: Amigable, de barrio, respetuoso pero sin vueltas.
2. SIN SPAM: Si en el historial ya hubo un saludo reciente, NO saludéis de nuevo. Andá directo a la respuesta.
3. ARIEL REPARACIONES: 10 días hábiles aprox. Traer la máquina al local.
4. INDIO II: Carola Lorenzini 1261 (Agus y Ciro). Solo si preguntan ubicación.
5. PAGOS: Efectivo o transferencia (Alias: elindioferreteria.mp - Daiana Astrid Pereyra).
6. ENVÍOS: 'Te dejo con los encargados y en un rato te contestamos, gracias'.
7. FOTOS: 'Mandame foto así te asesoro mejor'.
8. MAPA: NO mandes ubicación a menos que digan 'donde estan', 'como llego' o 'ubicacion'.

CONSEJOS (De los chats reales):
- Varilla roscada 3/16 es la más fina.
- Discos de sensitiva: Omaha es el caballito de batalla.

DATOS CATÁLOGO:
{contexto if contexto else "Sin stock específico. Consultame en el local."}
""".strip()

    for api_key in LISTA_LLAVES:
        try:
            genai.configure(api_key=api_key)
            for name in model_names:
                try:
                    model = genai.GenerativeModel(name)
                    # Tomamos el historial para ver si ya saludamos
                    hist_text = "\n".join([f"{'Bot' if m.get('role')=='assistant' else 'Cliente'}: {m.get('content')}" for m in (historial[-5:] if historial else [])])
                    response = await model.generate_content_async(f"{system_prompt}\n\n{hist_text}\n\nCliente: {mensaje_usuario}")
                    if response and hasattr(response, 'text') and response.text:
                        return response.text
                except: continue
        except: continue
    return "¡Buenas! ¿Qué estás necesitando hoy?"
