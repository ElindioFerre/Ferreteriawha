# agent/brain.py — Con Detector de Errores 🕵️‍♂️🏹🦾
import os, logging, asyncio, google.generativeai as genai
from agent.tools import buscar_precio

logger = logging.getLogger("agentkit")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

async def generar_respuesta(mensaje_usuario, historial):
    model_names = ["gemini-flash-latest", "gemini-1.5-flash", "gemini-pro"]
    
    contexto = ""
    try:
        if len(mensaje_usuario) > 3:
            contexto = buscar_precio(mensaje_usuario)
            if "no se encontró" in contexto.lower() or "sin resultados" in contexto.lower():
                contexto = ""
    except: pass

    system_prompt = f""" Sos el asistente de 'Ferretería El Indio'. Horarios: Lunes a Viernes 8-18 (Corrido), Sábados 9-14, Domingos y Feriados 9-13. Si te preguntan cómo hacer algo, explicá y sugerí venir al local para asesoría profesional. Datos: {contexto} """.strip()

    for name in model_names:
        try:
            model = genai.GenerativeModel(name)
            response = await model.generate_content_async(f"{system_prompt}\n\nCliente: {mensaje_usuario}")
            
            if response and hasattr(response, 'text') and response.text:
                return response.text
                
        except Exception as e:
            # 👁️ ESTO NOS VA A DECIR POR QUÉ FALLA
            logger.error(f"❌ Error CRÍTICO en {name}: {e}")
            continue

    return "¡Hola! ¿Cómo va? Consultame lo que necesites o pasate por el local. (IA temporalmente ocupada)"
