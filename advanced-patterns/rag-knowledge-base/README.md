# RAG Knowledge Base

Retrieval-Augmented Generation system that combines semantic search with LLM responses. Query documents using natural language and get accurate answers with source citations.

## Overview

This agent implements RAG (Retrieval-Augmented Generation) to answer questions by first retrieving relevant context from a knowledge base, then generating responses grounded in that context. Perfect for Q&A systems, documentation search, and knowledge management.

## Quick Start

```bash
cd advanced-patterns/rag-knowledge-base
pip install -r requirements.txt
python rag_agent.py
```

**Output:**
```
RAG Knowledge Base Agent
============================================================

Query: What is Python?
Response: Python is a high-level, interpreted programming language known for its 
simplicity and readability. It supports multiple programming paradigms including 
procedural, object-oriented, and functional programming.

Sources:
[1] Python Programming Guide - Section 1.1
[2] Introduction to Python - Chapter 2
============================================================

Query: How do I use decorators?
Response: Decorators in Python are functions that modify the behavior of other 
functions. Use the @decorator_name syntax above a function definition...

Sources:
[1] Advanced Python Patterns - Section 4.3
============================================================
```

## How It Works

### 1. Document Ingestion

Load and chunk documents:
```python
documents = [
    {"id": "doc1", "text": "Python is a programming language...", "metadata": {"source": "guide.pdf"}},
    {"id": "doc2", "text": "Decorators modify function behavior...", "metadata": {"source": "advanced.pdf"}}
]
```

### 2. Embedding Generation

Convert text to vectors:
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode([doc["text"] for doc in documents])
```

### 3. Semantic Search

Find relevant documents:
```python
query_embedding = model.encode(query)
similarities = cosine_similarity([query_embedding], embeddings)[0]
top_docs = sorted(zip(documents, similarities), key=lambda x: x[1], reverse=True)[:3]
```

### 4. Context-Aware Generation

Generate answer with retrieved context:
```python
context = "\n".join([doc["text"] for doc, _ in top_docs])
prompt = f"Context: {context}\n\nQuestion: {query}\n\nAnswer:"
response = llm.generate(prompt)
```

## Available Tools

### search_knowledge_base()
Semantic search over documents:
```python
search_knowledge_base(query="What is Python?", top_k=3)
# Returns: [(doc1, 0.92), (doc2, 0.85), (doc3, 0.78)]
```

### add_document()
Add new documents to knowledge base:
```python
add_document(
    text="New content here",
    metadata={"source": "new.pdf", "page": 1}
)
```

### get_sources()
Retrieve source citations:
```python
get_sources(doc_ids=["doc1", "doc2"])
# Returns: ["guide.pdf - Section 1.1", "advanced.pdf - Chapter 4"]
```

## Example Queries

### Factual Questions
```
"What is machine learning?"
"How does HTTP work?"
"What are design patterns?"
```

### How-To Questions
```
"How do I deploy to AWS?"
"How to use async/await?"
"How to optimize database queries?"
```

### Comparison Questions
```
"What's the difference between REST and GraphQL?"
"Compare Python and JavaScript"
"SQL vs NoSQL databases"
```

## Customization

### Use Vector Database

```python
from pinecone import Pinecone

pc = Pinecone(api_key="your-key")
index = pc.Index("knowledge-base")

@tool
def search_knowledge_base(query: str, top_k: int = 3) -> list:
    """Search using Pinecone"""
    query_embedding = model.encode(query).tolist()
    results = index.query(vector=query_embedding, top_k=top_k, include_metadata=True)
    return [(match.metadata["text"], match.score) for match in results.matches]
```

### Add Document Chunking

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

@tool
def add_document(text: str, metadata: dict) -> str:
    """Add document with chunking"""
    chunks = splitter.split_text(text)
    for i, chunk in enumerate(chunks):
        chunk_metadata = {**metadata, "chunk": i}
        embeddings = model.encode(chunk)
        index.upsert([(f"{metadata['id']}_{i}", embeddings, chunk_metadata)])
    return f"Added {len(chunks)} chunks"
```

### Add Reranking

```python
from sentence_transformers import CrossEncoder

reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

@tool
def rerank_results(query: str, documents: list) -> list:
    """Rerank search results"""
    pairs = [[query, doc["text"]] for doc in documents]
    scores = reranker.predict(pairs)
    return sorted(zip(documents, scores), key=lambda x: x[1], reverse=True)
```

