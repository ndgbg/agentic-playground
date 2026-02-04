# Building an Agentic AI Playground: 20 Production-Ready Demos

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![AWS Bedrock](https://img.shields.io/badge/AWS-Bedrock-orange.svg)](https://aws.amazon.com/bedrock/)
[![MCP Servers](https://img.shields.io/badge/MCP-Servers-green.svg)](https://modelcontextprotocol.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## What Does "Agentic AI Product Manager" Mean?

An Agentic AI Product Manager isn't just someone who talks about AI agents—they build them. They understand the technical architecture, can implement working prototypes, and bridge the gap between AI capabilities and real business problems.

Traditional PM skills (user research, roadmaps, stakeholder management) remain essential, but agentic AI adds a new dimension: you need to think in terms of autonomous systems that reason, use tools, and make decisions. You're not just defining features—you're designing agent behaviors, tool ecosystems, and orchestration patterns.

This repo represents that philosophy: theory backed by working code.

## The Inspiration

I built this playground after noticing a gap in how agentic AI is presented online. Most resources fall into two camps:

1. **Academic papers** - Fascinating research, but disconnected from production reality
2. **Marketing content** - Bold claims about what agents "can do," with no code to back it up

What was missing? **Working implementations that you can run, modify, and deploy.**

I wanted to create something that would help me (and others) move from "I understand agents conceptually" to "I've built and deployed agent systems." Each demo solves a real problem with actual code—not pseudocode, not architecture diagrams, but Python you can execute locally or deploy to AWS.

## What's Inside: 20 Production-Ready Demos

The playground is organized into five categories:

### 1. Agent Framework Demos
Learn the major frameworks by building the same multi-agent workflow three different ways:
- **LangGraph** - State-based orchestration with conditional routing
- **CrewAI** - Role-based agents working as a crew
- **AutoGen** - Conversational agents with code generation

These aren't toy examples. Each implements a researcher → writer → reviewer pipeline that actually produces content.

### 2. AgentCore Features
AWS Bedrock AgentCore provides infrastructure for production agents. These demos show how to use it:
- **Gateway Integration** - Connect agents to external tools and APIs
- **Memory Demo** - Maintain conversation context across sessions
- **Code Interpreter** - Let agents write and execute code safely
- **Browser Tool** - Enable agents to interact with web pages

### 3. Enterprise Use Cases
Real business problems solved with agents:
- **Customer Support** - Multi-agent system with routing, FAQ lookup, and escalation
- **DevOps Agent** - Monitor infrastructure, analyze logs, suggest fixes
- **Data Analysis** - Natural language to SQL queries and insights

### 4. Integration Demos
Connect agents to your existing systems:
- **Slack Bot** - Deploy agents where your team already works
- **API Gateway** - Expose agents as REST APIs with auth and rate limiting
- **EventBridge** - Trigger agents from AWS events (S3 uploads, CloudWatch alarms)

### 5. Advanced Patterns
Production-grade patterns for serious deployments:
- **RAG Knowledge Base** - Semantic search with source citations
- **Multi-Modal Agent** - Process images and text together
- **Evaluation Framework** - Test agent quality systematically
- **Policy Controls** - Fine-grained access control with Cedar policies

Plus three practical applications: Meeting Assistant, Code Review Agent, and Research Assistant.

## How This Helps You

### If You're Learning Agentic AI
Start with the framework demos. Run them locally, see how agents make decisions, modify the prompts, add new tools. The code is commented and structured to be readable.

Each README includes:
- Quick start commands
- Expected output
- How it works explanations
- Customization examples

### If You're Building Production Systems
Use these as templates. The patterns are production-ready:
- Error handling
- Logging and monitoring
- Security best practices
- Deployment instructions (Docker, Lambda, ECS)

Copy the code, adapt it to your use case, deploy it.

### If You're a PM Evaluating Agent Platforms
Run the demos to understand what's actually possible vs. marketing hype. See how different frameworks compare. Use the evaluation framework to test agent quality systematically.

## Getting Started

### Prerequisites
```bash
# Install Python 3.8+
python --version

# Install dependencies (each demo has its own requirements.txt)
pip install bedrock-agentcore strands-agents
```

### Run Your First Demo

1. **Clone the repo:**
```bash
git clone https://github.com/ndgbg/agentic-playground.git
cd agentic-playground
```

2. **Pick a demo** (I recommend starting with Gateway Integration):
```bash
cd agentcore-features/gateway-integration
pip install -r requirements.txt
python gateway_agent.py
```

3. **See it work:**
```
Gateway Integration Demo
============================================================

Query: What's the weather in Seattle?
Response: Weather in Seattle: Rainy, 52°F

Query: Search for customer Alice
Response: Found customer: Alice Smith (Premium, 2 orders)
============================================================
```

4. **Modify it:**
Open `gateway_agent.py`, add your own tool:
```python
@tool
def your_custom_tool(param: str) -> str:
    """Your tool description"""
    # Your logic here
    return result
```

The agent will automatically discover and use your tool.

### Deploy to Production

Each demo includes deployment instructions. For example, to deploy to AWS Lambda:

```bash
# Package
pip install -r requirements.txt -t package/
cp gateway_agent.py package/
cd package && zip -r ../function.zip .

# Deploy
aws lambda create-function \
  --function-name my-agent \
  --runtime python3.11 \
  --handler gateway_agent.invoke \
  --zip-file fileb://function.zip
```

## What Makes These Demos Different

### 1. They Actually Work
Every demo has been tested. You can run them locally right now. No "coming soon" or "conceptual example" disclaimers.

### 2. They Use Real Agent Frameworks
These aren't scripts with if/else logic pretending to be agents. They use:
- `strands.Agent` with tool calling
- LangGraph with state management
- CrewAI with role-based collaboration
- AutoGen with conversational agents

The agents reason about user requests and autonomously choose which tools to invoke.

### 3. They're Production-Ready
Each includes:
- Error handling
- Input validation
- Security considerations
- Deployment guides
- Best practices

### 4. They're Educational
Comprehensive READMEs explain:
- What the demo does
- How it works
- How to customize it
- How to deploy it
- Common pitfalls

## Real-World Applications

These patterns power real systems:

**Customer Support:** Companies use multi-agent systems to handle tier-1 support, routing complex issues to humans only when needed.

**DevOps:** Teams deploy agents that monitor infrastructure, analyze logs, and suggest fixes—reducing MTTR from hours to minutes.

**Data Analysis:** Business users query databases in natural language, getting insights without SQL knowledge.

**Code Review:** Development teams use agents to catch security issues and style violations before human review.

## The Philosophy Behind This Repo

I believe the best way to learn is by doing. Reading about agents is useful, but running agent code, breaking it, fixing it, and deploying it—that's how you truly understand them.

This repo embodies that philosophy:
- **Minimal but complete** - Each demo is focused but fully functional
- **Practical over theoretical** - Real problems, real solutions
- **Code over slides** - Working implementations, not architecture diagrams
- **Production-ready** - Patterns you can actually deploy

## What's Next

I'm continuing to add demos as I explore new patterns and use cases. Some ideas in progress:
- Multi-agent debate systems
- Agent-to-agent communication patterns
- Long-running agent workflows
- Human-in-the-loop patterns

But the core principle remains: every addition must be a working implementation you can run and deploy.

## Contributing

Found a bug? Have an idea for a new demo? Contributions welcome! The goal is to build a comprehensive resource for anyone building agentic AI systems.

## Get Started Today

Don't just read about agentic AI—build it:

1. Clone the repo: `git clone https://github.com/ndgbg/agentic-playground.git`
2. Pick a demo that matches your use case
3. Run it locally
4. Modify it for your needs
5. Deploy it to production

The gap between understanding agents conceptually and building them in production is smaller than you think. These 20 demos are your bridge across that gap.

---

**Repository:** [github.com/ndgbg/agentic-playground](https://github.com/ndgbg/agentic-playground)

**More Resources:**
- [Agentic AI Insights](https://github.com/ndgbg/agentic-ai-insights) - Strategic content on use cases and patterns
- [LinkedIn](https://linkedin.com/in/nidabeig) - Connect with me

---

*Built by an Agentic AI Product Manager who believes the best documentation is working code.*
