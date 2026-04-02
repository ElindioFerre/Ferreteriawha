# agent/brain.py — Versión Ultra-Blindada y Resistente 🏹🛡️
import os, httpx, logging, asyncio
from agent.tools import buscar_precio

logger = logging.getLogger("agentkit")

async def generar_respuesta(mensaje_usuario, historial):
    api_key = os.getenv("GOOGLE_API_KEY")
    
    # 🏹 LISTA DE MODELOS (Si uno falla, probamos el otro)
    modelos_a_probar = ["gemini-1.5-flash-latest", "gemini-3-flash-preview"]
    
    contexto_precios = ""
    try:
        contexto_precios = buscar_precio(mensaje_usuario)
    except: pass

    system_prompt = f"""
Eres el "Indio", ferretero experto y amable. 
REGLAS: Sé servicial, rústico y breve. Si no hay stock o precio, invita al local.
HORARIOS: Lun-Vie 8-18, Sab 9-14, Dom/Feriado 9-13.
INFO PRECIOS: {contexto_precios}
""".strip()

    payload = {
        "contents": [{"parts": [{"text": f"{system_prompt}\n\nCliente: {mensaje_usuario}"}]}]
    }

    # 🏹 INTENTAMOS 3 VECES ANTES DE DARNOS POR VENCIDOS
    for intento in range(3):
        for model_name in modelos_a_probar:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(url, json=payload)
                    
                    if response.status_code == 200:
                        res_json = response.json()
                        return res_json['candidates'][0]['content']['parts'][0]['text']
                    
                    if response.status_code == 429:
                        logger.warning(f"Límite excedido en {model_name}, esperando...")
                        await asyncio.sleep(2) # Esperamos 2 segunditos
                        continue # Probamos el siguiente modelo o el siguiente intento
                    
                    logger.error(f"Falla {model_name}: {response.status_code}")

            except Exception as e:
                logger.error(f"Error en intento con {model_name}: {e}")
        
        # Si llegamos acá, esperamos un poco más para el próximo gran intento
        await asyncio.sleep(1)

    return "¡Perdone paisano! El satélite anda a los saltos. ¿Me repite lo último que se me entrecortó?"
