import os
import httpx

async def generar_respuesta(mensaje_usuario, historial):
    api_key = os.getenv("GOOGLE_API_KEY")
    # Usamos el modelo 2.0 que confirmamos que tenés en tu lista
    model_name = "gemini-2.0-flash" 
    
    # El "cable directo" a Google
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    
    # Instrucciones del Indio
    sistema = "Eres el asistente de Ferretería El Indio. Hablas con tono amable y experto."
    
    # Preparamos el paquete de datos
    datos = {
        "contents": [{
            "parts": [{"text": f"INSTRUCCIONES: {sistema}\n\nMENSAJE CLIENTE: {mensaje_usuario}"}]
        }]
    }

    try:
        async with httpx.AsyncClient() as client:
            # Mandamos el mensaje directo a los servidores de Google
            response = await client.post(url, json=datos, timeout=30.0)
            
            if response.status_code == 200:
                res_json = response.json()
                # Sacamos el texto de la respuesta
                texto = res_json['candidates'][0]['content']['parts'][0]['text']
                return texto
            else:
                # Si Google nos dice que no por algo, te lo avisamos por WhatsApp
                return f"ERROR GOOGLE DIRECTO ({response.status_code}): {response.text[:100]}"
                
    except Exception as e:
        return f"ERROR DE CONEXIÓN: {str(e)}"
