import requests
import json

print("Testing Ollama...")

# Simple test
url = "http://localhost:11434/api/generate"
payload = {
    "model": "llama3.1",
    "prompt": "Say hello",
    "stream": False
}

try:
    print("Sending request...")
    response = requests.post(url, json=payload, timeout=120)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Success!")
        print(f"Response: {data.get('response', 'No response')}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Exception: {e}")
