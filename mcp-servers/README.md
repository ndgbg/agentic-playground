# MCP Servers Collection

Model Context Protocol servers for AI agents. Production-ready tools for AWS operations, parenting, and general use.

## 📦 Collections

### [AWS Examples](aws-examples/)
Production-ready AWS operations servers:
- Resource Inspector
- Cost Optimizer
- Security Auditor
- CloudWatch Insights
- Well-Architected Advisor

### [Parenting Examples](parenting-examples/)
Practical tools for parents with newborns:
- Baby Tracker
- Sleep Schedule Helper
- Quick Parent Helper

### Basic Examples
Simple MCP server examples:
- `example_standalone.py` - No dependencies
- `example_simple.py` - Full MCP implementation

## Quick Start

```bash
# Run basic example
python3 example_standalone.py

# Run AWS examples
cd aws-examples
pip install -r requirements.txt
python3 aws_resource_inspector.py

# Run parenting examples
cd parenting-examples
./run_all_examples.sh
```

## Documentation

- **INDEX.md** - Complete package overview
- **EXAMPLE.md** - Basic MCP server tutorial
- **OVERVIEW.txt** - Visual summary

Each collection has its own README with detailed documentation.

## What is MCP?

Model Context Protocol (MCP) is a standard for AI agents to use tools. Each server provides tools that agents can call to perform tasks.

**Example:**
- Agent: "Show me EC2 instances"
- MCP Server: Calls AWS API, returns results
- Agent: Presents results to user

## Requirements

- Python 3.8+
- No dependencies for basic/parenting examples
- `mcp` and `boto3` for AWS examples

## Contributing

Add new servers following the pattern in `example_standalone.py`. See individual collection READMEs for guidelines.
