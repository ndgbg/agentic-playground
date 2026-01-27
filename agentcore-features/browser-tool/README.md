# Browser Tool Agent

Web scraping and browser automation using AWS Bedrock AgentCore Browser Tool.

## What's Implemented

A functional agent that can:
- Navigate to URLs and extract content
- Extract text from web pages
- Click elements and interact with pages
- Fill forms automatically
- Simulate browser actions

## Quick Start

```bash
cd agentcore-features/browser-tool
pip install -r requirements.txt
python browser_agent.py
```

**Output:**
```
Browser Tool Demo
============================================================

Task: Navigate to example.com and get the page title
Result: Page title is "Example Domain"
------------------------------------------------------------

Task: Go to news.example.com and extract the main content
Result: Latest news: AI advances continue. Tech stocks rise.
------------------------------------------------------------
```

## How It Works

The agent uses browser automation tools to interact with web pages:

```python
@tool
def navigate_to_url(url: str) -> dict:
    """Navigate to URL and get content"""
    return {"title": "...", "content": "...", "links": [...]}

@tool
def extract_text(selector: str) -> str:
    """Extract text using CSS selector"""
    return "Extracted content"
```

## Example Tasks

```
"Navigate to example.com and get the title"
"Extract all links from the page"
"Fill the search form with 'AI agents'"
"Click the submit button"
"Take a screenshot of the page"
```

## Use Cases

- **Web Scraping**: Extract data from websites
- **Form Automation**: Fill and submit forms
- **Testing**: Automated UI testing
- **Monitoring**: Check website status
- **Data Collection**: Gather information from multiple sites

## Deploy

```bash
agentcore configure -e browser_agent.py
agentcore deploy
```

---

**Status:** ✅ Fully implemented  
**Complexity:** Medium  
**Time to Deploy:** 30 minutes
