# agent/brain.py — El Indio EDUCADO y PRUDENTE 🏹🎩🦾⚡
import os, logging, asyncio, datetime, google.generativeai as genai
from agent.tools import buscar_precio

logger = logging.getLogger("agentkit")

raw_keys = os.getenv("GOOGLE_API_KEYS") or os.getenv("GOOGLE_API_KEY") or ""
LISTA_LLAVES = [k.strip() for k in raw_keys.split(",") if k.strip()]

async def generar_respuesta(mensaje_usuario, historial):
    model_names = ["gemini-flash-latest", "gemini-1.5-flash", "gemini-pro"]
    
    # 🏹 Detectamos si el cliente está pidiendo un PRECIO específicamente
    pide_precio = any(w in mensaje_usuario.lower() for w in ["cuanto", "precio", "sale", "costo", "valor", "vale", "cotiz"])

    contexto = ""
    try:
        ignorar = ["hola", "buenas", "buen dia", "hola!", "como va"]
        if len(mensaje_usuario) > 4 and mensaje_usuario.lower().strip() not in ignorar:
            contexto = buscar_precio(mensaje_usuario)
    except: pass

    # 🏹 REGLAS DE ETIQUETA Y PRUDENCIA
    now = datetime.datetime.now()
    saludo = "buenos días" if now.hour < 13 else "buenas tardes" if now.hour < 20 else "buenas noches"

    system_prompt = f"""
Sos el asesor experto de 'Ferretería El Indio'. Tu tono es profesional, amable y humano.
Momento actual: {saludo}.

REGLAS DE ORO:
1. SALUDO: Usá saludos naturales como "Hola", "{saludo}", "¿Cómo estás?". NUNCA digas "Fiera", "Campeón" ni frases de ese estilo.
2. PRECIOS: SOLO mencioná el precio si el cliente lo pidió explícitamente (ej: "¿Cuánto sale?", "¿Qué precio tiene?"). Si solo pregunta por el producto, asesoralo técnicamente sin dar el precio.
3. CÓDIGOS: NUNCA, bajo ninguna circunstancia, des los códigos de producto (ej: 'AL105'). Usá solo el nombre del producto.
4. NUNCA digas "catálogo" o "base de datos".
5. DATOS (Usalos solo según las reglas anteriores): {contexto if contexto else "No hay datos específicos, asesorá con tu conocimiento general de ferretería."}
""".strip()

    for api_key in LISTA_LLAVES:
        try:
            genai.configure(api_key=api_key)
            for name in model_names:
                try:
                    model = genai.GenerativeModel(name)
                    response = await model.generate_content_async(f"{system_prompt}\n\nCliente: {mensaje_usuario}")
                    if response and hasattr(response, 'text') and response.text:
                        return response.text
                except: continue
        except: continue

    return f"¡Hola, {saludo}! ¿Cómo te puedo ayudar hoy con tu proyecto?"
