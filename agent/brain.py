# agent/brain.py — Versión con modelos de respaldo 🏹🛡️
import os, logging, google.generativeai as genai
from agent.tools import buscar_precio

logger = logging.getLogger("agentkit")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

async def generar_respuesta(mensaje_usuario, historial):
    # Probamos con estos nombres por orden hasta que uno pegue
    model_names = ["gemini-1.5-flash", "gemini-pro"]
    
    contexto = ""
    if len(mensaje_usuario) > 3:
        try: contexto = buscar_precio(mensaje_usuario)
        except: pass

    system_prompt = f"Eres el asistente de Ferretería El Indio. Amable y directo. Datos: {contexto}"
    
    for name in model_names:
        try:
            logger.info(f"Probando modelo: {name}")
            model = genai.GenerativeModel(name)
            response = model.generate_content(f"{system_prompt}\n\nCliente: {mensaje_usuario}")
            
            if response and response.text:
                logger.info(f"✅ ÉXITO con el modelo: {name}")
                return response.text
        except Exception as e:
            logger.warning(f"❌ Falló {name}: {e}")
            continue # Si falla uno, prueba el siguiente

    return "¡Hola amigo! Dame un segundo que estoy con mucha gente en el mostrador. ¿Qué necesitabas?"
