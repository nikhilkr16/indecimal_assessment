import requests
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('OLLAMA_API_KEY')
print(f'API Key (first 20 chars): {api_key[:20] if api_key else "NOT FOUND"}...')

url = 'http://localhost:11434/api/chat'

headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

payload = {
    'model': 'llama3.1',
    'messages': [
        {
            'role': 'user',
            'content': 'Say hello in one word'
        }
    ],
    'stream': False
}

print(f'\nMaking request to: {url}')
print(f'Model: {payload["model"]}')

try:
    response = requests.post(url, headers=headers, json=payload, timeout=120)
    print(f'\nStatus Code: {response.status_code}')
    print(f'Content-Type: {response.headers.get("Content-Type")}')
    print(f'\nResponse Text (first 500 chars):\n{response.text[:500]}')
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f'\nParsed JSON successfully!')
            print(f'Keys in response: {data.keys()}')
            if 'message' in data and 'content' in data['message']:
                print(f'\nAnswer: {data["message"]["content"]}')
            elif 'choices' in data:
                print(f'\nAnswer: {data["choices"][0]["message"]["content"]}')
        except Exception as e:
            print(f'\nError parsing JSON: {e}')
    else:
        print(f'\nHTTP Error: {response.status_code}')
        
except Exception as e:
    print(f'\nException: {e}')
    print('\n⚠️ Make sure Ollama is running locally. Install from: https://ollama.com/')
