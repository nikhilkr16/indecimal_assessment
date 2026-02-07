# Sample Documents

This folder should contain the PDF documents for the RAG system to process.

## Required Documents

Download and place the following documents here:

1. **Document 1**: [Download](https://drive.google.com/file/d/1oWcyH0XkzpHeWozMBWJSFEUEw70Lrc2-/view?usp=sharing)
2. **Document 2**: [Download](https://drive.google.com/file/d/1m1SudlRSlEK7y_-jweDjhPB5VVWzmQ7-/view?usp=sharing)
3. **Document 3**: [Download](https://drive.google.com/file/d/1suFO8EBLxRH6hKKcJln4a9PRsOGu2oYj/view?usp=sharing)

## Supported Formats

Currently, only **PDF files** are supported.

## Processing

Once documents are added here, run:

```bash
python rag_pipeline.py
```

This will:
- Extract text from PDFs
- Split into chunks
- Generate embeddings
- Build FAISS index

## File Structure

After processing, your folder structure will look like:

```
documents/
├── document1.pdf
├── document2.pdf
└── document3.pdf
```
