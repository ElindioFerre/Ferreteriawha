# agent/tools.py — Herramientas de la Ferreteria El Indio
# buscar_precio() esta lista para conectar al Gestor de precios de la app
import os, csv, logging
logger = logging.getLogger("agentkit")

def buscar_precio(consulta: str) -> str:
    """
    Busca precios en knowledge/catalogo_productos.csv
    TODO: Reemplazar con llamada HTTP al Gestor de precios de ferreteriaelindio
    Ejemplo futuro:
        import httpx
        r = httpx.get(f"https://tu-api.ferreteriaelindio.com/precios?q={consulta}")
        return r.json()
    """
    ruta = os.path.join("knowledge", "catalogo_productos.csv")
    if not os.path.exists(ruta):
        return "Catalogo no disponible en este momento."
    palabras = consulta.lower().split()
    resultados = []
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                linea = " ".join(row.values()).lower()
                if all(p in linea for p in palabras):
                    nombre = row.get("producto", "")
                    precio = row.get("precio", "")
                    unidad = row.get("unidad", "")
                    resultados.append(f"- {nombre}: ${precio} / {unidad}")
        if resultados:
            return "\n".join(resultados[:5])
        return f"No encontre '{consulta}' en el catalogo. Consultar directamente en el local."
    except Exception as e:
        logger.error(f"Error buscando precio: {e}")
        return "Error al buscar en el catalogo."
