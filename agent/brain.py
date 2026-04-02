# agent/brain.py — Versión ULTRA-COMPATIBLE 🏹🦾🛡️⚡
import os, logging, asyncio, google.generativeai as genai
from agent.tools import buscar_precio

logger = logging.getLogger("agentkit")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

async def generar_respuesta(mensaje_usuario, historial):
    # 🏹 LISTA AGRESIVA DE MODELOS (Si uno falla, salta al otro al toque)
    model_names = [
        "gemini-1.5-flash", 
        "gemini-flash-latest", 
        "gemini-2.0-flash", 
        "gemini-pro", 
        "gemini-pro-latest"
    ]
    
    contexto = ""
    try:
        if len(mensaje_usuario) > 3:
            contexto = buscar_precio(mensaje_usuario)
    except: pass

    system_prompt = f"Eres el asistente de Ferretería El Indio. Horarios: L-V 8-18, Sab 9-14, Dom 9-13. Sé amable. Datos: {contexto}"
    
    for name in model_names:
        try:
            logger.info(f"🤖 Probando con: {name}...")
            model = genai.GenerativeModel(name)
            
            # 🚀 LLAMADA ASYNC
            response = await model.generate_content_async(f"{system_prompt}\n\nCliente: {mensaje_usuario}")
            
            if response and hasattr(response, 'text') and response.text:
                logger.info(f"✅ ¡PEGÓ EL MODELO: {name}!")
                return response.text
                
        except Exception as e:
            error_str = str(e).lower()
            if "404" in error_str:
                logger.warning(f"🚫 {name} no encontrado, saltando...")
                continue
            if "429" in error_str:
                logger.warning(f"⚠️ {name} sin cuota, esperando 2s...")
                await asyncio.sleep(2)
                continue
            
            logger.error(f"❌ Error en {name}: {e}")
            continue

    return "¡Hola amigo! Aguantame un segundo que estoy buscando el catálogo. ¿Qué me decías del Indio?"
