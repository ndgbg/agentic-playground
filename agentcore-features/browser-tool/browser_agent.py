"""
Browser Tool Agent

Web scraping and browser automation.
"""

from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent, tool

app = BedrockAgentCoreApp()

# Simulated web pages
WEB_PAGES = {
    "example.com": {
        "title": "Example Domain",
        "content": "This domain is for use in illustrative examples.",
        "links": ["about.html", "contact.html"]
    },
    "news.example.com": {
        "title": "News Site",
        "content": "Latest news: AI advances continue. Tech stocks rise.",
        "links": ["article1.html", "article2.html"]
    }
}

@tool
def navigate_to_url(url: str) -> dict:
    """Navigate to a URL and get page content"""
    domain = url.replace("http://", "").replace("https://", "").split("/")[0]
    
    if domain in WEB_PAGES:
        return WEB_PAGES[domain]
    
    return {"error": "Page not found"}

@tool
def extract_text(selector: str) -> str:
    """Extract text from page using selector"""
    # Simulated extraction
    return "Extracted text content"

@tool
def click_element(selector: str) -> str:
    """Click an element on the page"""
    return f"Clicked element: {selector}"

@tool
def fill_form(field: str, value: str) -> str:
    """Fill a form field"""
    return f"Filled {field} with {value}"

@app.entrypoint
def invoke(payload):
    """
    Browser automation agent.
    """
    task = payload.get("prompt")
    
    agent = Agent()
    agent.add_tool(navigate_to_url)
    agent.add_tool(extract_text)
    agent.add_tool(click_element)
    agent.add_tool(fill_form)
    
    result = agent(task)
    
    return {"result": result.message}

if __name__ == "__main__":
    print("Browser Tool Demo")
    print("=" * 60)
    
    tasks = [
        "Navigate to example.com and get the page title",
        "Go to news.example.com and extract the main content",
        "Find all links on example.com"
    ]
    
    for task in tasks:
        print(f"\nTask: {task}")
        response = invoke({"prompt": task})
        print(f"Result: {response['result']}")
        print("-" * 60)
    
    app.run()
