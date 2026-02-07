import os
import numpy as np
import faiss
import pickle
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer
import PyPDF2
from pathlib import Path


class RAGPipeline:
    def __init__(self, embedding_model_name: str = "all-MiniLM-L6-v2", chunk_size: int = 500, chunk_overlap: int = 50):
        """
        Initialize RAG pipeline with embedding model and chunking parameters.
        
        Args:
            embedding_model_name: Name of sentence-transformers model
            chunk_size: Maximum characters per chunk
            chunk_overlap: Overlap between consecutive chunks
        """
        print(f"Loading embedding model: {embedding_model_name}...")
        self.embedding_model = SentenceTransformer(embedding_model_name)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.chunks = []
        self.index = None
        self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
        
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text content from PDF file."""
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            print(f"Error reading {pdf_path}: {e}")
        return text
    
    def extract_text_from_txt(self, txt_path: str) -> str:
        """Extract text content from text file."""
        text = ""
        try:
            with open(txt_path, 'r', encoding='utf-8') as file:
                text = file.read()
        except Exception as e:
            print(f"Error reading {txt_path}: {e}")
        return text
    
    def chunk_text(self, text: str, source: str) -> List[Dict[str, str]]:
        """
        Split text into overlapping chunks with memory optimization.
        
        Args:
            text: Text to chunk
            source: Source document name
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        # Limit total text size BEFORE any processing to prevent memory issues
        max_text_length = 50000  # Reduced to 50KB per document for safety
        
        # Check and truncate FIRST
        if len(text) > max_text_length:
            print(f"  Warning: Document {source} is large ({len(text)} chars), truncating to {max_text_length}")
            text = text[:max_text_length]
        
        # Clean text but preserve some structure - do this AFTER truncation
        text = ' '.join(text.split())
        
        chunks = []
        start = 0
        chunk_count = 0
        max_chunks = 200  # Limit chunks per document to prevent memory issues
        
        while start < len(text) and chunk_count < max_chunks:
            end = min(start + self.chunk_size, len(text))
            
            # Find the last sentence boundary before chunk_size
            if end < len(text):
                last_period = text.rfind('.', start, end)
                if last_period > start:
                    end = last_period + 1
            
            chunk_text = text[start:end].strip()
            
            if chunk_text and len(chunk_text) > 10:  # Skip very small chunks
                chunks.append({
                    'text': chunk_text,
                    'source': source,
                    'start_pos': start
                })
                chunk_count += 1
            
            start = end - self.chunk_overlap
            if start >= len(text):
                break
        
        if chunk_count >= max_chunks:
            print(f"  Warning: Reached maximum chunk limit ({max_chunks}) for {source}")
            
        return chunks
    
    def process_documents(self, documents_dir: str = "documents"):
        """
        Process all documents in the directory and build vector index.
        
        Args:
            documents_dir: Directory containing PDF and TXT documents
        """
        print(f"\nProcessing documents from {documents_dir}...")
        
        documents_path = Path(documents_dir)
        if not documents_path.exists():
            print(f"Warning: {documents_dir} directory not found")
            return
        
        all_chunks = []
        max_total_chunks = 1000  # Global limit to prevent memory issues
        
        # Process PDF files
        pdf_files = list(documents_path.glob("*.pdf"))
        for pdf_file in pdf_files:
            if len(all_chunks) >= max_total_chunks:
                print(f"Warning: Reached maximum total chunks ({max_total_chunks}), skipping remaining files")
                break
                
            print(f"Processing: {pdf_file.name}")
            text = self.extract_text_from_pdf(str(pdf_file))
            
            if text.strip():
                chunks = self.chunk_text(text, pdf_file.name)
                # Only add chunks if we haven't exceeded the limit
                chunks_to_add = chunks[:max_total_chunks - len(all_chunks)]
                all_chunks.extend(chunks_to_add)
                print(f"  Created {len(chunks_to_add)} chunks (total: {len(all_chunks)})")
        
        # Process TXT files
        txt_files = list(documents_path.glob("*.txt"))
        for txt_file in txt_files:
            if len(all_chunks) >= max_total_chunks:
                print(f"Warning: Reached maximum total chunks ({max_total_chunks}), skipping remaining files")
                break
                
            print(f"Processing: {txt_file.name}")
            text = self.extract_text_from_txt(str(txt_file))
            
            if text.strip():
                chunks = self.chunk_text(text, txt_file.name)
                # Only add chunks if we haven't exceeded the limit
                chunks_to_add = chunks[:max_total_chunks - len(all_chunks)]
                all_chunks.extend(chunks_to_add)
                print(f"  Created {len(chunks_to_add)} chunks (total: {len(all_chunks)})")
        
        if not pdf_files and not txt_files:
            print(f"No PDF or TXT files found in {documents_dir}")
            return
        
        self.chunks = all_chunks
        print(f"\nTotal chunks created: {len(self.chunks)}")
        
        if self.chunks:
            self.build_index()
    
    def build_index(self):
        """Build FAISS vector index from document chunks with batch processing."""
        print("\nGenerating embeddings...")
        
        chunk_texts = [chunk['text'] for chunk in self.chunks]
        
        # Process embeddings in batches to reduce memory usage
        batch_size = 100
        all_embeddings = []
        
        for i in range(0, len(chunk_texts), batch_size):
            batch = chunk_texts[i:i+batch_size]
            batch_embeddings = self.embedding_model.encode(batch, show_progress_bar=True)
            all_embeddings.append(batch_embeddings)
        
        embeddings = np.vstack(all_embeddings).astype('float32')
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        
        print("Building FAISS index...")
        self.index = faiss.IndexFlatIP(self.embedding_dim)
        self.index.add(embeddings)
        
        print(f"Index built with {self.index.ntotal} vectors")
    
    def retrieve(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Retrieve top-k most relevant chunks for a query.
        
        Args:
            query: User query
            top_k: Number of chunks to retrieve
            
        Returns:
            List of retrieved chunks with scores
        """
        if self.index is None or len(self.chunks) == 0:
            return []
        
        # Encode query
        query_embedding = self.embedding_model.encode([query])
        query_embedding = np.array(query_embedding).astype('float32')
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = self.index.search(query_embedding, min(top_k, len(self.chunks)))
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.chunks):
                results.append({
                    'text': self.chunks[idx]['text'],
                    'source': self.chunks[idx]['source'],
                    'score': float(score)
                })
        
        return results
    
    def save_index(self, save_dir: str = "vector_store"):
        """Save the FAISS index and chunks to disk."""
        os.makedirs(save_dir, exist_ok=True)
        
        if self.index is not None:
            faiss.write_index(self.index, os.path.join(save_dir, "faiss.index"))
        
        with open(os.path.join(save_dir, "chunks.pkl"), 'wb') as f:
            pickle.dump(self.chunks, f)
        
        print(f"Index saved to {save_dir}")
    
    def load_index(self, save_dir: str = "vector_store"):
        """Load the FAISS index and chunks from disk."""
        index_path = os.path.join(save_dir, "faiss.index")
        chunks_path = os.path.join(save_dir, "chunks.pkl")
        
        if os.path.exists(index_path) and os.path.exists(chunks_path):
            self.index = faiss.read_index(index_path)
            
            with open(chunks_path, 'rb') as f:
                self.chunks = pickle.load(f)
            
            print(f"Loaded index with {self.index.ntotal} vectors")
            return True
        
        return False


if __name__ == "__main__":
    # Test the pipeline
    rag = RAGPipeline()
    
    # Try to load existing index or process documents
    if not rag.load_index():
        rag.process_documents()
        rag.save_index()
    
    # Test query
    query = "What factors affect construction project delays?"
    results = rag.retrieve(query, top_k=3)
    
    print(f"\nQuery: {query}")
    print("\nRetrieved chunks:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. Source: {result['source']}")
        print(f"   Score: {result['score']:.4f}")
        print(f"   Text: {result['text'][:200]}...")