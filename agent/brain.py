# agent/brain.py — Versión DEFINITIVA 🏹🦾
import os, logging, google.generativeai as genai
from agent.tools import buscar_precio

logger = logging.getLogger("agentkit")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

async def generar_respuesta(mensaje_usuario, historial):
    # 🏹 USAMOS TUS NOMBRES REALES (Sacados del espía)
    model_names = ["gemini-flash-latest", "gemini-2.0-flash", "gemini-pro-latest"]
    
    contexto = ""
    try:
        if len(mensaje_usuario) > 3:
            contexto = buscar_precio(mensaje_usuario)
    except: pass

    system_prompt = f"Eres el asistente de Ferretería El Indio. Amable y directo. Usa 'Hola' o 'Amigo'. Datos: {contexto}"
    
    for name in model_names:
        try:
            logger.info(f"Intentando con tu modelo: {name}")
            model = genai.GenerativeModel(name)
            response = model.generate_content(f"{system_prompt}\n\nCliente: {mensaje_usuario}")
            
            if response and response.text:
                logger.info(f"✅ ¡POR FIN! Pegó el modelo: {name}")
                return response.text
        except Exception as e:
            logger.warning(f"❌ El modelo {name} no quiso: {e}")
            continue 

    return "¡Hola amigo! Aguantame un toque que se me llenó el mostrador. ¿Qué buscabas?"
