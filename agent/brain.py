# agent/brain.py — El Indio EXPERTO DEL MOSTRADOR 🏹🦾📚✨🦾
import os, logging, asyncio, datetime, google.generativeai as genai
from agent.catalogo import buscar_precio # 🏹 NUEVA CALLE

logger = logging.getLogger("agentkit")

raw_keys = os.getenv("GOOGLE_API_KEYS") or os.getenv("GOOGLE_API_KEY") or ""
LISTA_LLAVES = [k.strip() for k in raw_keys.split(",") if k.strip()]

async def generar_respuesta(mensaje_usuario, historial):
    model_names = ["gemini-flash-latest", "gemini-1.5-flash", "gemini-pro"]
    
    contexto = ""
    try:
        ignorar_saludos = ["hola", "buenas", "buen dia", "hola!", "holas", "buas", "buenas!", "que tal", "como va"]
        if len(mensaje_usuario) > 3 and mensaje_usuario.lower().strip() not in ignorar_saludos:
            contexto = buscar_precio(mensaje_usuario) # 🔍 BUSCA EN CATALGO.PY
    except: pass

    ahora_arg = datetime.datetime.utcnow() - datetime.timedelta(hours=3)
    saludo_sugerido = "buenos días" if ahora_arg.hour < 13 else "buenas tardes" if ahora_arg.hour < 20 else "buenas noches"

    system_prompt = f"""
Sos el experto de mostrador de 'Ferretería El Indio'. Sé directo y muy profesional.

REGLAS:
1. NO SALUDES si el cliente ya te habló. Sé directo.
2. PRIORIDAD AL CATÁLOGO: Si en los datos dice 'Amoladora TOTAL', decí 'Tengo la Amoladora TOTAL'. No inventes marcas famosas si no aparecen en los datos de abajo.
3. PRECIOS: Si el cliente pide precio, dáselo EXACTO según el catálogo. Si no lo ves, no lo inventes.
4. NOMBRES EXACTOS: Decí el nombre del producto tal cual aparece en los datos.
5. NUNCA menciones códigos ni proveedores.

DATOS DEL LOCAL (STOCK Y PRECIOS):
{contexto if contexto else "No hay coincidencias exactas. Asesorá técnicamente de forma experta hasta que el cliente diga un producto puntual."}
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

    return f"¡Hola! {saludo_sugerido}, ¿en qué puedo ayudarte con tu compra o proyecto de ferretería?"
