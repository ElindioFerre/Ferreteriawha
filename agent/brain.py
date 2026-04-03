# agent/brain.py — El Indio 11.2 (SUPER ESTABLE - GOOGLE GENAI) 🏹🛡️🦾💎✨🦾
import os, logging, asyncio, sqlite3, httpx, time
from google import genai
from google.genai import types

logger = logging.getLogger("agentkit")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "knowledge", "catalogo.db")

def buscar_en_el_catalogo(consulta: str) -> str:
    if not os.path.exists(DB_PATH): return ""
    limpia = consulta.lower()
    for char in "?!,.:;()": limpia = limpia.replace(char, "")
    keywords = [p for p in limpia.split() if len(p) >= 3]
    if not keywords: return ""
    try:
        conn = sqlite3.connect(DB_PATH); c = conn.cursor()
        filtros = ["nombre LIKE ?" for _ in keywords]; params = [f"%{p}%" for p in keywords]
        c.execute(f"SELECT nombre, precio FROM productos WHERE {' AND '.join(filtros)} LIMIT 10", params)
        res = c.fetchall(); conn.close()
        return "\n".join([f"- {r[0]}: ${r[1]:,.0f}" for r in res])
    except: return ""

raw_keys = os.getenv("GOOGLE_API_KEYS") or os.getenv("GOOGLE_API_KEY") or ""
LISTA_LLAVES = [k.strip() for k in raw_keys.split(",") if k.strip()]

async def generar_respuesta(input_user, historial):
    contexto_catalog = buscar_en_el_catalogo(input_user)
    
    # 🏹 IDENTIDAD EXPERTA (ADN BARRIO 11.2)
    system_prompt = f"""
Sos el experto de mostrador de 'Ferretería El Indio'. ULTRA-CONCISO. 🏹🛡️🦾

REGLA DE CARRO (Mostrador Virtual):
- Si el cliente confirma querer algo: 'Dale joya, te separo: [Producto] - $[Precio]. ¿Pasás por Indio I o II?'

VISIÓN (Si hay foto):
- Identificá la pieza. Si no estás seguro, pedí otra foto mejor ('No llego a ver bien la rosca genio, mandame otra de cerca'). No inventes.

DATOS:
- Horarios: Lun-Vie 8-18, Sab 9-14, Dom/Fer 9-13.
- Indio II: Carola Lorenzini 1261.
- Alias de pago: elindioferreteria.mp

PRODUCTOS RECIENTES:
{contexto_catalog if contexto_catalog else "Sin stock rápido. Consultame en el local."}
""".strip()

    for api_key in LISTA_LLAVES:
        try:
            # 🏹 CLIENTE OFICIAL DE GOOGLE GENAI
            client = genai.Client(api_key=api_key)
            model_id = "gemini-1.5-flash"
            
            # 📸 MANEJO DE FOTOS (OJOS)
            if "[IMAGE_LINK:" in input_user:
                img_url = input_user.split("[IMAGE_LINK:")[1].split("]")[0]
                logger.info(f"📸 Procesando visión...")
                async with httpx.AsyncClient() as client_http:
                    resp = await client_http.get(img_url)
                    if resp.status_code == 200:
                        image = types.Part.from_bytes(data=resp.content, mime_type="image/jpeg")
                        response = client.models.generate_content(
                            model=model_id,
                            contents=[system_prompt, image, "Identifica el repuesto de ferretería en la foto."]
                        )
                        if response and response.text: return response.text
                continue

            # 🎙️ MANEJO DE AUDIOS (OÍDOS)
            if "[AUDIO_LINK:" in input_user:
                audio_url = input_user.split("[AUDIO_LINK:")[1].split("]")[0]
                logger.info(f"🎙️ Procesando audio...")
                async with httpx.AsyncClient() as client_http:
                    resp = await client_http.get(audio_url)
                    if resp.status_code == 200:
                        audio = types.Part.from_bytes(data=resp.content, mime_type="audio/ogg")
                        response = client.models.generate_content(
                            model=model_id,
                            contents=[system_prompt, audio, "Responde al cliente basándote en su audio."]
                        )
                        if response and response.text: return response.text
                continue

            # 📝 TEXTO Y GROUNDING
            hist_text = "\n".join([f"{'Bot' if m.get('role')=='assistant' else 'Cliente'}: {m.get('content')}" for m in (historial[-5:] if historial else [])])
            config = types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearchGrounding())]
            )
            
            response = client.models.generate_content(
                model=model_id,
                contents=f"{system_prompt}\n\n{hist_text}\n\nCliente: {input_user}",
                config=config
            )
            
            if response and response.text: return response.text
        except Exception as e:
            logger.error(f"Error Brain 11.2 (GenAI): {e}")
            continue
    return "¡Hola genio! ¿Qué estás necesitando hoy? Mandame foto, audio o consultame el precio de lo que buscás."
