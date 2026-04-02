# agent/brain.py — Versión ASYNC TOTAL 🏹🦾⚡
import os, logging, asyncio, google.generativeai as genai
from agent.tools import buscar_precio

logger = logging.getLogger("agentkit")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

async def generar_respuesta(mensaje_usuario, historial):
    model_names = ["gemini-1.5-flash", "gemini-pro"]
    
    contexto = ""
    try:
        if len(mensaje_usuario) > 3:
            contexto = buscar_precio(mensaje_usuario)
    except: pass

    system_prompt = f"Eres el asistente de Ferretería El Indio. Horarios: L-V 8-18, Sab 9-14, Dom 9-13. Datos: {contexto}"
    
    for name in model_names:
        intentos = 0
        while intentos < 2: 
            try:
                logger.info(f"🤖 IA pensando con {name}...")
                model = genai.GenerativeModel(name)
                
                # 🏹 LLAMADA ASINCRÓNICA REAL
                response = await model.generate_content_async(f"{system_prompt}\n\nCliente: {mensaje_usuario}")
                
                if response and hasattr(response, 'text') and response.text:
                    logger.info(f"✅ IA respondió con {name}")
                    return response.text
                    
            except Exception as e:
                if "429" in str(e):
                    logger.warning(f"⚠️ Cuota agotada, esperando 3s...")
                    await asyncio.sleep(3)
                    intentos += 1
                    continue
                logger.error(f"❌ Error IA ({name}): {e}")
                break

    return "¡Hola amigo! Dame un toque que estoy buscando el catálogo. ¿Qué necesitabas?"
