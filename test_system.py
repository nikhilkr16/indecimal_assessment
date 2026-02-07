"""
Test script to verify RAG system is working correctly.
"""
from rag_pipeline import RAGPipeline
from llm_generator import LLMGenerator


def test_rag_pipeline():
    """Test the RAG pipeline components."""
    print("Testing RAG System Components")
    print("=" * 60)
    
    # Test 1: Check if embedding model loads
    print("\n1. Testing Embedding Model...")
    try:
        rag = RAGPipeline()
        print(f"   [OK] Model loaded")
        print(f"   [OK] Embedding dimension: {rag.embedding_dim}")
    except Exception as e:
        print(f"   [ERROR] {e}")
        return False
    
    # Test 2: Check if index exists
    print("\n2. Testing Vector Index...")
    try:
        if rag.load_index():
            print(f"   [OK] Index loaded: {rag.index.ntotal} vectors")
            print(f"   [OK] Total chunks: {len(rag.chunks)}")
        else:
            print("   [WARN] No index found. Run 'python rag_pipeline.py' first")
            return False
    except Exception as e:
        print(f"   [ERROR] {e}")
        return False
    
    # Test 3: Test retrieval
    print("\n3. Testing Document Retrieval...")
    try:
        test_query = "construction project"
        results = rag.retrieve(test_query, top_k=2)
        
        if results:
            print(f"   [OK] Retrieved {len(results)} chunks")
            print(f"   [OK] Top result score: {results[0]['score']:.4f}")
        else:
            print("   [ERROR] No results retrieved")
            return False
    except Exception as e:
        print(f"   [ERROR] {e}")
        return False
    
    # Test 4: Test LLM generator
    print("\n4. Testing LLM Generator...")
    try:
        llm = LLMGenerator()
        
        # Check API key
        if not llm.api_key or llm.api_key == "your_api_key_here":
            print("   [WARN] OpenRouter API key not configured")
            print("   Please set OPENROUTER_API_KEY in .env file")
            return False
        
        print("   [OK] LLM generator initialized")
        print("   [OK] API key configured")
        
    except Exception as e:
        print(f"   [ERROR] {e}")
        return False
    
    # Test 5: End-to-end test
    print("\n5. Testing End-to-End Query...")
    try:
        test_query = "What is construction?"
        
        # Retrieve
        chunks = rag.retrieve(test_query, top_k=2)
        
        # Generate answer
        result = llm.generate_answer(test_query, chunks)
        
        print(f"   [OK] Query: {test_query}")
        print(f"   [OK] Retrieved {len(chunks)} chunks")
        print(f"   [OK] Answer generated: {result['answer'][:100]}...")
        print(f"   [OK] Grounded: {result['grounded']}")
        
    except Exception as e:
        print(f"   [ERROR] {e}")
        return False
    
    print("\n" + "=" * 60)
    print("[SUCCESS] All tests passed!")
    print("=" * 60)
    print("\nYou can now run: python app.py")
    
    return True


if __name__ == "__main__":
    success = test_rag_pipeline()
    if not success:
        print("\n[WARN] Some tests failed. Please check the errors above.")
        exit(1)
