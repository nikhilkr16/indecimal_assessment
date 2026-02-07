from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
from rag_pipeline import RAGPipeline
from llm_generator import LLMGenerator

app = Flask(__name__)
CORS(app)

# Initialize RAG pipeline and LLM generator
print("Initializing RAG system...")
rag = RAGPipeline()
llm = LLMGenerator()

# Load or build index
if not rag.load_index():
    print("Building new index from documents...")
    rag.process_documents()
    if len(rag.chunks) > 0:
        rag.save_index()
    else:
        print("Warning: No documents found to index")

print("RAG system ready!")


@app.route('/')
def home():
    """Render the main chat interface."""
    return render_template('index.html')


@app.route('/api/query', methods=['POST'])
def query():
    """
    Handle user queries and return RAG-based answers.
    
    Expected JSON payload:
        {
            "query": "user question",
            "top_k": 3  (optional)
        }
    
    Returns:
        {
            "query": "original query",
            "answer": "generated answer",
            "context": [list of retrieved chunks],
            "grounded": true/false
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({'error': 'Missing query parameter'}), 400
        
        user_query = data['query'].strip()
        top_k = data.get('top_k', 3)
        
        if not user_query:
            return jsonify({'error': 'Query cannot be empty'}), 400
        
        # Retrieve relevant chunks
        retrieved_chunks = rag.retrieve(user_query, top_k=top_k)
        
        # Generate answer
        result = llm.generate_answer(user_query, retrieved_chunks)
        
        # Format response
        response = {
            'query': user_query,
            'answer': result['answer'],
            'context': [
                {
                    'text': chunk['text'],
                    'source': chunk['source'],
                    'score': chunk['score']
                }
                for chunk in result['context_used']
            ],
            'grounded': result['grounded']
        }
        
        return jsonify(response)
    
    except Exception as e:
        print(f"Error processing query: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'documents_indexed': len(rag.chunks),
        'index_ready': rag.index is not None
    })


@app.route('/api/stats', methods=['GET'])
def stats():
    """Get system statistics."""
    return jsonify({
        'total_chunks': len(rag.chunks),
        'embedding_dimension': rag.embedding_dim,
        'model': 'all-MiniLM-L6-v2'
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
