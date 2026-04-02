import os
from google import genai
from google.genai import types

async def generar_respuesta(mensaje_usuario, historial):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return "Error: No encontré la GOOGLE_API_KEY en Railway."

    client = genai.Client(api_key=api_key)
    sistema = "Eres el asistente de Ferretería El Indio. Amable y experto."
    
    contents = []
    for h in historial:
        role = "user" if h["role"] == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part.from_text(text=h["content"])]))
    contents.append(types.Content(role="user", parts=[types.Part.from_text(text=mensaje_usuario)]))

    # Lista de nombres posibles de la IA, prueba una tras otra
    modelos_a_probar = ["gemini-1.5-flash-latest", "gemini-1.5-flash-8b", "gemini-2.0-flash"]
    
    ultimo_error = ""
    for model_name in modelos_a_probar:
        try:
            response = client.models.generate_content(
                model=model_name,
                config=types.GenerateContentConfig(system_instruction=sistema),
                contents=contents
            )
            return response.text
        except Exception as e:
            ultimo_error = str(e)
            print(f"Fallo modelo {model_name}, probando siguiente...")
            continue
            
    return f"Todos los modelos fallaron. Último error: {ultimo_error}"

