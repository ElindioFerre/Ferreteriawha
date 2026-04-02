# agent/brain.py — Versión TERCA (No se rinde) 🏹🦾🛡️⚡
import os, logging, asyncio, google.generativeai as genai
from agent.tools import buscar_precio

logger = logging.getLogger("agentkit")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

async def generar_respuesta(mensaje_usuario, historial):
    # 🏹 Solo los que sabemos que funcionan o pueden funcionar
    model_names = ["gemini-flash-latest", "gemini-1.5-flash", "gemini-2.0-flash", "gemini-pro"]
    
    contexto = ""
    try:
        if len(mensaje_usuario) > 3:
            contexto = buscar_precio(mensaje_usuario)
            if "no se encontró" in contexto.lower(): contexto = ""
    except: pass

    system_prompt = f"Sos el asistente de 'Ferretería El Indio'. Horarios: L-V 8-18, Sáb 9-14, Dom/Fer 9-13. Datos: {contexto}"

    for name in model_names:
        intentos = 0
        while intentos < 3: # 🏹 Tres intentos por modelo
            try:
                model = genai.GenerativeModel(name)
                response = await model.generate_content_async(f"{system_prompt}\n\nCliente: {mensaje_usuario}")
                if response and hasattr(response, 'text') and response.text:
                    return response.text
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg or "quota" in error_msg.lower():
                    # 🏹 SI GOOGLE NOS FRENA, ESPERAMOS DE VERDAD
                    espera = 10 if intentos == 0 else 20
                    logger.warning(f"⏳ PEAJE LLENO ({name}). Esperando {espera}s para reintentar...")
                    await asyncio.sleep(espera)
                    intentos += 1
                    continue
                
                # Si el modelo no existe (404), pasamos al siguiente modelo de una
                if "404" in error_msg:
                    break
                    
                logger.error(f"❌ Error inesperado en {name}: {e}")
                break

    return "¡Hola! Estoy con un poquito de demora pero ya te atiendo. ¿Qué me decías?"
