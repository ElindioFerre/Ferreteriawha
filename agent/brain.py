# agent/brain.py — Versión Con Personalidad 🏹🦾
import os, httpx, logging
from agent.tools import buscar_precio

logger = logging.getLogger("agentkit")

async def generar_respuesta(mensaje_usuario, historial):
    api_key = os.getenv("GOOGLE_API_KEY")
    model_name = "gemini-3-flash-preview" 
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    
    contexto_precios = ""
    try:
        # Solo buscamos si el usuario parece estar preguntando un precio o producto
        contexto_precios = buscar_precio(mensaje_usuario)
    except: pass

    # 🏹 UN SYSTEM PROMPT MUCHO MÁS DETALLADO:
    system_prompt = f"""
Eres "El Indio", el alma de la Ferretería El Indio. 
Tu misión es atender a los clientes con amabilidad, rapidez y ese toque rústico del oficio.

REGLAS DE ORO:
1. SALUDO: Sé amable y usa términos como "paisano", "don", "doña".
2. PRECIOS: Si encuentras precios en los datos de abajo, dáselos con seguridad. 
3. SI NO HAY PRECIOS: No digas "no encontré en el catálogo". Di algo como: "No tengo el precio justo acá a mano, pero si te pasás lo buscamos en el mostrador". 
4. BREVEDAD: Responde corto y al punto, no escribas testamentos.
5. HORARIOS Y UBICACIÓN: Si te preguntan, dales los datos: 
   - Lun-Vie: 08:00 a 18:00 (corrido).
   - Sab: 09:00 a 14:00.
   - Dom/Feriados: 09:00 a 13:00.

DATOS EXTRAÍDOS (Úsalos solo si sirven): {contexto_precios}
""".strip()

    payload = {
        "contents": [{"parts": [{"text": f"{system_prompt}\n\nCliente dice: {mensaje_usuario}"}]}]
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)
            if response.status_code == 200:
                res_json = response.json()
                if 'candidates' in res_json and res_json['candidates']:
                    return res_json['candidates'][0]['content']['parts'][0]['text']
            
            if response.status_code == 429:
                return "¡Buenas paisano! Aguantame un cachito que se me llenó el mostrador y ya lo atiendo."
            
            logger.error(f"Error {response.status_code}: {response.text}")
            return "Perdone paisano, se me cortó la señal del satélite. ¿Qué me decía?"

    except Exception as e:
        logger.error(f"Error: {e}")
        return "Se me trabó la neurona, ¿podés repetir?"
