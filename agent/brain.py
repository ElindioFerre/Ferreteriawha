import os
import google.generativeai as genai

async def generar_respuesta(mensaje_usuario, historial):
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=api_key)
        
        # Le pedimos a Google la LISTA de modelos que podemos usar
        modelos = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                modelos.append(m.name.replace('models/', ''))
        
        # Te mandamos la lista por WhatsApp
        lista_modelos = "\n".join(modelos)
        return f"MENÚ DE MODELOS DISPONIBLES:\n{lista_modelos}"
        
    except Exception as e:
        return f"ERROR AL LISTAR: {str(e)}"
