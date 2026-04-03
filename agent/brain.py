# agent/brain.py — El Indio EXPERTO 5.4 🏹🛡️🦾💎✨🦾
import os, logging, asyncio, datetime, sqlite3, google.generativeai as genai

logger = logging.getLogger("agentkit")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "knowledge", "catalogo.db")

# 🏹 MOTOR DE BÚSQUEDA "LASER" (Antivirus de Repuestos de Auto)
def buscar_en_el_catalogo(consulta: str) -> str:
    """Buscador que ignora el ruido y se centra en el producto real"""
    if not os.path.exists(DB_PATH): return ""
    
    # 1. Limpieza extrema del ruido
    limpia = consulta.lower()
    for char in "?!,.:;()": limpia = limpia.replace(char, "")
    
    # Palabras que NO debemos buscar nunca en la DB
    ruido = {
        "precio", "cuanto", "sale", "tenes", "alguna", "quiero", "usar", "cortar", "unos", 
        "fierros", "para", "recomendame", "decime", "esto", "esta", "estos", "estas",
        "horario", "donde", "estan", "venden", "tenen", "tienen", "tenas", "podes", "pasas"
    }
    
    # 2. Diccionario de corrección
    vocabulario = {
        "moladora": "amoladora", "moladoras": "amoladora", 
        "fresa": "fresadora", "agujereadora": "taladro"
    }

    palabras_raw = limpia.split()
    palabras_clave = []
    
    for p in palabras_raw:
        if p in ruido or len(p) < 3: continue
        # Corregimos si es necesario
        p_final = vocabulario.get(p, p)
        palabras_clave.append(p_final)

    if not palabras_clave: return ""

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # 🏹 ESTRATEGIA LASER: 
        # Buscamos que el nombre tenga AL MENOS la palabra más importante (la primera)
        principal = palabras_clave[0]
        
        # Generamos el filtro: El producto DEBE contener la palabra principal
        # Y opcionalmente las otras
        sub_filtros = []
        params = [f"%{principal}%"]
        for p in palabras_clave[1:]:
            sub_filtros.append("nombre LIKE ?")
            params.append(f"%{p}%")
            
        sql = f"SELECT nombre, precio FROM productos WHERE nombre LIKE ?"
        if sub_filtros:
            # Si hay más palabras, tratamos de que coincidan todas (AND) para ser precisos
            sql += " AND " + " AND ".join(sub_filtros)
        
        sql += " LIMIT 10"
        
        c.execute(sql, params)
        res = c.fetchall()
        
        # Si no encontró con AND (demasiado estricto), probamos con OR pero solo para la principal
        if not res:
            sql = "SELECT nombre, precio FROM productos WHERE nombre LIKE ? LIMIT 8"
            c.execute(sql, [f"%{principal}%"])
            res = c.fetchall()
            
        conn.close()
        
        if res:
            return "\n".join([f"- {r[0]}: ${r[1]:,.0f}" for r in res])
        return ""
    except Exception as e:
        logger.error(f"Error buscador laser: {e}")
        return ""

raw_keys = os.getenv("GOOGLE_API_KEYS") or os.getenv("GOOGLE_API_KEY") or ""
LISTA_LLAVES = [k.strip() for k in raw_keys.split(",") if k.strip()]

async def generar_respuesta(mensaje_usuario, historial):
    model_names = ["gemini-flash-latest", "gemini-1.5-flash", "gemini-pro"]
    
    contexto = ""
    try:
        contexto = buscar_en_el_catalogo(mensaje_usuario)
    except: pass

    system_prompt = f"""
Sos el experto de mostrador de 'Ferretería El Indio'. Sé directo y muy profesional.

HORARIOS: Lun-Vie 8-18, Sáb 9-14, Dom/Fér 9-13.

REGLAS DE ORO:
1. NO SALUDES si el historial muestra que ya lo hiciste.
2. PRECIOS: Si el cliente pide precio, mirá los DATOS reales abajo. 
3. SI ves repuestos de autos (Renault, Fiat, Ford) y el cliente pidió una HERRAMIENTA ferretera (Amoladora, Taladro), IGNORA los autos. No ofrezcas patines de freno si te piden una amoladora.
4. Si los datos abajo coinciden con lo pedido, dale las opciones y el precio TAL CUAL aparece.
5. NO menciones códigos ni proveedores.

DATOS DEL CATÁLOGO REAL:
{contexto if contexto else "No se encontraron herramientas específicas en la lista rápida."}
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
    return "¡Hola! Bienvenido a 'El Indio'. ¿En qué fierros te puedo ayudar hoy?"
