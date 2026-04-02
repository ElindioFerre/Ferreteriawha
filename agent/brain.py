# agent/brain.py — Versión "Amigo Indio" 🏹🤝
import os, httpx, logging, asyncio
from agent.tools import buscar_precio

logger = logging.getLogger("agentkit")

async def generar_respuesta(mensaje_usuario, historial):
    api_key = os.getenv("GOOGLE_API_KEY")
    modelos_a_probar = ["gemini-1.5-flash-latest", "gemini-3-flash-preview"]
    
    contexto_precios = ""
    try:
        contexto_precios = buscar_precio(mensaje_usuario)
    except: pass

    # 🤝 PROMPT MÁS NORMAL Y AMIGABLE:
    system_prompt = f"""
Eres el asistente de la Ferretería El Indio. 
PERSONALIDAD: Habla de forma amable, servicial y normal. 
- Puedes usar "Hola" o "Amigo", pero evita ser demasiado rústico (ya no uses la palabra "paisano").
- Si no encuentras un precio en los datos, di amablemente: "No tengo el precio justo acá en sistema ahora, pero si te queda cerca el local podés pasarte y lo vemos en el mostrador".
- Responde de forma clara y sin dar vueltas.

HORARIOS DE ATENCIÓN:
- Lun-Vie: 08:00 a 18:00 (horario corrido).
- Sábados: 09:00 a 14:00.
- Domingos y Feriados de guardia: 09:00 a 13:00.

DATOS DE PRODUCTOS (Úsalos si el usuario pregunta precios): {contexto_precios}
""".strip()

    payload = {
        "contents": [{"parts": [{"text": f"{system_prompt}\n\nCliente dice: {mensaje_usuario}"}]}]
    }

    # 🏹 REINTENTOS PARA EVITAR TRABAS:
    for intento in range(2): 
        for model_name in modelos_a_probar:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(url, json=payload)
                    if response.status_code == 200:
                        res_json = response.json()
                        if 'candidates' in res_json and res_json['candidates']:
                            return res_json['candidates'][0]['content']['parts'][0]['text']
                    
                    if response.status_code == 429:
                        await asyncio.sleep(2) 
                        continue 
            except Exception as e:
                logger.error(f"Falla {model_name}: {e}")
        await asyncio.sleep(1)

    return "¡Hola amigo! Se me cortó la conexión un segundo. ¿Me podés repetir la pregunta así te ayudo mejor?"
