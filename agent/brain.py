# agent/brain.py — Cerebro con Horarios Reales 🏹
import os, httpx, logging
from agent.tools import buscar_precio

logger = logging.getLogger("agentkit")

async def generar_respuesta(mensaje_usuario, historial):
    api_key = os.getenv("GOOGLE_API_KEY")
    
    # 🏹 MODELO ESTABLE (Gemini 2.0 Flash)
    model_name = "gemini-2.0-flash" 
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    
    # 🔍 Buscamos precios
    contexto_precios = ""
    palabras_precio = ['cuanto', 'precio', 'vale', 'costo', 'tenes', 'hay', 'presupuesto', 'tenés']
    if any(p in mensaje_usuario.lower() for p in palabras_precio) or len(mensaje_usuario.split()) < 4:
        try:
            contexto_precios = buscar_precio(mensaje_usuario)
        except Exception as e:
            logger.error(f"Error precios: {e}")

    # 🤖 EL INDIO (Con horarios REALES)
    system_prompt = f"""
Eres 'Indio', el encargado de 'Ferretería El Indio'.
Estilo: Amable, rústico, servicial y directo. 'paisano', 'che', 'laburo'.

HORARIOS DE LA FERRETERÍA:
- Lunes a Viernes: 08:00 a 18:00 (de corrido).
- Sábados: 09:00 a 14:00.
- Domingos y Feriados: 09:00 a 13:00.

DATOS DE PRODUCTOS ENCONTRADOS:
{contexto_precios}

REGLAS:
1. Si pregunta precios y ves productos arriba, diles el nombre y el precio exacto.
2. Si NO hay productos arriba, pídele más detalles (medida, marca).
3. Respondé siempre cortito, máximo 3 líneas.
""".strip()

    payload = {
        "contents": [{"parts": [{"text": f"SISTEMA:\n{system_prompt}\n\nMensaje: {mensaje_usuario}"}]}]
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)
            if response.status_code == 200:
                res_json = response.json()
                if 'candidates' in res_json and res_json['candidates']:
                    return res_json['candidates'][0]['content']['parts'][0]['text']
            return "Perdone paisano, se me cortó la señal del satélite un segundo. ¿Qué me decía?"
    except Exception as e:
        return "Se me trabó la neurona, ¿podés repetir?"
