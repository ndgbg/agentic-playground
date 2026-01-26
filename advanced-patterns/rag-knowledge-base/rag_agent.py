"""
RAG Knowledge Base Agent

Retrieval-augmented generation with semantic search.
"""

from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent, tool

app = BedrockAgentCoreApp()

# Simulated knowledge base
KNOWLEDGE_BASE = [
    {"id": 1, "content": "Python is a high-level programming language known for readability.", "topic": "python"},
    {"id": 2, "content": "AWS Lambda is a serverless compute service.", "topic": "aws"},
    {"id": 3, "content": "Machine learning is a subset of artificial intelligence.", "topic": "ml"},
    {"id": 4, "content": "Docker containers package applications with dependencies.", "topic": "docker"},
    {"id": 5, "content": "Kubernetes orchestrates containerized applications.", "topic": "kubernetes"}
]

@tool
def search_knowledge_base(query: str, max_results: int = 3) -> list:
    """
    Search knowledge base with semantic search.
    
    Args:
        query: Search query
        max_results: Maximum results to return
    
    Returns:
        List of relevant documents
    """
    query_lower = query.lower()
    
    # Simple keyword matching (in production, use embeddings)
    results = []
    for doc in KNOWLEDGE_BASE:
        score = 0
        for word in query_lower.split():
            if word in doc["content"].lower():
                score += 1
        
        if score > 0:
            results.append({"doc": doc, "score": score})
    
    # Sort by score
    results.sort(key=lambda x: x["score"], reverse=True)
    
    return [r["doc"] for r in results[:max_results]]

@app.entrypoint
def invoke(payload):
    """
    RAG agent with knowledge base search.
    """
    query = payload.get("prompt")
    
    # Search knowledge base
    docs = search_knowledge_base(query)
    
    # Build context
    context = "\n".join([f"- {doc['content']}" for doc in docs])
    
    # Agent with context
    agent = Agent()
    prompt = f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer based on the context above."
    
    result = agent(prompt)
    
    return {
        "answer": result.message,
        "sources": [doc["id"] for doc in docs]
    }

if __name__ == "__main__":
    print("RAG Knowledge Base Demo")
    print("=" * 60)
    
    queries = [
        "What is Python?",
        "Tell me about AWS Lambda",
        "What is Kubernetes?",
        "Explain machine learning"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        response = invoke({"prompt": query})
        print(f"Answer: {response['answer']}")
        print(f"Sources: {response['sources']}")
        print("-" * 60)
    
    app.run()
