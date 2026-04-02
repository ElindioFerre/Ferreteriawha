# agent/brain.py - Gemini Agent
import os, yaml, logging
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("agentkit")
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
MODELO = "gemini-3-flash-preview"

def _cargar_yaml():
    try:
        with open("config/prompts.yaml", "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError: return {}

def cargar_system_prompt():
    cfg = _cargar_yaml()
    prompt = cfg.get("system_prompt", "Eres el asistente de Ferreteria El Indio.")
    extras = []
    if os.path.exists("knowledge"):
        for a in os.listdir("knowledge"):
            if a.endswith((".csv", ".md", ".txt")):
                with open(os.path.join("knowledge", a), "r", encoding="utf-8") as f:
                    extras.append(f"Archivo: {a}\n{f.read()}")
    if extras: prompt += "\n\nConocimiento:\n" + "\n".join(extras)
    return prompt

async def generar_respuesta(mensaje, historial):
    if not mensaje: return "No entendi."
    system_prompt = cargar_system_prompt()
    contenidos = []
    for m in historial:
        role = "model" if m["role"] == "assistant" else "user"
        contenidos.append(types.Content(role=role, parts=[types.Part(text=m["content"])]))
    contenidos.append(types.Content(role="user", parts=[types.Part(text=mensaje)]))
    try:
        res = client.models.generate_content(model=MODELO, contents=contenidos, config=types.GenerateContentConfig(system_instruction=system_prompt))
        return res.text
    except Exception as e:
        logger.error(f"Error: {e}")
        return "Tuve un error tecnico."
