# agent/brain.py — Versión con Cupo Ilimitado (1.5 Flash) 🏹🚀
import os, httpx, logging, asyncio
from agent.tools import buscar_precio

logger = logging.getLogger("agentkit")

async def generar_respuesta(mensaje_usuario, historial):
    api_key = os.getenv("GOOGLE_API_KEY")
    
    # 🏹 MODELO ESTABLE (1500 mensajes por día)
    model_name = "gemini-1.5-flash-002" 
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    
    contexto_precios = ""
    try:
        # Buscamos en el catálogo si el mensaje es representativo
        if len(mensaje_usuario) > 3:
            contexto_precios = buscar_precio(mensaje_usuario)
    except: pass

    system_prompt = f"""
Eres el asistente de la Ferretería El Indio. 
Personalidad: Amable, servicial y directa. Usa "Hola" o "Amigo".
HORARIOS: Lun-Vie 8-18 (corrido), Sab 9-14, Dom/Feriado 9-13.
DATOS DE PRECIOS: {contexto_precios}
""".strip()

    payload = {
        "contents": [{"parts": [{"text": f"{system_prompt}\n\nCliente: {mensaje_usuario}"}]}]
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)
            
            if response.status_code == 200:
                res_json = response.json()
                if 'candidates' in res_json and res_json['candidates']:
                    return res_json['candidates'][0]['content']['parts'][0]['text']
                return "Dame un segundo que me quedé pensando..."
            
            # Si llegas al límite RPM (15 por minuto), esperamos
            if response.status_code in [429, 503]:
                logger.warning(f"Saturación detectada: {response.status_code}")
                return "¡Hola amigo! Dame un minutito que se me llenó el boliche. En un ratito te respondo bien."

            logger.error(f"Error {response.status_code}: {response.text}")

    except Exception as e:
        logger.error(f"Error crítico brain: {e}")

    return "¡Hola! Se me cortó la conexión un segundo. ¿Me podés repetir la pregunta?"
