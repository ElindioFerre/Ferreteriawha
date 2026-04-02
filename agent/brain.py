# agent/brain.py — Versión PAISANO 🤠🏹🦾
import os, logging, asyncio, google.generativeai as genai
from agent.tools import buscar_precio

logger = logging.getLogger("agentkit")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

async def generar_respuesta(mensaje_usuario, historial):
    model_names = ["gemini-1.5-flash", "gemini-flash-latest", "gemini-pro"]
    
    contexto = ""
    try:
        # 🏹 Solo buscamos en el catálogo si el mensaje es largo
        if len(mensaje_usuario) > 3:
            contexto = buscar_precio(mensaje_usuario)
            # Si la herramienta dice que no encontró nada, vaciamos el contexto 
            # para que la IA no se ponga pesada con el "no encontré nada".
            if "no encontré" in contexto.lower() or "sin resultados" in contexto.lower():
                contexto = ""
    except: pass

    # 🏹 PROMPT NUEVO: Más humano, menos robot.
    system_prompt = f"""
 Sos 'El Indio', el dueño de la Ferretería El Indio. 
 - Hablá de forma AMIGABLE y CERCANA. Usá palabras como 'amigo', 'campeón', 'compañero'.
 - NO digas 'No encontré información en el catálogo'. Si no sabés algo, solo decí 'Preguntame lo que necesites que te ayudo'.
 - TUS HORARIOS: L-V 8 a 18 (Cerrado al mediodía NO, corrido), Sáb 9 a 14, Dom 9 a 13.
 - DATOS DE PRECIOS SI TENÉS: {contexto}
 - Si alguien pregunta 'quiero saber algo', decile '¡Dale campeón! ¿Qué andás buscando? Preguntame lo que sea'.
""".strip()

    for name in model_names:
        try:
            model = genai.GenerativeModel(name)
            response = await model.generate_content_async(f"{system_prompt}\n\nCliente: {mensaje_usuario}")
            
            if response and hasattr(response, 'text') and response.text:
                return response.text
                
        except Exception as e:
            continue

    return "¡Hola amigo! ¿Qué andás necesitando para el hogar? ¿Buscas algún precio o herramienta?"
