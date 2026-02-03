#!/usr/bin/env python3
"""
Personal Knowledge Base MCP Server with RAG
Semantic search over personal documents, notes, and knowledge.
"""

import json
import sqlite3
from datetime import datetime
from typing import List, Dict
import hashlib

class KnowledgeBaseServer:
    def __init__(self, db_path: str = "knowledge.db"):
        self.name = "knowledge-base"
        self.db_path = db_path
        self.tools = {}
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS documents
                     (id TEXT PRIMARY KEY,
                      title TEXT,
                      content TEXT,
                      tags TEXT,
                      created_at TEXT,
                      updated_at TEXT,
                      metadata TEXT)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS embeddings
                     (doc_id TEXT,
                      chunk_id INTEGER,
                      chunk_text TEXT,
                      embedding_hash TEXT,
                      PRIMARY KEY (doc_id, chunk_id))''')
        
        c.execute('''CREATE VIRTUAL TABLE IF NOT EXISTS fts_documents
                     USING fts5(title, content, tags)''')
        
        conn.commit()
        conn.close()
    
    def register_tool(self, name: str, description: str, handler, schema: dict):
        self.tools[name] = {
            "name": name,
            "description": description,
            "handler": handler,
            "inputSchema": schema
        }
    
    def call_tool(self, name: str, arguments: dict):
        if name not in self.tools:
            return {"error": f"Unknown tool: {name}"}
        return self.tools[name]["handler"](arguments)
    
    def add_document(self, args: dict) -> dict:
        """Add a document to the knowledge base."""
        doc_id = hashlib.md5(args["title"].encode()).hexdigest()
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        now = datetime.now().isoformat()
        tags = json.dumps(args.get("tags", []))
        metadata = json.dumps(args.get("metadata", {}))
        
        c.execute('''INSERT OR REPLACE INTO documents
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (doc_id, args["title"], args["content"], tags, now, now, metadata))
        
        # Add to FTS index
        c.execute('''INSERT OR REPLACE INTO fts_documents(rowid, title, content, tags)
                     VALUES ((SELECT rowid FROM documents WHERE id = ?), ?, ?, ?)''',
                  (doc_id, args["title"], args["content"], tags))
        
        # Chunk and store for semantic search
        chunks = self._chunk_text(args["content"])
        for i, chunk in enumerate(chunks):
            embedding_hash = hashlib.md5(chunk.encode()).hexdigest()
            c.execute('''INSERT OR REPLACE INTO embeddings
                         VALUES (?, ?, ?, ?)''',
                      (doc_id, i, chunk, embedding_hash))
        
        conn.commit()
        conn.close()
        
        return {
            "doc_id": doc_id,
            "title": args["title"],
            "chunks": len(chunks),
            "message": "Document added successfully"
        }
    
    def search_documents(self, args: dict) -> dict:
        """Search documents using full-text search."""
        query = args["query"]
        limit = args.get("limit", 10)
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # FTS search
        c.execute('''SELECT d.id, d.title, d.content, d.tags, d.created_at
                     FROM documents d
                     JOIN fts_documents fts ON d.rowid = fts.rowid
                     WHERE fts_documents MATCH ?
                     ORDER BY rank
                     LIMIT ?''', (query, limit))
        
        results = []
        for row in c.fetchall():
            doc_id, title, content, tags, created = row
            results.append({
                "id": doc_id,
                "title": title,
                "snippet": content[:200] + "..." if len(content) > 200 else content,
                "tags": json.loads(tags),
                "created_at": created,
                "relevance": "high"
            })
        
        conn.close()
        
        return {
            "query": query,
            "results": results,
            "count": len(results)
        }
    
    def semantic_search(self, args: dict) -> dict:
        """Semantic search using embeddings (simplified)."""
        query = args["query"]
        limit = args.get("limit", 5)
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Simple keyword matching in chunks (in production, use actual embeddings)
        query_words = set(query.lower().split())
        
        c.execute('''SELECT DISTINCT e.doc_id, e.chunk_text, d.title
                     FROM embeddings e
                     JOIN documents d ON e.doc_id = d.id
                     LIMIT ?''', (limit * 3,))
        
        chunks = []
        for row in c.fetchall():
            doc_id, chunk_text, title = row
            chunk_words = set(chunk_text.lower().split())
            overlap = len(query_words & chunk_words)
            
            if overlap > 0:
                chunks.append({
                    "doc_id": doc_id,
                    "title": title,
                    "text": chunk_text,
                    "score": overlap / len(query_words)
                })
        
        # Sort by score and limit
        chunks.sort(key=lambda x: x["score"], reverse=True)
        chunks = chunks[:limit]
        
        conn.close()
        
        return {
            "query": query,
            "chunks": chunks,
            "count": len(chunks)
        }
    
    def get_document(self, args: dict) -> dict:
        """Get a document by ID."""
        doc_id = args["doc_id"]
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''SELECT title, content, tags, created_at, updated_at, metadata
                     FROM documents WHERE id = ?''', (doc_id,))
        
        row = c.fetchone()
        conn.close()
        
        if not row:
            return {"error": "Document not found"}
        
        title, content, tags, created, updated, metadata = row
        
        return {
            "id": doc_id,
            "title": title,
            "content": content,
            "tags": json.loads(tags),
            "created_at": created,
            "updated_at": updated,
            "metadata": json.loads(metadata)
        }
    
    def list_tags(self, args: dict) -> dict:
        """List all unique tags."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('SELECT tags FROM documents')
        
        all_tags = set()
        for row in c.fetchall():
            tags = json.loads(row[0])
            all_tags.update(tags)
        
        conn.close()
        
        return {
            "tags": sorted(list(all_tags)),
            "count": len(all_tags)
        }
    
    def get_stats(self, args: dict) -> dict:
        """Get knowledge base statistics."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('SELECT COUNT(*) FROM documents')
        doc_count = c.fetchone()[0]
        
        c.execute('SELECT COUNT(*) FROM embeddings')
        chunk_count = c.fetchone()[0]
        
        c.execute('SELECT SUM(LENGTH(content)) FROM documents')
        total_chars = c.fetchone()[0] or 0
        
        conn.close()
        
        return {
            "documents": doc_count,
            "chunks": chunk_count,
            "total_characters": total_chars,
            "avg_doc_size": total_chars // doc_count if doc_count > 0 else 0
        }
    
    def _chunk_text(self, text: str, chunk_size: int = 500) -> List[str]:
        """Split text into chunks for embedding."""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
        
        return chunks

# Initialize server
server = KnowledgeBaseServer()

# Register tools
server.register_tool(
    "add_document",
    "Add a document to the knowledge base",
    server.add_document,
    {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "content": {"type": "string"},
            "tags": {"type": "array", "items": {"type": "string"}},
            "metadata": {"type": "object"}
        },
        "required": ["title", "content"]
    }
)

server.register_tool(
    "search_documents",
    "Full-text search across documents",
    server.search_documents,
    {
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "limit": {"type": "integer"}
        },
        "required": ["query"]
    }
)

server.register_tool(
    "semantic_search",
    "Semantic search using embeddings",
    server.semantic_search,
    {
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "limit": {"type": "integer"}
        },
        "required": ["query"]
    }
)

server.register_tool(
    "get_document",
    "Get a document by ID",
    server.get_document,
    {
        "type": "object",
        "properties": {
            "doc_id": {"type": "string"}
        },
        "required": ["doc_id"]
    }
)

server.register_tool(
    "list_tags",
    "List all tags in the knowledge base",
    server.list_tags,
    {"type": "object", "properties": {}}
)

server.register_tool(
    "get_stats",
    "Get knowledge base statistics",
    server.get_stats,
    {"type": "object", "properties": {}}
)

def main():
    print("📚 Personal Knowledge Base with RAG")
    print("=" * 60)
    
    # Add sample documents
    print("\n1. Adding documents...")
    
    result = server.call_tool("add_document", {
        "title": "Python Best Practices",
        "content": "Use type hints for better code clarity. Follow PEP 8 style guide. Write docstrings for all functions. Use virtual environments for project isolation.",
        "tags": ["python", "programming", "best-practices"]
    })
    print(f"✓ Added: {result['title']} ({result['chunks']} chunks)")
    
    result = server.call_tool("add_document", {
        "title": "AWS Lambda Tips",
        "content": "Keep functions small and focused. Use environment variables for configuration. Implement proper error handling. Monitor with CloudWatch. Optimize cold starts by minimizing dependencies.",
        "tags": ["aws", "lambda", "serverless"]
    })
    print(f"✓ Added: {result['title']} ({result['chunks']} chunks)")
    
    result = server.call_tool("add_document", {
        "title": "MCP Server Development",
        "content": "Model Context Protocol enables AI agents to use tools. Implement stdio transport for communication. Register tools with clear schemas. Handle errors gracefully. Log all operations for debugging.",
        "tags": ["mcp", "ai", "development"]
    })
    print(f"✓ Added: {result['title']} ({result['chunks']} chunks)")
    
    print("\n" + "-" * 60)
    
    # Search
    print("\n2. Full-text search for 'python'...")
    result = server.call_tool("search_documents", {"query": "python"})
    print(f"Found {result['count']} results:")
    for doc in result['results']:
        print(f"  • {doc['title']}")
        print(f"    {doc['snippet']}")
    
    print("\n" + "-" * 60)
    
    # Semantic search
    print("\n3. Semantic search for 'error handling'...")
    result = server.call_tool("semantic_search", {"query": "error handling"})
    print(f"Found {result['count']} relevant chunks:")
    for chunk in result['chunks']:
        print(f"  • {chunk['title']} (score: {chunk['score']:.2f})")
        print(f"    {chunk['text'][:100]}...")
    
    print("\n" + "-" * 60)
    
    # List tags
    print("\n4. All tags...")
    result = server.call_tool("list_tags", {})
    print(f"Tags ({result['count']}): {', '.join(result['tags'])}")
    
    print("\n" + "-" * 60)
    
    # Stats
    print("\n5. Knowledge base statistics...")
    result = server.call_tool("get_stats", {})
    print(f"Documents: {result['documents']}")
    print(f"Chunks: {result['chunks']}")
    print(f"Total characters: {result['total_characters']:,}")
    print(f"Avg doc size: {result['avg_doc_size']} chars")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
