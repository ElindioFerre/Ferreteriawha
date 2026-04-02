# agent/brain.py — Depuración 🧠🔬
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)
            logger.info(f"🤖 GOOGLE STATUS: {response.status_code}") # <--- VER ESTO
            
            if response.status_code == 200:
                # ... resto del codigo ...
            else:
                logger.error(f"❌ Error Google {response.status_code}: {response.text}")
                return "Perdón amigo, el sistema está medio cansado. Probame en un ratito."
