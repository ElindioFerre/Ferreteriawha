# agent/brain.py — Versión Robusta y Estable 🏹
import os, httpx, logging
from agent.tools import buscar_precio

logger = logging.getLogger("agentkit")

async def generar_respuesta(mensaje_usuario, historial):
    api_key = os.getenv("GOOGLE_API_KEY")
    
    # 🏹 MODELO CON MÁS CUOTA (Gemini 1.5 Flash - 15 RPM)
    model_name = "gemini-1.5-flash" 
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    
    contexto_precios = ""
    try:
        contexto_precios = buscar_precio(mensaje_usuario)
    except: pass

    system_prompt = f"""
Eres el Indio de la Ferretería El Indio. 
Horarios: Lun-Vie 08-18 (corrido), Sab 09-14, Dom/Feriados 09-13.
Localidad: Estamos en la zona para servirle. Estilo rústico y amable.
Datos Catálogo: {contexto_precios}
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
                return "Me quedé pensando... ¿me repetís?"
            
            if response.status_code == 429:
                logger.warning("Cuota de Google agotada temporalmente.")
                return "¡Buenas paisano! Aguantame un segundito que se me llenó el boliche y ya lo atiendo (estamos un poco saturados de mensajes)."
            
            logger.error(f"Error Google {response.status_code}: {response.text}")
            return "Perdone paisano, se me cortó la señal del satélite. ¿Qué me decía?"

    except Exception as e:
        logger.error(f"Error crítico brain: {e}")
        return "Se me trabó la neurona, ¿podés repetir?"
