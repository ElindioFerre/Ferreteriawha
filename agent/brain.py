# agent/brain.py — Versión con nombre de captura 🏹📸
import os, httpx, logging, asyncio
from agent.tools import buscar_precio

logger = logging.getLogger("agentkit")

async def generar_respuesta(mensaje_usuario, historial):
    api_key = os.getenv("GOOGLE_API_KEY")
    
    # 🏹 MODELO EXACTO DE TU CAPTURA
    model_name = "gemini-1.5-flash" 
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    
    # ... resto del código ...