## Integration Examples

### Load from PDF

```python
from PyPDF2 import PdfReader

def load_pdf(file_path: str) -> list:
    reader = PdfReader(file_path)
    documents = []
    for i, page in enumerate(reader.pages):
        documents.append({
            "id": f"{file_path}_page_{i}",
            "text": page.extract_text(),
            "metadata": {"source": file_path, "page": i+1}
        })
    return documents
```

### Load from Website

```python
import requests
from bs4 import BeautifulSoup

def load_website(url: str) -> dict:
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    text = soup.get_text()
    return {
        "id": url,
        "text": text,
        "metadata": {"source": url, "type": "webpage"}
    }
```

### Load from Database

```python
import psycopg2

def load_from_db(query: str) -> list:
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cursor = conn.cursor()
    cursor.execute(query)
    
    documents = []
    for row in cursor.fetchall():
        documents.append({
            "id": row[0],
            "text": row[1],
            "metadata": {"source": "database", "table": "articles"}
        })
    return documents
```

## Deploy to Production

### Use Amazon Bedrock Knowledge Base

```python
import boto3

bedrock = boto3.client('bedrock-agent')

# Create knowledge base
kb_response = bedrock.create_knowledge_base(
    name='my-knowledge-base',
    roleArn='arn:aws:iam::123:role/bedrock-kb-role',
    storageConfiguration={
        'type': 'OPENSEARCH_SERVERLESS',
        'opensearchServerlessConfiguration': {
            'collectionArn': 'arn:aws:aoss:...',
            'vectorIndexName': 'knowledge-base-index'
        }
    }
)

# Query knowledge base
@tool
def search_knowledge_base(query: str) -> list:
    response = bedrock.retrieve(
        knowledgeBaseId=kb_response['knowledgeBaseId'],
        retrievalQuery={'text': query}
    )
    return response['retrievalResults']
```

### Use OpenSearch

```python
from opensearchpy import OpenSearch

client = OpenSearch(
    hosts=[{'host': 'localhost', 'port': 9200}],
    http_auth=('admin', 'admin')
)

@tool
def search_knowledge_base(query: str) -> list:
    query_embedding = model.encode(query).tolist()
    response = client.search(
        index='knowledge-base',
        body={
            'query': {
                'knn': {
                    'embedding': {
                        'vector': query_embedding,
                        'k': 3
                    }
                }
            }
        }
    )
    return [hit['_source'] for hit in response['hits']['hits']]
```

## Use Cases

### Documentation Q&A
Answer questions about product documentation without manual searching.

### Customer Support
Provide accurate answers based on support articles and FAQs.

### Research Assistant
Query research papers and technical documents for insights.

### Internal Knowledge Management
Search company wikis, policies, and procedures.

## Best Practices

### Chunk Size Optimization
```python
# Too small: loses context
chunk_size = 100  # ❌

# Too large: less precise retrieval
chunk_size = 5000  # ❌

# Just right: balance context and precision
chunk_size = 500  # ✅
chunk_overlap = 50  # ✅
```

### Metadata Enrichment
```python
metadata = {
    "source": "guide.pdf",
    "page": 42,
    "section": "Advanced Topics",
    "author": "John Doe",
    "date": "2026-01-26",
    "tags": ["python", "advanced"]
}
```

### Hybrid Search
```python
# Combine semantic and keyword search
semantic_results = semantic_search(query)
keyword_results = keyword_search(query)
combined = merge_and_rerank(semantic_results, keyword_results)
```

## Troubleshooting

**Poor Retrieval Quality**
- Adjust chunk size and overlap
- Try different embedding models
- Add reranking step
- Improve metadata

**Slow Search**
- Use vector database (Pinecone, Weaviate)
- Add caching
- Reduce embedding dimensions
- Batch queries

**Irrelevant Answers**
- Increase top_k for more context
- Add relevance threshold
- Improve document quality
- Use better prompts

## Next Steps

1. Load your documents (PDF, web, database)
2. Choose vector database (Pinecone, OpenSearch, Bedrock)
3. Tune chunk size and retrieval parameters
4. Add reranking for better results
5. Deploy to production
