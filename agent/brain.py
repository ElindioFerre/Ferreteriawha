import os
from google import genai
from google.genai import types

async def generar_respuesta(mensaje_usuario, historial):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return "Error: No encontré la GOOGLE_API_KEY en las variables de Railway."

    client = genai.Client(api_key=api_key)
    sistema = "Eres el asistente de Ferretería El Indio."
    
    contents = []
    for h in historial:
        role = "user" if h["role"] == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part.from_text(text=h["content"])]))
    contents.append(types.Content(role="user", parts=[types.Part.from_text(text=mensaje_usuario)]))

    try:
        # Probamos con el modelo más común
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            config=types.GenerateContentConfig(system_instruction=sistema),
            contents=contents
        )
        return response.text
    except Exception as e:
        # ¡ESTO ES LO IMPORTANTE! El Indio te va a decir el error real por WhatsApp
        return f"Error de Google: {str(e)}"

