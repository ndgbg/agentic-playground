# Advanced MCP Server Examples

Sophisticated, production-grade MCP servers demonstrating complex patterns and real-world use cases.

## 🧠 Knowledge Base with RAG

Personal knowledge management system with semantic search capabilities.

### Features
- **Full-text search** using SQLite FTS5
- **Semantic search** with text chunking and embeddings
- **Document management** with tags and metadata
- **Persistent storage** with SQLite
- **Statistics and analytics**

### Tools
- `add_document` - Add documents with tags and metadata
- `search_documents` - Full-text search across all documents
- `semantic_search` - Find semantically similar content
- `get_document` - Retrieve document by ID
- `list_tags` - List all unique tags
- `get_stats` - Knowledge base statistics

### Use Cases
- Personal note-taking system
- Documentation search
- Research paper management
- Code snippet library
- Meeting notes archive

### Example
```bash
python3 knowledge_base_rag.py
```

**Output:**
```
📚 Personal Knowledge Base with RAG
Documents: 3
Chunks: 3
Tags: ai, aws, best-practices, development, lambda, mcp, programming, python, serverless

Search for 'python':
  • Python Best Practices
    Use type hints for better code clarity...
```

---

## ⚙️ Task Automation Engine

Workflow automation with conditions, variables, and execution tracking.

### Features
- **Workflow creation** with multiple steps
- **Conditional execution** based on variables
- **Variable management** across workflow steps
- **Execution history** tracking
- **Multiple trigger types** (manual, schedule, webhook)
- **Action library** (HTTP, variables, delays, logging)

### Tools
- `create_workflow` - Define automation workflows
- `execute_workflow` - Run workflows with context
- `list_workflows` - List all workflows
- `get_execution_history` - View execution logs

### Workflow Actions
- `http_request` - Make HTTP calls
- `set_variable` - Store values
- `get_variable` - Retrieve values
- `delay` - Wait between steps
- `log` - Log messages
- `condition` - Conditional branching

### Use Cases
- Daily report generation
- Data synchronization
- Notification workflows
- Backup automation
- API integration chains

### Example
```bash
python3 task_automation.py
```

**Output:**
```
⚙️  Task Automation Engine
Created workflow: Daily Report Generator (4 steps)

Executing workflow...
Status: completed
Steps executed: 4
  Step 1: log → Starting daily report generation
  Step 2: set_variable → report_date = 2026-02-02
  Step 3: http_request → GET https://api.example.com/data
  Step 4: log → Report generated successfully
```

---

## 🏗️ Production-Ready Template

Full MCP protocol implementation with logging, monitoring, and Docker support.

### Features
- **Complete MCP protocol** (stdio transport)
- **JSON-RPC 2.0** message handling
- **Tools and Resources** support
- **Comprehensive logging** to file and stderr
- **Error tracking** and statistics
- **Docker deployment** ready
- **Health checks** included

### Architecture
```
ProductionMCPServer
├── Protocol Handler (JSON-RPC)
├── Tool Registry
├── Resource Registry
├── Logging System
├── Statistics Tracking
└── Stdio Transport
```

### Deployment

**Local:**
```bash
python3 mcp_server_template.py
```

**Docker:**
```bash
docker build -t mcp-server .
docker run -i mcp-server
```

**Kubernetes:**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: mcp-server
spec:
  containers:
  - name: server
    image: mcp-server:latest
    stdin: true
    tty: true
```

### Monitoring
- Request count tracking
- Error rate monitoring
- Uptime statistics
- Per-tool metrics
- Log file: `mcp_server.log`

---

## Comparison: Simple vs Advanced

| Feature | Simple Examples | Advanced Examples |
|---------|----------------|-------------------|
| **Protocol** | Simplified | Full MCP stdio |
| **Storage** | In-memory | SQLite persistent |
| **Error Handling** | Basic | Comprehensive |
| **Logging** | Print statements | Structured logging |
| **Deployment** | Script only | Docker + K8s |
| **State** | Lost on restart | Persistent |
| **Complexity** | ~100 lines | ~400+ lines |
| **Production Ready** | No | Yes |

---

## Integration Examples

### With Kiro CLI

```json
{
  "mcpServers": {
    "knowledge-base": {
      "command": "python3",
      "args": ["/path/to/knowledge_base_rag.py"],
      "env": {
        "DB_PATH": "/data/knowledge.db"
      }
    },
    "automation": {
      "command": "python3",
      "args": ["/path/to/task_automation.py"]
    }
  }
}
```

### With Docker Compose

```yaml
version: '3.8'
services:
  knowledge-base:
    build: ./production-ready
    volumes:
      - ./data:/data
    environment:
      - DB_PATH=/data/knowledge.db
  
  automation:
    build: ./production-ready
    volumes:
      - ./workflows:/workflows
```

---

## Extending the Servers

### Add Custom Actions to Automation

```python
def _custom_action(self, params: dict) -> dict:
    # Your custom logic
    return {"result": "success"}

# Register in _execute_step
elif action == "custom_action":
    return self._custom_action(params)
```

### Add Embeddings to Knowledge Base

```python
# Install: pip install sentence-transformers
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def _generate_embedding(self, text: str):
    return model.encode(text).tolist()
```

### Add Authentication

```python
def _check_auth(self, token: str) -> bool:
    # Verify JWT or API key
    return token == os.getenv("API_KEY")
```

---

## Performance Considerations

### Knowledge Base
- **Indexing**: FTS5 provides fast full-text search
- **Chunking**: 500-word chunks balance granularity and performance
- **Scaling**: SQLite handles millions of documents
- **Optimization**: Add indexes on frequently queried fields

### Task Automation
- **Concurrency**: Execute workflows in parallel with asyncio
- **Retries**: Implement exponential backoff for failed steps
- **Timeouts**: Set per-step timeouts to prevent hanging
- **Caching**: Cache frequently accessed variables

---

## Security Best Practices

1. **Input Validation**: Validate all tool parameters
2. **SQL Injection**: Use parameterized queries (already implemented)
3. **File Access**: Restrict file system access
4. **API Keys**: Store in environment variables
5. **Rate Limiting**: Implement per-client rate limits
6. **Audit Logging**: Log all operations with timestamps

---

## Next Steps

1. **Run the examples** to see them in action
2. **Modify for your use case** - add custom tools/actions
3. **Deploy to production** using Docker
4. **Monitor and optimize** based on usage patterns
5. **Contribute** improvements back to the repo

---

## Requirements

```bash
# Basic functionality
pip install sqlite3  # Built-in with Python

# Optional enhancements
pip install sentence-transformers  # For real embeddings
pip install requests  # For HTTP actions
pip install schedule  # For cron-like scheduling
```

---

**These examples demonstrate production-grade patterns suitable for real-world deployment.**
