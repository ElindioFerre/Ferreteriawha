# agent/brain.py — Versión con SDK Oficial (La forma Pro) 🏹🛰️
import os, logging, asyncio
from google import genai
from agent.tools import buscar_precio

logger = logging.getLogger("agentkit")

# 🏹 Inicializamos el cliente de Google
# El SDK oficial maneja reintentos y sesiones de forma transparente
api_key = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=api_key)

async def generar_respuesta(mensaje_usuario, historial):
    try:
        # 1. Buscamos precios (RAG)
        contexto_precios = ""
        if len(mensaje_usuario) > 3:
            try:
                contexto_precios = buscar_precio(mensaje_usuario)
            except: 
                pass

        system_prompt = f"""
Eres el asistente de la Ferretería El Indio. 
Personalidad: Amable, servicial y directa. Usa "Hola" o "Amigo".
HORARIOS: Lun-Vie 8-18 (corrido), Sab 9-14, Dom/Feriado 9-13.
DATOS DE PRECIOS: {contexto_precios}
""".strip()

        # 🚀 Generar contenido de forma asíncrona (es bloqueante en este SDK v1 pero muy rápido)
        # Nota: Usamos loop.run_in_executor si queremos asíncrono real, pero por ahora directo va bien.
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=f"{system_prompt}\n\nCliente: {mensaje_usuario}"
        )
        
        if response and response.text:
            logger.info("🤖 IA respondió con éxito vía SDK")
            return response.text
            
        return "Dame un segundo que me quedé pensando..."

    except Exception as e:
        error_str = str(e).lower()
        if "429" in error_str or "quota" in error_str:
            logger.warning("⚠️ Límite de cuota Google alcanzado.")
            return "¡Hola amigo! Aguantame un toque que se me llenó el mostrador. En un ratito te respondo."
            
        logger.error(f"❌ Error IA: {e}", exc_info=True)
        return "¡Hola! Se me cortó la conexión un segundo. ¿Me podés repetir la pregunta?"
