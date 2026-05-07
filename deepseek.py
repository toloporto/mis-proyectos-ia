import requests

# Reemplazar con clave API Key  de Open Router
API_KEY = 'your_openrouter_api_key'
API_URL = 'https://openrouter.ai/api/v1/chat/completions'


# Definir los encabezados para la solicitud de API
headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}

# Definir la carga util de la solicitud (datos)
data = {
    "model": "deepseek/deepseek-chat:free",
    "messages": [{"role": "user", "content": "What is the meaning of life?"}]
}

# Envía la solicitud POST a la API de DeepSeek
response = requests.post(API_URL, json=data, headers=headers)

# Comprobar si la solicitud fue exitosa
if response.status_code == 200:
    print("API Response:", response.json())
else:
    print("Failed to fetch data from API. Status Code:", response.status_code)

