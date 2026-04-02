import os
from google import genai
from google.genai import types

async def generar_respuesta(mensaje_usuario, historial):
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    
    # Personalidad del Indio (Directo en el código para que no falle)
    sistema = """
Eres el asistente virtual de 'Ferretería El Indio'. Tu nombre es 'Indio'. 
Atiendes por WhatsApp con un tono amable, profesional pero también cercano y algo rústico.
Tu objetivo es ayudar a los clientes con precios, stock y consultas técnicas simples.
Si no sabes algo, dile que pueden pasar por el local o llamar al dueño.
"""
    
    # Filtramos el historial para que la IA entienda
    contents = []
    for h in historial:
        role = "user" if h["role"] == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part.from_text(text=h["content"])]))
    
    # Agregamos el mensaje actual
    contents.append(types.Content(role="user", parts=[types.Part.from_text(text=mensaje_usuario)]))

    try:
        # Intentamos con el modelo más nuevo
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
                system_instruction=sistema,
                temperature=0.7,
            ),
            contents=contents
        )
        return response.text
    except Exception as e:
        print(f"Error con gemini: {e}")
        # SI FALLA por cuota o cualquier cosa, respondemos algo digno
        return "Lo siento, el Indio está atendiendo a mucha gente ahora mismo... ¿Podés repetirme tu consulta en un minuto?"

