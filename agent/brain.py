# agent/brain.py — Versión REFORZADA 🏹🦾🛡️
import os, logging, asyncio, google.generativeai as genai
from agent.tools import buscar_precio

logger = logging.getLogger("agentkit")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

async def generar_respuesta(mensaje_usuario, historial):
    # 🏹 Mantenemos tus modelos que ya sabemos que funcionan
    model_names = ["gemini-flash-latest", "gemini-pro-latest"]
    
    contexto = ""
    try:
        if len(mensaje_usuario) > 3:
            contexto = buscar_precio(mensaje_usuario)
    except: pass

    # Reforzamos los horarios al mango
    system_prompt = f"""
SABER IMPORTANTE:
- HORARIOS: Lunes a Viernes de 8:00 a 18:00 (largo), Sábados de 9:00 a 14:00, Domingos y Feriados de 9:00 a 13:00.
- LUGAR: Ferretería El Indio.
- PERSONALIDAD: Amable, servicial, "paisano" pero moderno.
- DATOS EXTRA: {contexto}
""".strip()

    for name in model_names:
        intentos = 0
        while intentos < 3: # 🔄 SISTEMA DE REINTENTOS (Terco)
            try:
                logger.info(f"Intentando {name} (Intento {intentos+1})")
                model = genai.GenerativeModel(name)
                response = model.generate_content(f"{system_prompt}\n\nCliente: {mensaje_usuario}")
                
                if response and hasattr(response, 'text') and response.text:
                    return response.text
                    
            except Exception as e:
                error_msg = str(e).lower()
                if "429" in error_msg or "quota" in error_msg:
                    logger.warning(f"⚠️ Google saturado, esperando 2 seg...")
                    await asyncio.sleep(2) # Espera un toque y reintenta
                    intentos += 1
                    continue
                
                logger.warning(f"❌ Error en {name}: {e}")
                break # Si es otro error, saltamos de modelo

    return "¡Hola amigo! Aguantame un milisegundo que estoy buscando el precio en el mostrador. ¿Qué me decías?"
