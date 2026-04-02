# agent/brain.py — Versión Liviana y Estable 🏹🦾
import os, httpx, logging, asyncio
from agent.tools import buscar_precio

logger = logging.getLogger("agentkit")

async def generar_respuesta(mensaje_usuario, historial):
    api_key = os.getenv("GOOGLE_API_KEY")
    
    # 🏹 MODELO 8B (El más liviano y estable para evitar errores 429/503)
    model_name = "gemini-1.5-flash-8b" 
    url = f"https://generativelanguage.googleapis.com/v1/models/{model_name}:generateContent?key={api_key}"
    
    contexto_precios = ""
    try:
        contexto_precios = buscar_precio(mensaje_usuario)
    except: pass

    system_prompt = f"""
Eres el asistente de la Ferretería El Indio. 
Habla de forma amable y directa. Usa "Hola" o "Amigo".
Si no hay precio en los datos, invita al local amablemente.
HORARIOS: Lun-Vie 8-18 (corrido), Sab 9-14, Dom/Feriado 9-13.
DATOS: {contexto_precios}
""".strip()

    payload = {
        "contents": [{"parts": [{"text": f"{system_prompt}\n\nCliente: {mensaje_usuario}"}]}]
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Solo un intento limpio para no saturar
            response = await client.post(url, json=payload)
            
            if response.status_code == 200:
                res_json = response.json()
                if 'candidates' in res_json and res_json['candidates']:
                    return res_json['candidates'][0]['content']['parts'][0]['text']
            
            # Si es 429 o 503, le avisamos al cliente con onda
            if response.status_code in [429, 503]:
                logger.warning(f"Google saturado: {response.status_code}")
                return "¡Hola amigo! Dame un minutito que se me llenó el mostrador. En un ratito te respondo bien."

            logger.error(f"Error Google {response.status_code}: {response.text}")

    except Exception as e:
        logger.error(f"Error crítico: {e}")

    return "¡Hola! Se me cortó la conexión un segundo. ¿Me podés repetir la pregunta así te ayudo?"
