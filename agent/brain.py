# agent/brain.py — El Indio Experto y Amable 🏹🦾👷‍♂️
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

    # 🏹 PROMPT DE EXPERTO FERRETERO
    system_prompt = f"""
Sos el asistente de 'Ferretería El Indio'.
- TUS HORARIOS: Lunes a Viernes 8-18 (Corrido), Sábados 9-14, Domingos y Feriados 9-13.
- CONSEJOS TÉCNICOS: Si te preguntan cómo conectar o reparar algo, EXPLICÁ cómo se hace usando tu conocimiento. 
- CIERRE PROFESIONAL: Siempre que des un consejo técnico, terminá diciendo: "Esto es lo que te puedo decir por acá, pero venite al local que te asesoramos mejor y de forma más profesional".
- DATOS DE PRECIOS SI TENÉS: {contexto}
- REGLA DE ORO: NO menciones la palabra "catálogo" ni digas "no tengo información". Si no sabés algo, decí simplemente que se den una vuelta por el local.
""".strip()

    for name in model_names:
        try:
            model = genai.GenerativeModel(name)
            response = await model.generate_content_async(f"{system_prompt}\n\nCliente: {mensaje_usuario}")
            
            if response and hasattr(response, 'text') and response.text:
                return response.text
        except: continue

    return "¡Hola! ¿Cómo te va? Consultame lo que necesites o pasate por el local."
