# agent/brain.py — Optimización de Velocidad 🏹🦾⚡
import os, logging, asyncio, google.generativeai as genai
from agent.tools import buscar_precio

logger = logging.getLogger("agentkit")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

async def generar_respuesta(mensaje_usuario, historial):
    # 🏹 Ponemos el 8b PRIMERO para evitar el peaje de Google
    model_names = [
        "gemini-1.5-flash-8b",
        "gemini-1.5-flash",
        "gemini-flash-latest",
        "gemini-pro"
    ]
    
    contexto = ""
    try:
        if len(mensaje_usuario) > 3:
            contexto = buscar_precio(mensaje_usuario)
            if "no se encontró" in contexto.lower() or "sin resultados" in contexto.lower():
                contexto = ""
    except: pass

    system_prompt = f"Sos el asistente de 'Ferretería El Indio'. Horarios: L-V 8-18, Sáb 9-14, Dom/Fer 9-13. Sé breve y amable. Datos: {contexto}"

    for name in model_names:
        intentos = 0
        while intentos < 2:
            try:
                model = genai.GenerativeModel(name)
                response = await model.generate_content_async(f"{system_prompt}\n\nCliente: {mensaje_usuario}")
                if response and hasattr(response, 'text') and response.text:
                    return response.text
            except Exception as e:
                if "429" in str(e) or "quota" in str(e).lower():
                    logger.warning(f"⏳ Esperando peaje de Google ({name})...")
                    await asyncio.sleep(4)
                    intentos += 1
                    continue
                break
    return "¡Hola! Dame un toque que el mostrador está lleno. ¿Qué necesitabas?"
