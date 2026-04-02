# agent/brain.py — Superando el 429 de Google 🏹🦾🛡️
import os, logging, asyncio, google.generativeai as genai
from agent.tools import buscar_precio

logger = logging.getLogger("agentkit")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

async def generar_respuesta(mensaje_usuario, historial):
    # 🏹 Agregamos el "8b" que es más ligero y suele tener cuota propia
    model_names = [
        "gemini-1.5-flash",
        "gemini-1.5-flash-8b", 
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

    system_prompt = f"Sos el asistente de 'Ferretería El Indio'. Horarios: L-V 8-18, Sáb 9-14, Dom/Fer 9-13. Datos: {contexto}"

    for name in model_names:
        intentos = 0
        while intentos < 2:
            try:
                model = genai.GenerativeModel(name)
                response = await model.generate_content_async(f"{system_prompt}\n\nCliente: {mensaje_usuario}")
                
                if response and hasattr(response, 'text') and response.text:
                    return response.text
                    
            except Exception as e:
                error_str = str(e)
                if "429" in error_str:
                    logger.warning(f"⚠️ {name} sin cuota, esperando 5 segundos...")
                    await asyncio.sleep(5) # 🏹 Espera un poco más para que Google se calme
                    intentos += 1
                    continue
                break # Si es otro error (como 404), saltá al siguiente modelo

    return "¡Hola! Dame un segundito que el sistema está un poco lento. ¿Qué andás necesitando?"
