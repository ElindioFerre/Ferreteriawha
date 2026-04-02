import requests, json
url = "https://ferreteriaelindio.netlify.app/data.json"
try:
    print(f"Descargando {url}...")
    # Descargamos solo un pedazo grande para parsear el inicio del JSON
    header = {'Range': 'bytes=0-10000'}
    r = requests.get(url, headers=header)
    content = r.content.decode('utf-8')
    # Tratamos de limpiar si no es un JSON perfecto por el corte
    if not content.endswith(']'):
        content = content[:content.rfind('}')+1] + "]"
    data = json.loads(content)
    print(json.dumps(data[:3], indent=2))
except Exception as e:
    print(f"Error: {e}")
