# agent/main.py — Arreglo del Bucle Infinito 🔄🚫
import logging
from fastapi import FastAPI, Request, BackgroundTasks
from agent.brain import generar_respuesta
from agent.providers.whapi import ProveedorWhapi

app = FastAPI()
whapi = ProveedorWhapi()

async def procesar_mensaje_async(msg):
    # 🏹 REGLA DE ORO: Ignorar si el mensaje lo mandó el bot
    if msg.get('from_me') is True:
        return 

    chat_id = msg.get('chat_id')
    texto = msg.get('text', {}).get('body', '')
    
    if not chat_id or not texto:
        return

    # Generamos la IA
    respuesta = await generar_respuesta(texto, [])
    
    # Enviamos
    await whapi.enviar_mensaje(chat_id, respuesta)

@app.post("/webhook")
async def webhook_post(request: Request, background_tasks: BackgroundTasks):
    try:
        data = await request.json()
        mensajes = data.get('messages', [])
        
        for msg in mensajes:
            # 🏹 Filtro de seguridad también aquí
            if not msg.get('from_me'):
                background_tasks.add_task(procesar_mensaje_async, msg)
                
    except Exception as e:
        logging.error(f"Error webhook: {e}")
        
    return {"status": "accepted"}
