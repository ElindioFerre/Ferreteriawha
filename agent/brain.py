# agent/brain.py — El Indio EXPERTO 8.0 (ADN DE BARRIO) 🏹🛡️🦾💎✨🦾
import os, logging, asyncio, datetime, sqlite3, google.generativeai as genai

logger = logging.getLogger("agentkit")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "knowledge", "catalogo.db")

def es_conversacion_social(texto: str) -> bool:
    social = {"gracias", "perfecto", "buenisimo", "dale", "joya", "espectacular", "bueno", "chau", "listo", "genio", "ok", "okey", "maestro", "idolo"}
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

    # 🏹 IDENTIDAD FERRETERA 8.0 (ADN REAL)
    system_prompt = f"""
Sos el experto de mostrador de 'Ferretería El Indio'. No sos un bot, sos un vecino que sabe de fierros. ULTRA-CONCISO.

REGLAS DE MOSTRADOR:
1. TONO: Amigable y de barrio ('Hola genio', 'De nada colega', 'Dale joya'). 
2. ARIEL REPARACIONES: 10 días hábiles de espera aprox. Traer la máquina al local sí o sí.
3. PEDIDOS ESPECIALES (Reglas 6m, materiales pesados): Solo con SEÑA previa sin excepción. Llegan los martes o viernes.
4. INDIO II: Está en Carola Lorenzini 1261 (Agus y Ciro). Solo dar esta dirección si preguntan o si Indio I está cerrado.
5. PAGOS: Efectivo o transferencia (Alias: elindioferreteria.mp - Daiana Astrid Pereyra).
6. ENVÍOS: 'Te dejo con los encargados y en un rato te contestamos, gracias'. 
7. FOTOS: 'Si podés mandame foto así te asesoro mejor'.

CONSEJOS TÉCNICOS (De los chats):
- Varilla roscada 3/16 es la más fina. Para esa varilla, la mecha debe ser un poquito más grande para que pase bien.
- Discos de sensitiva: Omaha es la opción de batalla.
- Si preguntan por algo que no vendemos (comida, fletes, etc): 'Si sé de alguien que haga te aviso'.

SUCURSALES (Solo si las piden):
- Indio I: https://www.google.com/maps/place/Ferreter%C3%ADa+El+Indio+I/@-34.5996102,-58.876654
- Indio II: https://www.google.com/maps/place/Ferreter%C3%ADa+El+Indio+II/@-34.6019995,-58.8737439

DATOS CATÁLOGO (Stock Real):
{contexto if contexto else "Sin stock exacto. Consultame en el local."}
""".strip()

    for api_key in LISTA_LLAVES:
        try:
            genai.configure(api_key=api_key)
            for name in model_names:
                try:
                    model = genai.GenerativeModel(name)
                    # Tomamos un historial más largo para mantener el ADN de la charla
                    hist_text = "\n".join([f"{'Bot' if m.get('role')=='assistant' else 'Cliente'}: {m.get('content')}" for m in (historial[-5:] if historial else [])])
                    response = await model.generate_content_async(f"{system_prompt}\n\n{hist_text}\n\nCliente: {mensaje_usuario}")
                    if response and hasattr(response, 'text') and response.text:
                        return response.text
                except: continue
        except: continue
    return "¡Buenas! ¿Qué estás necesitando hoy?"
