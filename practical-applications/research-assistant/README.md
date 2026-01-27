# Research Assistant

Web search, source synthesis, and citation management. Gather information from multiple sources and create well-cited research summaries.

## Overview

Automate research tasks by searching the web, synthesizing information from multiple sources, and generating properly cited summaries. Perfect for literature reviews, fact-checking, and information gathering.

## Quick Start

```bash
cd practical-applications/research-assistant
pip install -r requirements.txt
python research_assistant.py
```

**Output:**
```
Research Assistant
============================================================

Query: What is artificial intelligence?

Research Results:
============================================================

Artificial intelligence (AI) refers to the simulation of human 
intelligence in machines programmed to think and learn like humans [1]. 
The field was founded in 1956 and has grown to encompass machine 
learning, natural language processing, and computer vision [2].

Key applications include:
- Autonomous vehicles [3]
- Medical diagnosis [4]
- Natural language processing [1]
- Robotics and automation [2]

Recent advances in deep learning have enabled breakthroughs in image 
recognition and language understanding [3]. However, concerns about 
AI safety and ethics remain important considerations [4].

Sources:
[1] Introduction to AI - stanford.edu/ai-intro
[2] History of Artificial Intelligence - mit.edu/ai-history
[3] Deep Learning Advances - arxiv.org/dl-2024
[4] AI Ethics and Safety - ethics.ai/safety-concerns

============================================================
```

## Features

### Web Search
Search multiple sources:
- Academic papers
- News articles
- Documentation
- Blogs and forums

### Source Synthesis
Combine information:
- Extract key points
- Identify common themes
- Resolve contradictions
- Summarize findings

### Citation Management
Proper attribution:
- Numbered citations
- Source URLs
- Publication dates
- Author information

### Fact Checking
Verify information:
- Cross-reference sources
- Identify conflicts
- Check credibility
- Flag unverified claims

## Available Tools

### search_web()
Search for information:
```python
search_web(query="machine learning", num_results=5)
# Returns: [{"title": "...", "url": "...", "snippet": "..."}]
```

### extract_content()
Get full content from URL:
```python
extract_content(url="https://example.com/article")
# Returns: {"title": "...", "content": "...", "author": "..."}
```

### synthesize_sources()
Combine multiple sources:
```python
synthesize_sources(sources=[source1, source2, source3])
# Returns: "Summary with citations [1][2][3]"
```

### generate_bibliography()
Create citation list:
```python
generate_bibliography(sources)
# Returns: "[1] Title - Author - URL\n[2] ..."
```

## Example Queries

### Research Questions
```
"What are the latest developments in quantum computing?"
"How does CRISPR gene editing work?"
"What is the impact of climate change on agriculture?"
```

### Comparative Analysis
```
"Compare React vs Vue.js for web development"
"Differences between SQL and NoSQL databases"
"Python vs JavaScript for backend development"
```

### Literature Review
```
"Recent research on transformer models in NLP"
"Studies on remote work productivity"
"Meta-analysis of meditation benefits"
```

## Customization

### Add Academic Search

```python
import requests

@tool
def search_arxiv(query: str, max_results: int = 5) -> list:
    """Search arXiv for academic papers"""
    response = requests.get(
        "http://export.arxiv.org/api/query",
        params={
            "search_query": f"all:{query}",
            "max_results": max_results
        }
    )
    
    # Parse XML response
    papers = []
    for entry in parse_arxiv_xml(response.text):
        papers.append({
            "title": entry["title"],
            "authors": entry["authors"],
            "abstract": entry["abstract"],
            "url": entry["url"],
            "published": entry["published"]
        })
    
    return papers
```

### Add PDF Extraction

```python
from PyPDF2 import PdfReader
import requests

@tool
def extract_pdf_content(url: str) -> str:
    """Extract text from PDF"""
    response = requests.get(url)
    
    with open('/tmp/paper.pdf', 'wb') as f:
        f.write(response.content)
    
    reader = PdfReader('/tmp/paper.pdf')
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    
    return text
```

### Add Citation Formatting

```python
@tool
def format_citation(source: dict, style: str = "apa") -> str:
    """Format citation in different styles"""
    if style == "apa":
        return f"{source['author']} ({source['year']}). {source['title']}. {source['url']}"
    elif style == "mla":
        return f"{source['author']}. \"{source['title']}.\" {source['year']}. {source['url']}"
    elif style == "chicago":
        return f"{source['author']}. \"{source['title']}.\" {source['year']}. {source['url']}"
```

