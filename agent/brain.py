# agent/brain.py — Motor de Multicilindrada (Rotación de Llaves) 🏹🚀🦾⚡
import os, logging, asyncio, google.generativeai as genai
from agent.tools import buscar_precio

logger = logging.getLogger("agentkit")

# 🏹 CARGAMOS TODAS LAS LLAVES (Soporta múltiples llaves separadas por coma)
raw_keys = os.getenv("GOOGLE_API_KEYS") or os.getenv("GOOGLE_API_KEY") or ""
LISTA_LLAVES = [k.strip() for k in raw_keys.split(",") if k.strip()]

async def generar_respuesta(mensaje_usuario, historial):
    model_names = ["gemini-flash-latest", "gemini-1.5-flash", "gemini-pro"]
    
    contexto = ""
    try:
        if len(mensaje_usuario) > 3:
            contexto = buscar_precio(mensaje_usuario)
            if "no se encontró" in contexto.lower(): contexto = ""
    except: pass

    system_prompt = f"Sos el asistente experto de 'Ferretería El Indio'. Horarios: L-V 8-18 (Corrido), Sáb 9-14, Dom/Fer 9-13. Ayudá con consejos técnicos. Datos: {contexto}"

    # 🏹 CAMBIAMOS DE LLAVE SI LA ACTUAL SE AGOTA
    for api_key in LISTA_LLAVES:
        try:
            genai.configure(api_key=api_key)
            
            for name in model_names:
                try:
                    model = genai.GenerativeModel(name)
                    response = await model.generate_content_async(f"{system_prompt}\n\nCliente: {mensaje_usuario}")
                    if response and hasattr(response, 'text') and response.text:
                        return response.text
                except Exception as e:
                    error_msg = str(e).lower()
                    if "429" in error_msg or "quota" in error_msg:
                        logger.warning(f"⏳ Llave agotada... Saltando a la siguiente...")
                        # Salta al siguiente api_key
                        break 
                    if "404" in error_msg:
                        continue # Prueba el siguiente modelo con la misma llave
                    break # Error desconocido, saltamos llave
        except:
            continue

    return "¡Hola! Estoy con mucha gente en el mostrador. Aguantame un segundo y preguntame de nuevo."
