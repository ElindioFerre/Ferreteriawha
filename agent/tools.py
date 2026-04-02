# agent/tools.py — El Buscador Inteligente 🏹🔍✨
def buscar_precio(consulta: str) -> str:
    # ... (resto de la lógica) ...
    # 🏹 MEJORA: Normalizamos palabras (ej: 'moladora' -> 'amoladora')
    palabras_mejoradas = []
    for p in palabras:
        palabras_mejoradas.append(p)
        if p.startswith("molador"): palabras_mejoradas.append("a" + p) # moladora -> amoladora
        if p.endswith("s"): palabras_mejoradas.append(p[:-1]) # amoladoras -> amoladora
    # ...
