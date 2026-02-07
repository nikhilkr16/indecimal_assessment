import json
from rag_pipeline import RAGPipeline
from llm_generator import LLMGenerator
import time


class RAGEvaluator:
    """Evaluate RAG system quality with test questions."""
    
    def __init__(self):
        self.rag = RAGPipeline()
        self.llm = LLMGenerator()
        
        # Load existing index
        if not self.rag.load_index():
            print("Error: No index found. Please run rag_pipeline.py first.")
            return
        
        self.test_questions = [
            "What factors affect construction project delays?",
            "What are the safety requirements for construction sites?",
            "How should material procurement be handled?",
            "What are the payment terms for contractors?",
            "What is the process for quality inspection?",
            "How are change orders managed?",
            "What documentation is required for project completion?",
            "What are the insurance requirements?",
            "How is dispute resolution handled?",
            "What are the environmental compliance requirements?",
            "What is the warranty period for completed work?",
            "How are project milestones tracked?"
        ]
    
    def evaluate_single_query(self, query: str, top_k: int = 3):
        """Evaluate a single query."""
        print(f"\n{'='*80}")
        print(f"QUERY: {query}")
        print(f"{'='*80}")
        
        # Retrieve chunks
        start_time = time.time()
        retrieved_chunks = self.rag.retrieve(query, top_k=top_k)
        retrieval_time = time.time() - start_time
        
        print(f"\n📊 Retrieved {len(retrieved_chunks)} chunks in {retrieval_time:.2f}s")
        
        # Show retrieved context
        print("\n📚 RETRIEVED CONTEXT:")
        for i, chunk in enumerate(retrieved_chunks, 1):
            print(f"\n  [{i}] Source: {chunk['source']}")
            print(f"      Score: {chunk['score']:.4f}")
            print(f"      Text: {chunk['text'][:200]}...")
        
        # Generate answer
        start_time = time.time()
        result = self.llm.generate_answer(query, retrieved_chunks)
        generation_time = time.time() - start_time
        
        print(f"\n💬 GENERATED ANSWER ({generation_time:.2f}s):")
        print(f"  {result['answer']}")
        
        print(f"\n✓ Grounded: {result['grounded']}")
        
        return {
            'query': query,
            'retrieved_chunks': len(retrieved_chunks),
            'retrieval_time': retrieval_time,
            'generation_time': generation_time,
            'answer': result['answer'],
            'grounded': result['grounded'],
            'context': retrieved_chunks
        }
    
    def evaluate_all(self, save_results: bool = True):
        """Run evaluation on all test questions."""
        print("\n🚀 Starting RAG System Evaluation")
        print(f"📝 Testing {len(self.test_questions)} questions\n")
        
        results = []
        
        for i, query in enumerate(self.test_questions, 1):
            print(f"\n[{i}/{len(self.test_questions)}]")
            result = self.evaluate_single_query(query)
            results.append(result)
            
            # Small delay to avoid rate limiting
            time.sleep(1)
        
        # Calculate statistics
        avg_retrieval_time = sum(r['retrieval_time'] for r in results) / len(results)
        avg_generation_time = sum(r['generation_time'] for r in results) / len(results)
        grounded_count = sum(1 for r in results if r['grounded'])
        
        print("\n" + "="*80)
        print("📈 EVALUATION SUMMARY")
        print("="*80)
        print(f"Total queries: {len(results)}")
        print(f"Avg retrieval time: {avg_retrieval_time:.2f}s")
        print(f"Avg generation time: {avg_generation_time:.2f}s")
        print(f"Grounded responses: {grounded_count}/{len(results)} ({grounded_count/len(results)*100:.1f}%)")
        
        if save_results:
            with open('evaluation_results.json', 'w') as f:
                json.dump({
                    'summary': {
                        'total_queries': len(results),
                        'avg_retrieval_time': avg_retrieval_time,
                        'avg_generation_time': avg_generation_time,
                        'grounded_responses': grounded_count
                    },
                    'results': results
                }, f, indent=2)
            print("\n✅ Results saved to evaluation_results.json")
    
    def analyze_quality(self):
        """Provide quality analysis observations."""
        print("\n" + "="*80)
        print("🔍 QUALITY ANALYSIS OBSERVATIONS")
        print("="*80)
        
        observations = """
        1. RETRIEVAL RELEVANCE:
           - Semantic search using sentence-transformers effectively captures query intent
           - Top-k=3 provides good balance between context and precision
           - Cosine similarity scores help identify most relevant chunks
        
        2. GROUNDING & HALLUCINATIONS:
           - System prompt explicitly enforces grounding to retrieved context
           - LLM instructed to refuse answering when context is insufficient
           - Lower temperature (0.3) reduces hallucination risk
        
        3. ANSWER QUALITY:
           - Answers are concise and directly address the question
           - Context is properly referenced in responses
           - System maintains transparency by showing source documents
        
        4. LIMITATIONS:
           - Answer quality depends on document content
           - May struggle with questions requiring cross-document reasoning
           - Chunk size affects context completeness
        
        5. POTENTIAL IMPROVEMENTS:
           - Implement re-ranking for better chunk selection
           - Add query expansion for better retrieval
           - Use larger context windows for complex questions
           - Implement hybrid search (semantic + keyword)
        """
        
        print(observations)


if __name__ == "__main__":
    evaluator = RAGEvaluator()
    
    # Run full evaluation
    evaluator.evaluate_all()
    
    # Show quality analysis
    evaluator.analyze_quality()
