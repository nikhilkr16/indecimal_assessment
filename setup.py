#!/usr/bin/env python3
"""
Automated setup script for Construction Marketplace RAG Assistant.
Checks dependencies and guides through setup process.
"""
import os
import sys
import subprocess


def print_banner():
    """Print welcome banner."""
    print("""
╔═══════════════════════════════════════════════════════════╗
║   🏗️  Construction Marketplace RAG Assistant Setup       ║
╚═══════════════════════════════════════════════════════════╝
    """)


def check_python_version():
    """Check if Python version is compatible."""
    print("✓ Checking Python version...")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher required")
        print(f"   Current version: {sys.version}")
        return False
    
    print(f"  ✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    return True


def install_dependencies():
    """Install required Python packages."""
    print("\n✓ Installing dependencies...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("  ✅ Dependencies installed")
        return True
    except subprocess.CalledProcessError:
        print("  ❌ Failed to install dependencies")
        return False


def setup_env_file():
    """Create .env file if it doesn't exist."""
    print("\n✓ Setting up environment file...")
    
    if os.path.exists('.env'):
        print("  ⚠️  .env file already exists")
        response = input("  Overwrite? (y/N): ").strip().lower()
        if response != 'y':
            print("  ⏭️  Skipping .env setup")
            return True
    
    # Copy from example
    if os.path.exists('.env.example'):
        with open('.env.example', 'r') as src:
            content = src.read()
        
        print("\n  Please enter your OpenRouter API key")
        print("  (Get it from: https://openrouter.ai/)")
        api_key = input("  API Key: ").strip()
        
        if api_key:
            content = content.replace('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', api_key)
        
        with open('.env', 'w') as dst:
            dst.write(content)
        
        print("  ✅ .env file created")
        return True
    else:
        print("  ❌ .env.example not found")
        return False


def check_documents():
    """Check for documents in documents folder."""
    print("\n✓ Checking for documents...")
    
    if not os.path.exists('documents'):
        os.makedirs('documents')
        print("  📁 Created documents/ folder")
    
    doc_files = [f for f in os.listdir('documents') 
                 if f.endswith(('.pdf', '.txt'))]
    
    if not doc_files:
        print("  ⚠️  No documents found in documents/ folder")
        print("\n  Please add PDF or TXT documents:")
        print("  1. Download from provided Google Drive links")
        print("  2. Place in documents/ folder")
        print("  3. Or use the sample_faq.txt for testing")
        
        response = input("\n  Continue anyway? (y/N): ").strip().lower()
        return response == 'y'
    
    print(f"  ✅ Found {len(doc_files)} document(s)")
    for doc in doc_files:
        print(f"     - {doc}")
    return True


def build_index():
    """Build the FAISS vector index."""
    print("\n✓ Building vector index...")
    
    response = input("  Build index now? (Y/n): ").strip().lower()
    if response == 'n':
        print("  ⏭️  Skipping index build")
        print("     Run 'python rag_pipeline.py' manually later")
        return True
    
    try:
        print("\n  Processing documents...")
        import rag_pipeline
        
        rag = rag_pipeline.RAGPipeline()
        rag.process_documents()
        
        if len(rag.chunks) > 0:
            rag.save_index()
            print(f"  ✅ Index built with {len(rag.chunks)} chunks")
            return True
        else:
            print("  ⚠️  No chunks created - check your documents")
            return False
            
    except Exception as e:
        print(f"  ❌ Error building index: {e}")
        return False


def run_tests():
    """Run system tests."""
    print("\n✓ Running system tests...")
    
    response = input("  Run tests? (Y/n): ").strip().lower()
    if response == 'n':
        print("  ⏭️  Skipping tests")
        return True
    
    try:
        subprocess.check_call([sys.executable, "test_system.py"])
        return True
    except subprocess.CalledProcessError:
        print("  ⚠️  Some tests failed")
        return False


def print_next_steps():
    """Print next steps for the user."""
    print("""
╔═══════════════════════════════════════════════════════════╗
║                    ✅ Setup Complete!                     ║
╚═══════════════════════════════════════════════════════════╝

🚀 Next Steps:

1. Start the application:
   python app.py
   
   or use the convenience script:
   python run.py

2. Open your browser to:
   http://localhost:5000

3. Try example queries:
   - What factors affect construction project delays?
   - What are the safety requirements?

📚 Documentation:
   - README.md - Full documentation
   - QUICKSTART.md - Quick setup guide
   - DEPLOYMENT.md - Deployment instructions

🧪 Testing:
   - python test_system.py - System tests
   - python evaluate.py - Quality evaluation

💡 Tips:
   - Add more documents to documents/ folder
   - Rebuild index: python rag_pipeline.py
   - Customize UI in templates/index.html

Need help? Check README.md or PROJECT_SUMMARY.md
    """)


def main():
    """Main setup flow."""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    print("\nStep 1: Dependencies")
    response = input("Install required packages? (Y/n): ").strip().lower()
    if response != 'n':
        if not install_dependencies():
            print("\n❌ Setup failed at dependency installation")
            sys.exit(1)
    
    # Setup .env file
    print("\nStep 2: Configuration")
    if not setup_env_file():
        print("\n⚠️  Warning: .env file not configured properly")
    
    # Check documents
    print("\nStep 3: Documents")
    if not check_documents():
        print("\n⚠️  No documents to process")
        print("   Add documents and run 'python rag_pipeline.py' later")
    else:
        # Build index
        print("\nStep 4: Vector Index")
        build_index()
    
    # Run tests
    print("\nStep 5: Testing")
    run_tests()
    
    # Print next steps
    print_next_steps()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)
