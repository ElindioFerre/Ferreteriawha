# agent/brain.py — El Indio 11.8 (ULTRA ESTABLE) 🏹🛡️🦾💎✨🦾
import os, logging, sqlite3, httpx
from google.genai import Client, types

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
        c.execute(f"SELECT nombre, precio FROM productos WHERE {' AND '.join(filtros)} LIMIT 5", params)
        res = c.fetchall(); conn.close()
        return "\n".join([f"- {r[0]}: ${r[1]:,.0f}" for r in res])
    except: return ""

raw_keys = os.getenv("GOOGLE_API_KEYS") or os.getenv("GOOGLE_API_KEY") or ""
LISTA_LLAVES = [k.strip() for k in raw_keys.split(",") if k.strip()]

async def generar_respuesta(input_user, historial):
    system_prompt = "Sos el experto de Ferretería El Indio. Ultra-conciso. Da consejos técnicos y busca precios."
    
    for api_key in LISTA_LLAVES:
        try:
            # 🏹 CLIENTE ESTABLE (Sin forzar v1, para que el SDK use su mejor via)
            client = Client(api_key=api_key)
            model_id = "gemini-1.5-flash"
            
            # 🎙️ AUDIO -> TEXTO
            if "[AUDIO_LINK:" in input_user:
                url = input_user.split("[AUDIO_LINK:")[1].split("]")[0]
                async with httpx.AsyncClient() as h_client:
                    resp = await h_client.get(url)
                    if resp.status_code == 200:
                        part = types.Part.from_bytes(data=resp.content, mime_type="audio/ogg")
                        t_res = client.models.generate_content(model=model_id, contents=[part, "Transcribe este audio."])
                        if t_res and t_res.text: input_user = t_res.text

            # 📸 VISIÓN
            ctx_img = ""
            if "[IMAGE_LINK:" in input_user:
                url = input_user.split("[IMAGE_LINK:")[1].split("]")[0]
                async with httpx.AsyncClient() as h_client:
                    resp = await h_client.get(url)
                    if resp.status_code == 200:
                        part = types.Part.from_bytes(data=resp.content, mime_type="image/jpeg")
                        v_res = client.models.generate_content(model=model_id, contents=[part, "Qué pieza es esta?"])
                        if v_res and v_res.text: ctx_img = f"\nINFO FOTO: Es un {v_res.text}"

            # 🕵️‍♂️ BÚSQUEDA Y RESPUESTA (Tools Fix)
            contexto_cat = buscar_en_el_catalogo(input_user)
            config = types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())]
            )
            
            prompt_final = f"{system_prompt}\n{ctx_img}\nDATOS LOCAL:\n{contexto_cat}\n\nCliente: {input_user}"
            response = client.models.generate_content(model=model_id, contents=prompt_final, config=config)
            
            if response and response.text: return response.text
        except Exception as e:
            logger.error(f"Error Brain 11.8: {e}")
            continue
    return "¡Hola genio! ¿En qué te asesoro hoy?"
