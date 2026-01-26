# 🤖 Agentic Playground

A comprehensive collection of AI agent demos, frameworks, and AWS integrations.

## 📂 Project Categories

### 🎯 [Agent Framework Demos](./agent-framework-demos/)
Demonstrations of popular AI agent frameworks:
- **LangGraph Multi-Agent**: Collaborative agents with state management
- **CrewAI Task Automation**: Role-based agents in automated workflows
- **AutoGen Conversational**: Multi-agent conversations with code generation

### 🔧 [AgentCore Features](./agentcore-features/)
AWS Bedrock AgentCore platform capabilities:
- **Memory Demo**: Short-term and long-term memory
- **Gateway Integration**: MCP tools and enterprise APIs
- **Code Interpreter**: Safe code execution sandbox
- **Browser Tool**: Web scraping and automation

### 🏢 [Enterprise Use Cases](./enterprise-use-cases/)
Production-ready enterprise agent implementations:
- **Customer Support Agent**: Knowledge base integration and ticketing
- **DevOps Agent**: Infrastructure monitoring and troubleshooting
- **Data Analysis Agent**: Natural language to SQL and insights

### 🔗 [Integration Demos](./integration-demos/)
AWS services and external platform integrations:
- **Slack Bot**: Slash commands and interactive messages
- **API Gateway**: REST API with auth and rate limiting
- **EventBridge**: Event-driven triggers and scheduling

### 🧪 [Advanced Patterns](./advanced-patterns/)
Advanced agent techniques and patterns:
- **Evaluation Framework**: Automated testing and metrics
- **Multi-Modal Agent**: Image + text processing
- **RAG Knowledge Base**: Semantic search and retrieval
- **Policy Controls**: Cedar policies and access control

### 🎯 [Practical Applications](./practical-applications/)
Real-world agent applications:
- **Meeting Assistant**: Transcription and action items
- **Code Review Agent**: PR analysis and security scanning
- **Research Assistant**: Web search and synthesis

### 🚀 [Streamlit EKS Demo](./streamlit-eks-demo/)
Interactive Streamlit app for EKS cluster management with Strands agent.

### 🧠 [Bedrock AgentCore Demo](./bedrock-agentcore-demo/)
Complete tutorial for AgentCore Runtime deployment.

## 🚀 Getting Started

Each category and demo has its own README with detailed instructions. Navigate to the specific directory for setup and usage details.

### Common Requirements

- Python 3.10+
- AWS CLI configured
- AWS account with appropriate permissions
- Bedrock model access (Claude Sonnet 4.0)

### Quick Start

```bash
# Clone the repo
git clone https://github.com/ndgbg/agentic-playground.git
cd agentic-playground

# Navigate to a demo
cd agent-framework-demos/langgraph-multi-agent

# Install dependencies
pip install -r requirements.txt

# Run the demo
python multi_agent.py
```

## 📚 Documentation

Each demo includes:
- README with overview and setup
- Implementation code
- Requirements file
- Usage examples

## 🎓 Learning Path

**Beginners:**
1. Start with [Bedrock AgentCore Demo](./bedrock-agentcore-demo/)
2. Try [LangGraph Multi-Agent](./agent-framework-demos/langgraph-multi-agent/)
3. Explore [Memory Demo](./agentcore-features/memory-demo/)

**Intermediate:**
1. [CrewAI Task Automation](./agent-framework-demos/crewai-task-automation/)
2. [Customer Support Agent](./enterprise-use-cases/customer-support/)
3. [API Gateway Integration](./integration-demos/api-gateway/)

**Advanced:**
1. [Multi-Modal Agent](./advanced-patterns/multimodal-agent/)
2. [RAG Knowledge Base](./advanced-patterns/rag-knowledge-base/)
3. [Policy Controls](./advanced-patterns/policy-controls/)

## 🛠️ Tech Stack

- **Frameworks**: LangGraph, CrewAI, AutoGen, Strands Agents
- **AWS Services**: Bedrock, AgentCore, EKS, Lambda, API Gateway, EventBridge
- **Languages**: Python 3.10+
- **Tools**: boto3, Streamlit, kubectl, eksctl

## 💰 Cost Considerations

Most demos use AWS services that incur costs:
- Bedrock model invocations: ~$3 per 1M input tokens
- AgentCore Runtime: ~$0.10/hour when active
- EKS clusters: ~$0.10/hour + node costs

Always clean up resources after testing.

## 📖 Resources

- [AWS Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/)
- [AgentCore Documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/)
- [Strands Agents](https://strandsagents.com/)
- [LangGraph](https://langchain-ai.github.io/langgraph/)
- [CrewAI](https://www.crewai.com/)

## 🤝 Contributing

This is a learning playground. Feel free to:
- Add new demos
- Improve existing implementations
- Share feedback and suggestions

## 📝 License

MIT

---

**Note**: Some demos are fully implemented while others are placeholders for future development. Check individual README files for status.
