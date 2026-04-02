import os
import google.generativeai as genai

async def generar_respuesta(mensaje_usuario, historial):
    api_key = os.getenv("GOOGLE_API_KEY")
    genai.configure(api_key=api_key)
    
    # Usamos el modelo 2.0 que tenés disponible
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    # Instrucciones súper claras para el Indio
    sistema = """
Eres el asistente virtual de 'Ferretería El Indio'. Tu nombre es 'Indio'. 
Atiendes por WhatsApp con un tono amable, profesional pero también cercano y algo rústico.
Tu objetivo es ayudar a los clientes con precios, stock y consultas técnicas simples.
Si no sabes algo, diles que pueden pasar por el local.
    """.strip()
    
    try:
        # Iniciamos el chat con el sistema de instrucciones
        chat = model.start_chat()
        
        # Le mandamos el contexto y el mensaje del cliente
        prompt = f"INSTRUCCIONES DE IDENTIDAD:\n{sistema}\n\nMENSAJE DEL CLIENTE: {mensaje_usuario}"
        response = chat.send_message(prompt)
        
        return response.text
        
    except Exception as e:
        print(f"Error en IA: {e}")
        return "Lo siento, el Indio está buscando una llave inglesa y no te escuchó bien... ¿Podés repetirlo?"
