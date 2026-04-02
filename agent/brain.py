import os
import google.generativeai as genai

async def generar_respuesta(mensaje_usuario, historial):
    api_key = os.getenv("GOOGLE_API_KEY")
    genai.configure(api_key=api_key)
    
    # Configuramos el modelo
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Armamos la conversación
    chat = model.start_chat(history=[])
    
    # Ponemos las instrucciones del Indio como primer mensaje si el historial está vacío
    instrucciones = "Eres el asistente de Ferretería El Indio. Habla como un ferretero experto y amable."
    
    try:
        # La IA de Google procesa el mensaje
        response = chat.send_message(f"{instrucciones}\n\nMensaje del cliente: {mensaje_usuario}")
        return response.text
    except Exception as e:
        print(f"Error IA: {e}")
        return "Lo siento, el Indio está buscando un tornillo y no te escuchó bien... ¿Qué necesitabas?"
