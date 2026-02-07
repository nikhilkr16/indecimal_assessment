import os
import requests
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()


class LLMGenerator:
    def __init__(self, api_key: str = None):
        """
        Initialize LLM Generator with Ollama API.
        
        Args:
            api_key: Ollama API key
        """
        self.api_key = api_key or os.getenv("OLLAMA_API_KEY")
        # Use Ollama's generate endpoint which is more reliable
        self.base_url = "http://localhost:11434/api/generate"
        self.use_ollama_format = True
        self.site_url = "http://localhost:5000"
        self.app_name = "Construction RAG System"
        
    def generate_answer(self, query: str, retrieved_chunks: List[Dict]) -> Dict:
        """
        Generate answer using LLM based on retrieved chunks.
        
        Args:
            query: User query
            retrieved_chunks: List of retrieved document chunks
            
        Returns:
            Dictionary with answer and metadata
        """
        if not retrieved_chunks:
            return {
                'answer': "I couldn't find relevant information in the documents to answer your question.",
                'context_used': [],
                'grounded': False
            }
        
        # Build context from retrieved chunks
        context = "\n\n".join([
            f"[Source: {chunk['source']}]\n{chunk['text']}"
            for chunk in retrieved_chunks
        ])
        
        # Create prompt that enforces grounding
        prompt = self._create_grounded_prompt(query, context)
        
        # Generate answer
        answer = self._call_llm(prompt)
        
        return {
            'answer': answer,
            'context_used': retrieved_chunks,
            'grounded': True
        }
    
    def _create_grounded_prompt(self, query: str, context: str) -> str:
        """
        Create a prompt that enforces grounding to retrieved context.
        
        Args:
            query: User query
            context: Retrieved document context
            
        Returns:
            Formatted prompt
        """
        prompt = f"""You are a helpful assistant for a construction marketplace. Your job is to answer questions using ONLY the information provided in the context below.

IMPORTANT RULES:
1. Answer ONLY based on the provided context
2. If the context doesn't contain enough information, say "I don't have enough information in the documents to answer this question"
3. Do NOT use your general knowledge
4. Quote or reference specific parts of the context when possible
5. Be concise and direct

CONTEXT:
{context}

QUESTION:
{query}

ANSWER:"""
        
        return prompt
    
    def _call_llm(self, prompt: str, model: str = "llama3.1") -> str:
        """
        Call Ollama API to generate response.
        
        Args:
            prompt: Full prompt with context and query
            model: Model to use (default: llama3.1)
            
        Returns:
            Generated answer text
        """
        if not self.api_key:
            return "Error: Ollama API key not configured. Please set OLLAMA_API_KEY in .env file"
        
        # Ollama generate format (simpler and more reliable)
        headers = {
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=120  # Increased timeout for first model load
            )
            
            response.raise_for_status()
            
            # Check if response has content
            if not response.text:
                return "Error: Empty response from API"
            
            result = response.json()
            
            # Ollama generate endpoint returns 'response' field
            if 'response' in result:
                return result['response'].strip()
            
            # Check for error
            if 'error' in result:
                error_msg = result.get('error', 'Unknown error')
                return f"API Error: {error_msg}"
            
            return f"Error: Unexpected API response format: {result}"
            
        except requests.exceptions.HTTPError as e:
            return f"HTTP Error {response.status_code}: {response.text[:200]}"
        except requests.exceptions.RequestException as e:
            # If local Ollama fails, return helpful message
            return f"⚠️ Cannot connect to Ollama. Make sure Ollama is running locally on http://localhost:11434 or check your API key."
        except ValueError as e:
            return f"Error parsing JSON response: {str(e)}"
        except (KeyError, IndexError) as e:
            return f"Error parsing LLM response structure: {str(e)}"


if __name__ == "__main__":
    # Test the generator
    generator = LLMGenerator()
    
    # Sample retrieved chunks
    test_chunks = [
        {
            'text': 'Construction project delays can be caused by several factors including weather conditions, material shortages, and labor issues.',
            'source': 'construction_faq.pdf',
            'score': 0.85
        }
    ]
    
    result = generator.generate_answer(
        "What causes construction delays?",
        test_chunks
    )
    
    print("Answer:", result['answer'])
    print("\nGrounded:", result['grounded'])
