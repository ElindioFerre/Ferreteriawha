# agent/brain.py — Versión Blindada 🏹
import os, httpx, logging
from agent.tools import buscar_precio

logger = logging.getLogger("agentkit")

async def generar_respuesta(mensaje_usuario, historial):
    api_key = os.getenv("GOOGLE_API_KEY")
    
    # 🏹 USAMOS EL QUE YA FUNCIONÓ ANTES (Gemini 3 Flash Preview)
    model_name = "gemini-3-flash-preview" 
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    
    contexto_precios = ""
    try:
        contexto_precios = buscar_precio(mensaje_usuario)
    except: pass

    system_prompt = f"Eres el Indio de la Ferretería El Indio. Horarios: Lun-Vie 08-18 (corrido), Sab 09-14, Dom/Feriado 09-13. Info: {contexto_precios}"

    payload = {
        "contents": [{"parts": [{"text": f"{system_prompt}\n\nCliente: {mensaje_usuario}"}]}]
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)
            
            # ✅ SI FUNCIONA (Código 200)
            if response.status_code == 200:
                res_json = response.json()
                if 'candidates' in res_json and res_json['candidates']:
                    return res_json['candidates'][0]['content']['parts'][0]['text']
                return "Me quedé pensando... ¿me repetís?"
            
            # ⏳ SI HAY MUCHOS MENSAJES (Código 429)
            if response.status_code == 429:
                return "¡Aguantame un cachito paisano! Se me llenó el boliche y ya lo atiendo (Google hoy está pesado)."
            
            # ❌ SI GOOGLE SE PONE RARO (Otros errores como el 404 o 503)
            logger.error(f"Error Google {response.status_code}: {response.text}")
            return "Perdone paisano, se me cortó la señal del satélite un segundo. ¿Qué me decía?"

    except Exception as e:
        logger.error(f"Error crítico brain: {e}")
        return "Se me trabó la neurona, ¿podés repetir?"
