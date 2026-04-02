# agent/brain.py — El Indio HUMANO 🏹🤠🦾⚡
import os, logging, asyncio, google.generativeai as genai
from agent.tools import buscar_precio

logger = logging.getLogger("agentkit")

raw_keys = os.getenv("GOOGLE_API_KEYS") or os.getenv("GOOGLE_API_KEY") or ""
LISTA_LLAVES = [k.strip() for k in raw_keys.split(",") if k.strip()]

async def generar_respuesta(mensaje_usuario, historial):
    model_names = ["gemini-flash-latest", "gemini-1.5-flash", "gemini-pro"]
    
    contexto = ""
    try:
        # 🏹 FILTRO DE HUMANIDAD: Si el mensaje es muy corto (saludos), no buscamos nada.
        # Solo buscamos si el mensaje tiene más de 4 letras y no es un simple saludo.
        if len(mensaje_usuario) > 4 and mensaje_usuario.lower() not in ["hola", "buen día", "buenas"]:
            contexto = buscar_precio(mensaje_usuario)
            # Limpiamos el contexto para que no "contamine" la respuesta con frases robóticas
            if "no encontr" in contexto.lower(): contexto = ""
    except: pass

    # 🏹 PROMPT DE "FERRETERO DE BARRIO":
    system_prompt = f"""
Sos el dueño de 'Ferretería El Indio'. Hablá como una persona real, amable y experta.
- SIEMPRE respondé de forma NATURAL (ej: "Hola, ¿cómo va?", "Qué hacés amigo, todo bien?").
- NUNCA menciones la palabra "catálogo", "término", "búsqueda" ni "base de datos". 
- Si no tenés un precio exacto abajo, usá tu conocimiento general de IA para ayudar.
- HORARIOS (Solo si los piden): L-V 8-18 (Corrido), Sáb 9-14, Dom/Fer 9-13.
- DATOS (Si hay algo útil acá, usalo): {contexto}
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

    return "¡Hola! ¿Cómo andás? Decime qué andás necesitando para el hogar o la obra."
