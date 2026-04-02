# agent/brain.py — Versión SIMPLE Y NATURAL 🏹🦾⚡
import os, logging, asyncio, google.generativeai as genai
from agent.tools import buscar_precio

logger = logging.getLogger("agentkit")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

async def generar_respuesta(mensaje_usuario, historial):
    # 🏹 Usamos el modelo que ya sabemos que pega
    model_names = ["gemini-flash-latest", "gemini-1.5-flash", "gemini-pro"]
    
    contexto = ""
    try:
        if len(mensaje_usuario) > 3:
            contexto = buscar_precio(mensaje_usuario)
            if "no se encontró" in contexto.lower() or "sin resultados" in contexto.lower():
                contexto = ""
    except: pass

    # 🏹 PROMPT MINIMALISTA Y PROFESIONAL
    system_prompt = f"""
Sos el asistente de 'Ferretería El Indio'. 
- Sé directo y amable. 
- Respondé en máximo 2 frases. Cortito.
- NO repitas los horarios a menos que te pregunten.
- NO digas 'Soy el dueño' ni 'Soy la IA'. 
- Si no tenés la respuesta, decí que consulten en el local.
- DATOS DE PRECIOS SI TENÉS: {contexto}
""".strip()

    for name in model_names:
        try:
            model = genai.GenerativeModel(name)
            response = await model.generate_content_async(f"{system_prompt}\n\nCliente: {mensaje_usuario}")
            
            if response and hasattr(response, 'text') and response.text:
                return response.text
        except: continue

    return "¡Hola! ¿En qué te puedo ayudar hoy?"
