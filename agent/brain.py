# agent/brain.py — El Indio 11.6 (V1 STABLE) 🏹🛡️🦾💎✨🦾
import os, logging, asyncio, sqlite3, httpx, time
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
        c.execute(f"SELECT nombre, precio FROM productos WHERE {' AND '.join(filtros)} LIMIT 10", params)
        res = c.fetchall(); conn.close()
        return "\n".join([f"- {r[0]}: ${r[1]:,.0f}" for r in res])
    except: return ""

raw_keys = os.getenv("GOOGLE_API_KEYS") or os.getenv("GOOGLE_API_KEY") or ""
LISTA_LLAVES = [k.strip() for k in raw_keys.split(",") if k.strip()]

async def generar_respuesta(input_user, historial):
    system_prompt_base = f"""
Sos el experto de mostrador de 'Ferretería El Indio'. ULTRA-CONCISO Y SIMPLIFICADO. 🏹🛡️🦾

TU MISIÓN COMO ASESOR:
1. Si te preguntan 'CÓMO HACER ALGO': Buscá en Google y explicá la solución técnica cortito y al pie, como un ferretero de barrio.
2. Simplificá todo lo que diga Google. Tirá el consejo útil de frente.
3. Al final, decí si tenemos los materiales repasando tu lista rápida.

REGLA DE CARRO (Mostrador Virtual): Confirmá pedidos con precio y reserva.

MÁS INFO: Lun-Vie 8-18, Sab 9-14, Dom/Fer 9-13. Indio II: Carola Lorenzini 1261. Alias: elindioferreteria.mp
""".strip()

    for api_key in LISTA_LLAVES:
        try:
            # 🏹 FORZAMOS LA VERSIÓN ESTABLE V1 PARA EVITAR EL 404
            client = Client(api_key=api_key, http_options={"api_version": "v1"})
            model_id = "gemini-1.5-flash"
            
            # 🎙️ TRANSCRIPCIÓN
            if "[AUDIO_LINK:" in input_user:
                audio_url = input_user.split("[AUDIO_LINK:")[1].split("]")[0]
                async with httpx.AsyncClient() as client_http:
                    resp = await client_http.get(audio_url)
                    if resp.status_code == 200:
                        audio_part = types.Part.from_bytes(data=resp.content, mime_type="audio/ogg")
                        t_resp = client.models.generate_content(
                            model=model_id,
                            contents=[audio_part, "Traduci este audio a texto de ferretería."]
                        )
                        if t_resp and t_resp.text: input_user = t_resp.text

            # 📸 VISIÓN
            contexto_adicional = ""
            if "[IMAGE_LINK:" in input_user:
                img_url = input_user.split("[IMAGE_LINK:")[1].split("]")[0]
                async with httpx.AsyncClient() as client_http:
                    resp = await client_http.get(img_url)
                    if resp.status_code == 200:
                        image = types.Part.from_bytes(data=resp.content, mime_type="image/jpeg")
                        v_resp = client.models.generate_content(model=model_id, contents=[image, "Identifica este repuesto."])
                        if v_resp and v_resp.text:
                            contexto_adicional = f"\nINFO IMAGEN: El cliente mando foto de: {v_resp.text}"

            # 🕵️‍♂️ FINAL
            contexto_catalog = buscar_en_el_catalogo(input_user)
            prompt_final = f"{system_prompt_base}\n{contexto_adicional}\n\nCATÁLOGO:\n{contexto_catalog if contexto_catalog else 'Sin stock inmediato.'}"
            
            config = types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearchGrounding())]
            )
            
            response = client.models.generate_content(
                model=model_id,
                contents=f"{prompt_final}\n\nCliente: {input_user}",
                config=config
            )
            if response and response.text: return response.text
        except Exception as e:
            logger.error(f"Error Brain 11.6 (V1 Fix): {e}")
            continue
    return "¡Hola genio! ¿En qué te asesoro?"
