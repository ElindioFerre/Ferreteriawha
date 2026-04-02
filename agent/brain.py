import os
import yaml
from google import genai
from google.genai import types

# Cargar configuraciones
def cargar_config():
    with open("config/prompts.yaml", "r", encoding="utf-8") as f:
        prompts = yaml.safe_load(f)
    return prompts

async def generar_respuesta(telefono, mensaje_usuario, historial):
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    prompts = cargar_config()
    
    # Armar el contexto
    sistema = prompts["agent_persona"]["system_prompt"]
    
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
        print(f"Error con gemini-2.0-flash: {e}")
        # SI FALLA, intentamos con el modelo estable
        try:
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                config=types.GenerateContentConfig(
                    system_instruction=sistema,
                ),
                contents=contents
            )
            return response.text
        except Exception as e2:
            print(f"Error crítico en IA: {e2}")
            return "Lo siento, el Indio está un poco distraído ahora mismo... ¿Podés repetirme tu consulta en un minuto?"

