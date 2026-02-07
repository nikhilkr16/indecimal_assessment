"""
Script to pull Ollama model using the API
"""
import requests
import json
import time

def pull_model(model_name="llama3.1"):
    """Pull a model using Ollama API"""
    url = "http://localhost:11434/api/pull"
    
    payload = {
        "name": model_name
    }
    
    print(f"Pulling model: {model_name}")
    print("This may take a few minutes depending on your internet speed...\n")
    
    try:
        response = requests.post(url, json=payload, stream=True, timeout=600)
        
        if response.status_code == 200:
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        status = data.get('status', '')
                        
                        if 'total' in data and 'completed' in data:
                            total = data['total']
                            completed = data['completed']
                            percent = (completed / total * 100) if total > 0 else 0
                            print(f"\r{status}: {percent:.1f}%", end='', flush=True)
                        else:
                            print(f"\r{status}", end='', flush=True)
                            
                    except json.JSONDecodeError:
                        pass
            
            print("\n\n✅ Model pulled successfully!")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Error pulling model: {e}")
        return False

def list_models():
    """List available models"""
    url = "http://localhost:11434/api/tags"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            
            if models:
                print("\n📦 Available models:")
                for model in models:
                    print(f"  - {model['name']}")
            else:
                print("\n📦 No models installed yet")
            return models
        else:
            print(f"❌ Error: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error listing models: {e}")
        return []

if __name__ == "__main__":
    print("🦙 Ollama Model Setup")
    print("=" * 50)
    
    # Check if Ollama is running
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        print("✅ Ollama is running!\n")
    except:
        print("❌ Ollama is not running. Please start Ollama first.")
        exit(1)
    
    # List current models
    models = list_models()
    
    # Pull llama3.1 if not already available
    if not any('llama3.1' in model['name'] for model in models):
        print("\nPulling llama3.1 model...")
        if pull_model("llama3.1"):
            list_models()
    else:
        print("\n✅ llama3.1 is already installed!")
