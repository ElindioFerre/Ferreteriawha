# tests/test_local.py — Simulador de chat en terminal (sin necesitar WhatsApp)
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()
from agent.brain import generar_respuesta
from agent.memory import inicializar_db, guardar_mensaje, obtener_historial, limpiar_historial

TELEFONO_TEST = "test-local-001"

async def main():
    await inicializar_db()
    print()
    print("=" * 55)
    print("  Ferreteria El Indio Agent — Test Local")
    print("=" * 55)
    print("  Escribi como si fueras un cliente.")
    print("  'limpiar' = borrar historial | 'salir' = terminar")
    print("-" * 55)
    print()
    while True:
        try:
            mensaje = input("Cliente: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSaliendo...")
            break
        if not mensaje:
            continue
        if mensaje.lower() == "salir":
            break
        if mensaje.lower() == "limpiar":
            await limpiar_historial(TELEFONO_TEST)
            print("[Historial borrado]\n")
            continue
        historial = await obtener_historial(TELEFONO_TEST)
        print("\nAgente: ", end="", flush=True)
        respuesta = await generar_respuesta(mensaje, historial)
        print(respuesta)
        print()
        await guardar_mensaje(TELEFONO_TEST, "user", mensaje)
        await guardar_mensaje(TELEFONO_TEST, "assistant", respuesta)

if __name__ == "__main__":
    asyncio.run(main())
