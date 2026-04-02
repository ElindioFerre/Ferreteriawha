import os
import httpx

async def generar_respuesta(mensaje_usuario, historial):
    # La llave mágica que pusiste en Railway
    api_key = os.getenv("GOOGLE_API_KEY")
    # Modelo Lite: Es el más rápido y el que tiene cuota libre de tu lista
    model_name = "gemini-2.0-flash-lite-001" 
    
    # URL directa de Google (Súper rápida)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    
    # Instrucciones de la personalidad del Indio
    sistema = """
Eres el asistente virtual de 'Ferretería El Indio'. Tu nombre es 'Indio'. 
Atiendes por WhatsApp con un tono amable, profesional pero también cercano y algo rústico.
Tu objetivo es ayudar a los clientes con precios, stock y consultas técnicas simples.
Si no sabes algo, dile que pueden pasar por el local.
    """.strip()
    
    # Formateamos los datos para enviárselos a Google
    datos = {
        "contents": [{
            "parts": [{"text": f"INSTRUCCIONES DE IDENTIDAD:\n{sistema}\n\nMENSAJE DEL CLIENTE: {mensaje_usuario}"}]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 800,
        }
    }

    try:
        async with httpx.AsyncClient() as client:
            # Llamamos a la API de Google por cable directo (httpx)
            response = await client.post(url, json=datos, timeout=30.0)
            
            if response.status_code == 200:
                res_json = response.json()
                # Extraemos la respuesta inteligente de la IA
                texto = res_json['candidates'][0]['content']['parts'][0]['text']
                return texto
            elif response.status_code == 429:
                return "Che, estoy a mil ahora mismo... ¿Me aguantás un minutito y me preguntás de nuevo? ¡Gracias!"
            else:
                # Si hay otro error, te lo mostramos para saber qué pasa
                return f"ALERTA INDIO ({response.status_code}): {response.text[:100]}"
                
    except Exception as e:
        # Error de red o algo raro
        print(f"Error crítico: {e}")
        return "¡Uy! Se me cortó la señal en el depósito... ¿Probamos de nuevo?"
