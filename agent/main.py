# agent/main.py — Súper Logging 🏹🛰️
@app.post("/webhook")
async def webhook_post(request: Request, background_tasks: BackgroundTasks):
    try:
        data = await request.json()
        logger.info(f"📥 WEBHOOK RECIBIDO: {data.keys()}") # <--- LOG CLAVE
        
        mensajes = await proveedor.parsear_webhook(request)
        if not mensajes:
            logger.info("ℹ️ Webhook sin mensajes (posible status o confirmación).")
            return {"status": "ok"}

        for msg in mensajes:
            logger.info(f"💬 Mensaje detectado de {msg.telefono}. Propio? {msg.es_propio}")
            if msg.es_propio or not msg.texto:
                continue
            
            logger.info(f"🚀 Disparando procesamiento para: {msg.texto[:20]}...")
            background_tasks.add_task(procesar_mensaje_async, msg)
        
        return {"status": "accepted"}
    except Exception as e:
        logger.error(f"❌ ERROR WEBHOOK: {e}", exc_info=True)
        return {"status": "error"}