## Integration Examples

### Notion Integration

```python
from notion_client import Client

notion = Client(auth=os.getenv("NOTION_TOKEN"))

def save_research_to_notion(query: str, results: dict):
    # Create page
    page = notion.pages.create(
        parent={"database_id": DATABASE_ID},
        properties={
            "Name": {"title": [{"text": {"content": query}}]},
            "Status": {"select": {"name": "Complete"}}
        },
        children=[
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"text": {"content": results["summary"]}}]
                }
            },
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"text": {"content": "Sources"}}]
                }
            }
        ]
    )
    
    # Add sources
    for source in results["sources"]:
        notion.blocks.children.append(
            block_id=page["id"],
            children=[{
                "object": "block",
                "type": "bookmark",
                "bookmark": {"url": source["url"]}
            }]
        )
```

### Obsidian Integration

```python
def save_to_obsidian(query: str, results: dict, vault_path: str):
    """Save research to Obsidian vault"""
    filename = f"{vault_path}/{query.replace(' ', '_')}.md"
    
    content = f"""# {query}

## Summary
{results['summary']}

## Sources
"""
    
    for i, source in enumerate(results['sources'], 1):
        content += f"\n[{i}] [{source['title']}]({source['url']})"
    
    with open(filename, 'w') as f:
        f.write(content)
```

### Slack Bot

```python
from slack_bolt import App

app = App(token=SLACK_TOKEN)

@app.command("/research")
def handle_research(ack, command, say):
    ack()
    
    query = command['text']
    results = research_assistant(query)
    
    say(f"""
    *Research Results: {query}*
    
    {results['summary']}
    
    *Sources:*
    {results['bibliography']}
    """)
```

## Deploy to Production

### API Endpoint

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/research", methods=["POST"])
def research_endpoint():
    query = request.json["query"]
    max_sources = request.json.get("max_sources", 5)
    
    # Search
    sources = search_web(query, max_sources)
    
    # Extract content
    for source in sources:
        source["content"] = extract_content(source["url"])
    
    # Synthesize
    summary = synthesize_sources(sources)
    bibliography = generate_bibliography(sources)
    
    return jsonify({
        "query": query,
        "summary": summary,
        "sources": sources,
        "bibliography": bibliography
    })
```

### Lambda Function

```python
import json

def lambda_handler(event, context):
    query = event['query']
    
    # Research
    sources = search_web(query)
    summary = synthesize_sources(sources)
    
    # Store in S3
    s3.put_object(
        Bucket='research-results',
        Key=f"{query}.json",
        Body=json.dumps({
            "summary": summary,
            "sources": sources
        })
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps({'summary': summary})
    }
```

## Use Cases

### Academic Research
Gather sources for literature reviews and research papers.

### Competitive Analysis
Research competitors and market trends.

### Due Diligence
Investigate companies, products, or technologies.

### Content Creation
Research topics for articles, blogs, and reports.

### Fact Checking
Verify claims and find supporting evidence.

## Best Practices

### Source Quality
```python
TRUSTED_DOMAINS = [
    "edu",  # Educational institutions
    "gov",  # Government sites
    "org",  # Organizations
    "arxiv.org",  # Academic papers
    "scholar.google.com"
]

def is_trusted_source(url: str) -> bool:
    return any(domain in url for domain in TRUSTED_DOMAINS)
```

### Citation Accuracy
```python
def validate_citation(source: dict) -> bool:
    required_fields = ["title", "url", "date"]
    return all(field in source for field in required_fields)
```

### Avoid Plagiarism
```python
def paraphrase_content(text: str) -> str:
    """Paraphrase to avoid direct copying"""
    prompt = f"Paraphrase this text while preserving meaning: {text}"
    return llm.invoke(prompt)
```

## Troubleshooting

**Poor Search Results**
- Refine search query
- Use advanced search operators
- Try different search engines
- Add domain filters

**Broken Links**
- Check URL validity
- Use web archive (archive.org)
- Find alternative sources
- Update source list

**Conflicting Information**
- Cross-reference multiple sources
- Check publication dates
- Verify source credibility
- Note disagreements in summary

## Next Steps

1. Configure search APIs (Google, Bing, etc.)
2. Set up source quality filters
3. Integrate with note-taking tools
4. Add domain-specific sources
5. Deploy as API or bot
