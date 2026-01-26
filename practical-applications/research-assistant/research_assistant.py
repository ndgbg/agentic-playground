"""
Research Assistant

Web search, synthesis, and citation management.
"""

from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent, tool

app = BedrockAgentCoreApp()

# Simulated search results
SEARCH_DB = {
    "AI": [
        {"title": "Introduction to AI", "url": "example.com/ai", "snippet": "AI is intelligence demonstrated by machines..."},
        {"title": "AI Applications", "url": "example.com/ai-apps", "snippet": "AI is used in healthcare, finance, and more..."}
    ],
    "Python": [
        {"title": "Python Guide", "url": "example.com/python", "snippet": "Python is a versatile programming language..."},
        {"title": "Python for Data Science", "url": "example.com/python-ds", "snippet": "Python is popular for data analysis..."}
    ]
}

@tool
def web_search(query: str, max_results: int = 3) -> list:
    """Search the web for information"""
    query_lower = query.lower()
    
    for key in SEARCH_DB:
        if key.lower() in query_lower:
            return SEARCH_DB[key][:max_results]
    
    return []

@tool
def synthesize_sources(sources: list) -> str:
    """Synthesize information from multiple sources"""
    summary = "Based on multiple sources: "
    summary += " ".join([s["snippet"] for s in sources])
    return summary

@tool
def generate_citations(sources: list) -> list:
    """Generate citations for sources"""
    citations = []
    for i, source in enumerate(sources, 1):
        citations.append(f"[{i}] {source['title']} - {source['url']}")
    return citations

@app.entrypoint
def invoke(payload):
    """
    Research assistant agent.
    """
    query = payload.get("prompt")
    
    agent = Agent()
    agent.add_tool(web_search)
    agent.add_tool(synthesize_sources)
    agent.add_tool(generate_citations)
    
    result = agent(f"Research this topic and provide citations: {query}")
    
    return {"answer": result.message}

if __name__ == "__main__":
    print("Research Assistant Demo")
    print("=" * 60)
    
    queries = [
        "What is AI?",
        "Tell me about Python programming",
        "Research machine learning applications"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        response = invoke({"prompt": query})
        print(f"Answer: {response['answer']}")
        print("-" * 60)
    
    app.run()
