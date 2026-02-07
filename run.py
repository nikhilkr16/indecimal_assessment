"""
Quick start script to set up and run the RAG system.
"""
import os
import sys


def check_dependencies():
    """Check if required packages are installed."""
    try:
        import flask
        import sentence_transformers
        import faiss
        import PyPDF2
        print("✅ All dependencies installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("\nPlease run: pip install -r requirements.txt")
        return False


def check_env():
    """Check if environment variables are set."""
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("OLLAMA_API_KEY")
    if not api_key:
        print("⚠️  OLLAMA_API_KEY not set in .env file")
        print("\nPlease:")
        print("1. Add your Ollama API key to .env file")
        print("2. Format: OLLAMA_API_KEY=your_api_key_here")
        return False
    
    print("✅ Environment variables configured")
    return True


def check_documents():
    """Check if documents are available."""
    docs_dir = "documents"
    if not os.path.exists(docs_dir):
        os.makedirs(docs_dir)
        print(f"⚠️  Created {docs_dir}/ directory")
        print("\nPlease add PDF documents to the documents/ folder")
        return False
    
    pdf_files = [f for f in os.listdir(docs_dir) if f.endswith('.pdf')]
    if not pdf_files:
        print("⚠️  No PDF files found in documents/ directory")
        print("\nPlease add PDF documents to process")
        return False
    
    print(f"✅ Found {len(pdf_files)} PDF documents")
    return True


def build_index():
    """Build the FAISS index from documents."""
    print("\n📊 Building vector index...")
    from rag_pipeline import RAGPipeline
    
    rag = RAGPipeline()
    
    # Try to load existing index
    if rag.load_index():
        print("✅ Loaded existing index")
        return True
    
    # Build new index
    rag.process_documents()
    
    if len(rag.chunks) == 0:
        print("❌ No chunks created. Check your documents.")
        return False
    
    rag.save_index()
    print("✅ Index built and saved")
    return True


def main():
    """Main setup and run function."""
    print("🏗️  Construction Marketplace RAG Assistant")
    print("=" * 50)
    print("\n📋 Running setup checks...\n")
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Check environment
    if not check_env():
        return
    
    # Check documents
    if not check_documents():
        return
    
    # Build index
    if not build_index():
        return
    
    print("\n" + "=" * 50)
    print("✅ Setup complete!")
    print("=" * 50)
    print("\n🚀 Starting web application...")
    print("\nAccess the app at: http://localhost:5000")
    print("Press Ctrl+C to stop\n")
    
    # Import and run Flask app
    from app import app
    app.run(debug=True, host='0.0.0.0', port=5000)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
