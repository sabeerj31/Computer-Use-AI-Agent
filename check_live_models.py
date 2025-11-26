import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GOOGLE_API_KEY')
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"

response = requests.get(url)
if response.status_code == 200:
    models = response.json().get('models', [])
    print("Available models:")
    for model in models:
        name = model['name']
        supported_methods = model.get('supportedGenerationMethods', [])
        supports_live = 'bidiGenerateContent' in supported_methods
        live_indicator = " [LIVE]" if supports_live else ""
        print(f"- {name}{live_indicator}")
        if supports_live:
            print(f"  Supported methods: {supported_methods}")
else:
    print(f"Error: {response.status_code} - {response.text}")