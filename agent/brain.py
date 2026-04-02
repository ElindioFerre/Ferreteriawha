import os
import httpx
import logging
from agent.tools import buscar_precio

logger = logging.getLogger("agentkit")

async def generar_respuesta(mensaje_usuario, historial):
    api_key = os.getenv("GOOGLE_API_KEY")
    
    # Modelo Gemini 3 Flash
    model_name = "gemini-3-flash-preview" 
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    
    # 🔍 Buscamos precios
    contexto_precios = ""
    palabras_clave = ['cuanto', 'precio', 'vale', 'costo', 'tenes', 'hay', 'presupuesto', 'tenés']
    
    if any(p in mensaje_usuario.lower() for p in palabras_clave) or len(mensaje_usuario.split()) < 4:
        contexto_precios = buscar_precio(mensaje_usuario)
        logger.info(f"Busqueda de precios activa")

    # 🤖 El Indio
    system_prompt = f"""
Eres 'Indio', el encargado de 'Ferretería El Indio'.
Estilo: Amable, rústico, servicial.
Si el cliente pregunta precios, usa estos datos:
{contexto_precios}

REGLAS:
1. Si no encontrás el precio, decile que no lo tenés a mano y pedile detalles.
2. No inventes precios. 
3. Respondé cortito.
""".strip()

    payload = {
        "contents": [
            {
                "parts": [{"text": f"SISTEMA:\n{system_prompt}\n\nMensaje: {mensaje_usuario}"}]
            }
        ]
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=30.0)
            if response.status_code == 200:
                res_json = response.json()
                return res_json['candidates'][0]['content']['parts'][0]['text']
            return f"Hubo un temita (Error {response.status_code})."
    except Exception as e:
        logger.error(f"Error: {e}")
        return "Se me trabó la neurona, ¿podés repetir?"
