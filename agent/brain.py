# agent/brain.py — El Indio 10.0 (CON OÍDOS Y GOOGLE) 🏹🎙️🤫🦾💎✨🦾
import os, logging, asyncio, datetime, sqlite3, httpx, time
import google.generativeai as genai

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
        conn = sqlite3.connect(DB_PATH); c = conn.cursor()
        filtros = ["nombre LIKE ?" for _ in palabras_clave]; params = [f"%{p}%" for p in palabras_clave]
        c.execute(f"SELECT nombre, precio FROM productos WHERE {' AND '.join(filtros)} LIMIT 10", params)
        res = c.fetchall(); conn.close()
        return "\n".join([f"- {r[0]}: ${r[1]:,.0f}" for r in res])
    except: return ""

raw_keys = os.getenv("GOOGLE_API_KEYS") or os.getenv("GOOGLE_API_KEY") or ""
LISTA_LLAVES = [k.strip() for k in raw_keys.split(",") if k.strip()]

async def generar_respuesta(input_user, historial):
    contexto_catalog = buscar_en_el_catalogo(input_user)
    
    # 🏹 IDENTIDAD EXPERTA 10.0
    system_prompt = f"""
Sos el experto de mostrador de 'Ferretería El Indio'. ULTRA-CONCISO. 

SABIDURÍA SEMÁNTICA (Si el cliente tiene un problema, buscá la solución técnica):
- 'Agujero en el techo' -> Membrana en pasta, Sellador Sikaflex, Cinta autoadhesiva.
- 'Se rompió el caño' -> Unión doble, Pegamento PVC (depende el material).
- 'Fierros de silla' -> Disco de corte Fino (115mm o 4 1/2).

HORARIOS: Lun-Vie 8-18, Sab 9-14, Dom/Fer 9-13.
LOCALES: Indio I (Calle Central) e Indio II (Carola Lorenzini 1261).
PAGOS: Efectivo o Alias: elindioferreteria.mp

TU PROTOCOLO:
1. Escuchá/Leé el problema.
2. Traducilo a un producto técnico.
3. Chequeá precios en el catálogo.
4. Respondé MUY CORTO y amigable.

PRODUCTOS RECIENTES (Consultá si alguno le sirve):
{contexto_catalog if contexto_catalog else "Sin stock rápido. Consultá en el local."}
""".strip()

    for api_key in LISTA_LLAVES:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
            
            # 🎙️ MANEJO DE AUDIOS
            if "[AUDIO_LINK:" in input_user:
                audio_url = input_user.split("[AUDIO_LINK:")[1].split("]")[0]
                logger.info(f"🎙️ Bajando audio para Gemini: {audio_url}")
                async with httpx.AsyncClient() as client:
                    resp = await client.get(audio_url)
                    if resp.status_code == 200:
                        audio_data = resp.content
                        audio_part = {'mime_type': 'audio/ogg', 'data': audio_data}
                        response = await model.generate_content_async([system_prompt, audio_part, f"Chat: {input_user}"])
                        if response and response.text: return response.text
                continue # Si falla audio, salta a la prox llave o intento

            # 📝 MANEJO DE TEXTO
            hist_text = "\n".join([f"{'Bot' if m.get('role')=='assistant' else 'Cliente'}: {m.get('content')}" for m in (historial[-5:] if historial else [])])
            response = await model.generate_content_async(
                contents=f"{system_prompt}\n\n{hist_text}\n\nCliente: {input_user}",
                # Grounding con búsqueda de Google para mayor inteligencia
                tools=[{'google_search_retrieval': {'dynamic_retrieval_config': {'mode': 'unspecified', 'dynamic_threshold': 0.0}}}]
            )
            
            if response and response.text: return response.text
        except Exception as e:
            logger.error(f"Error Brain 10.0: {e}")
            continue
    return "¡Hola genio! ¿En qué te puedo asesorar hoy? Mandame foto o audio si querés."
