# agent/brain.py — El Indio 11.0 EXPERTO (OJOS Y MOSTRADOR) 🏹📸🎙️🌀🦾💎✨🦾
import os, logging, asyncio, sqlite3, httpx, time
import google.generativeai as genai

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
    
    # 🏹 IDENTIDAD EXPERTA 11.0
    system_prompt = f"""
Sos el experto de mostrador de 'Ferretería El Indio'. 🏹🛡️🦾

REGLA DE CARRO (Mostrador Virtual):
- Si el cliente confirma querer productos (ej: 'dale', 'reservame', 'llevo'), generá un RESUMEN:
  'Dale joya, te separo: 
  - [Producto X] - $[Precio]
  - [Producto Y] - $[Precio]
  Total: $[Suma]
  ¿Pasás por Indio I o II?'

VISIÓN (Si hay foto):
- Identificá la pieza (tornillo, repuesto, marca, medida).
- SI NO ESTÁS SEGURO: 'Che, no llego a ver bien la medida o la rosca en la foto. ¿Me pasás una más de cerca o del otro lado?'
- SI ESTÁS SEGURO: 'Eso es un [Nombre del Repuesto]. Tenemos [Opciones].'

DATOS ÚTILES:
- Alias: elindioferreteria.mp
- Ariel Reparaciones: 10 días hábiles.
- Indio II: Carola Lorenzini 1261.

PRODUCTOS RECIENTES:
{contexto_catalog if contexto_catalog else "Sin stock rápido. Consultame en el local."}
""".strip()

    for api_key in LISTA_LLAVES:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
            
            # 📸 MANEJO DE FOTOS (OJOS)
            if "[IMAGE_LINK:" in input_user:
                img_url = input_user.split("[IMAGE_LINK:")[1].split("]")[0]
                logger.info(f"📸 Analizando imagen para Gemini...")
                async with httpx.AsyncClient() as client:
                    resp = await client.get(img_url)
                    if resp.status_code == 200:
                        img_part = {'mime_type': 'image/jpeg', 'data': resp.content}
                        response = await model.generate_content_async([system_prompt, img_part, f"Analizame esta foto y decime qué es."])
                        if response and response.text: return response.text
                continue

            # 🎙️ MANEJO DE AUDIOS
            if "[AUDIO_LINK:" in input_user:
                audio_url = input_user.split("[AUDIO_LINK:")[1].split("]")[0]
                async with httpx.AsyncClient() as client:
                    resp = await client.get(audio_url)
                    if resp.status_code == 200:
                        audio_part = {'mime_type': 'audio/ogg', 'data': resp.content}
                        response = await model.generate_content_async([system_prompt, audio_part, f"Escuchá y respondé."])
                        if response and response.text: return response.text
                continue

            # 📝 TEXTO + GOOGLE GROUNDING
            hist_text = "\n".join([f"{'Bot' if m.get('role')=='assistant' else 'Cliente'}: {m.get('content')}" for m in (historial[-5:] if historial else [])])
            response = await model.generate_content_async(
                contents=f"{system_prompt}\n\n{hist_text}\n\nCliente: {input_user}",
                tools=[{'google_search_retrieval': {'dynamic_retrieval_config': {'mode': 'unspecified', 'dynamic_threshold': 0.0}}}]
            )
            
            if response and response.text: return response.text
        except Exception as e:
            logger.error(f"Error Brain 11.0: {e}")
            continue
    return "¡Hola genio! ¿En qué te puedo asesorar hoy? Mandame foto, audio o consultame el precio de lo que buscás."
