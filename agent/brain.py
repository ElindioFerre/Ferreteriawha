import os
import google.generativeai as genai

async def generar_respuesta(mensaje_usuario, historial):
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return "ERROR: No encontré la variable GOOGLE_API_KEY en Railway."
            
        # Configuramos la IA
        genai.configure(api_key=api_key)
        
        # Probamos con el modelo más liviano y seguro
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Ponemos las instrucciones
        instrucciones = "Eres el asistente de Ferretería El Indio."
        
        # Pedimos la respuesta a Google
        response = model.generate_content(f"{instrucciones}\n\nMensaje: {mensaje_usuario}")
        
        return response.text
        
    except Exception as e:
        # ¡ESTO NOS VA A DAR LA SOLUCIÓN! El bot te va a decir qué le dolió.
        return f"ALERTA GOOGLE: {str(e)}"
