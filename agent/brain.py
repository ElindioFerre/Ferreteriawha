import os
import httpx
from agent.tools import buscar_precio

async def generar_respuesta(mensaje_usuario, historial):
    api_key = os.getenv("GOOGLE_API_KEY")
    # MODELO ILIMITADO SEGÚN TU CONSOLA
    model_name = "gemini-3.0-flash-live-preview" 
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    
    # 🔍 Búsqueda de precios antes de hablar
    palabras_precio = ['cuanto', 'precio', 'vale', 'tenes', 'costo', 'presupuesto', 'hay']
    contexto_precios = ""
    if any(p in mensaje_usuario.lower() for p in palabras_precio) or len(mensaje_usuario.split()) < 4:
        contexto_precios = buscar_precio(mensaje_usuario)

    # 🏹 El Espíritu del Indio
    sistema = f"""
Eres 'Indio', el asistente rústico de 'Ferretería El Indio'.
IMPORTANTE:
- Si el catálogo tiene el precio, dáselo al cliente.
- Si no está, pídele medidas o marca para buscar mejor.
- Sé servicial pero directo, como un ferretero de confianza.

DATOS DEL CATÁLOGO ACTUAL:
{contexto_precios}
""".strip()
    
    datos = {
        "contents": [{
            "parts": [{"text": f"SISTEMA:\n{sistema}\n\nUSUARIO: {mensaje_usuario}"}]
        }]
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=datos, timeout=30.0)
            
            # Si el modelo "live" no responde por REST, el bot nos avisará
            if response.status_code == 200:
                return response.json()['candidates'][0]['content']['parts'][0]['text']
            
            # Si tira 404 (modelo no encontrado), avisame y probamos con 'gemini-3-flash-preview'
            return f"Che, el modelo {model_name} tiró error {response.status_code}. ¿Lo cambiamos?"
            
    except Exception as e:
        return f"Se me cortó el cable: {str(e)[:50]}"
