# agent/brain.py — Versión de Diagnóstico 🏹
import os, httpx, logging
from agent.tools import buscar_precio

logger = logging.getLogger("agentkit")

async def generar_respuesta(mensaje_usuario, historial):
    api_key = os.getenv("GOOGLE_API_KEY")
    
    # Probamos con el modelo más estándar de todos
    model_name = "gemini-1.5-flash" 
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    
    contexto_precios = ""
    try:
        contexto_precios = buscar_precio(mensaje_usuario)
    except: pass

    system_prompt = f"Eres el Indio de la Ferretería El Indio. Horarios: Lun-Vie 8-18, Sab 9-14, Dom 9-13. Datos: {contexto_precios}"

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
                return "Me quedé sin palabras, paisano."
            
            # 🚨 SI FALLA, TE VA A DECIR EL ERROR EN EL WHATSAPP:
            logger.error(f"Error Google: {response.text}")
            error_msg = response.json().get('error', {}).get('message', 'Error desconocido')
            return f"❌ Error de Google ({response.status_code}): {error_msg[:100]}"

    except Exception as e:
        logger.error(f"Error crítico brain: {e}")
        return f"❌ Error Técnico: {str(e)[:100]}"
