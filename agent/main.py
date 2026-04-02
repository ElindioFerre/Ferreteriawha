# agent/main.py — El Indio con Blindaje Pro 🏹🎩🛡️✨
import os, logging, threading
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import PlainTextResponse
from dotenv import load_dotenv
from agent.brain import generar_respuesta
from agent.memory import inicializar_db, guardar_mensaje, obtener_historial
from agent.providers import obtener_proveedor

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s agentkit: %(message)s")
logger = logging.getLogger("agentkit")
proveedor = obtener_proveedor()

async def procesar_mensaje_async(msg):
    try:
        historial = await obtener_historial(msg.telefono)
        respuesta = await generar_respuesta(msg.texto, historial)
        enviado = await proveedor.enviar_mensaje(msg.telefono, respuesta)
        if enviado:
            await guardar_mensaje(msg.telefono, "user", msg.texto)
            await guardar_mensaje(msg.telefono, "assistant", respuesta)
    except Exception as e:
        logger.error(f"❌ ERROR EN CICLO: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 🏹 ARRANCAMOS LO BÁSICO PRIMERO (Database de mensajes)
    try:
        await inicializar_db()
        logger.info("📡 BASE DE MENSAJES LISTA")
        
        # 🏹 EL SINCRONISMO PESADO LO HACEMOS DESPUÉS DE ARRANCAR
        def tarea_pesada():
            try:
                from agent.tools import sincronizar_catalogo
                sincronizar_catalogo()
                logger.info("✅ CATALOGO SINCRONIZADO EN SEGUNDO PLANO")
            except Exception as e:
                logger.error(f"⚠️ Error en carga pesada: {e}")

        threading.Thread(target=tarea_pesada, daemon=True).start()
        
    except Exception as e:
        logger.error(f"⚠️ Error en arranque: {e}")
        
    yield

#
