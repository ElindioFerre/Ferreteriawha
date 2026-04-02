# agent/brain.py — El Cerebro Robusto 🏹🧠
import os, logging, google.generativeai as genai
from agent.tools import buscar_precio

logger = logging.getLogger("agentkit")

# Configuramos la IA
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

async def generar_respuesta(mensaje_usuario, historial):
    try:
        # Buscamos precios
        contexto = ""
        if len(mensaje_usuario) > 3:
            try: 
                contexto = buscar_precio(mensaje_usuario)
            except: 
                pass

        # Usamos el modelo 1.5-flash que es el más estable y gratis
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        system_prompt = f"""
Eres el asistente de la Ferretería El Indio. 
Personalidad: Amable, servicial y directa. Usa "Hola" o "Amigo".
HORARIOS: Lun-Vie 8-18 (corrido), Sab 9-14, Dom/Feriado 9-13.
DATOS DE PRECIOS: {contexto}
""".strip()
        
        # Generar respuesta (en esta librería es síncrono pero rápido)
        response = model.generate_content(f"{system_prompt}\n\nCliente: {mensaje_usuario}")
        
        if response and response.text:
            logger.info("✅ IA respondió con éxito (GenerativeAI)")
            return response.text
            
        return "Dame un segundo que me quedé pensando..."

    except Exception as e:
        error_msg = str(e).lower()
        if "429" in error_msg or "quota" in error_msg:
            logger.warning("⚠️ Límite de cuota alcanzado.")
            return "¡Hola amigo! Aguantame un toque que se me llenó el mostrador. En un ratito te respondo."
            
        logger.error(f"❌ Error IA: {e}")
        return "¡Hola! Se me cortó la conexión un segundo. ¿Me podés repetir la pregunta?"
