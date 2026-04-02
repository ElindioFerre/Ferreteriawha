# agent/brain.py — Versión con Cupo Ilimitado (1.5 Flash) 🏹🚀
import os, httpx, logging, asyncio
from agent.tools import buscar_precio

logger = logging.getLogger("agentkit")

async def generar_respuesta(mensaje_usuario, historial):
    api_key = os.getenv("GOOGLE_API_KEY")
    
    # 🏹 MODELO CON 1500 MENSAJES POR DÍA (Gratis)
    # Este nombre es el correcto para tu clave según los logs.
    model_name = "gemini-flash-latest" 
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    
    contexto_precios = ""
    try:
        contexto_precios = buscar_precio(mensaje_usuario)
    except: pass

    system_prompt = f"""
Eres el asistente de la Ferretería El Indio. 
Personalidad: Amable y servicial. Usa "Hola" o "Amigo".
HORARIOS: Lun-Vie 8-18 (corrido), Sab 9-14, Dom/Feriado 9-13.
DATOS: {contexto_precios}
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
            
            # Si se satura Google, avisamos
            if response.status_code in [429, 503]:
                return "¡Hola amigo! Aguantame un toque que se me llenó el mostrador. En un ratito te respondo."

            logger.error(f"Error {response.status_code}: {response.text}")

    except Exception as e:
        logger.error(f"Error crítico: {e}")

    return "¡Hola! Se me cortó la conexión un segundo. ¿Me podés repetir la pregunta?"
