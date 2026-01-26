# 🤖 Agentic Playground

A collection of AI agent prototypes and AWS integration demos.

## Projects

### 🚀 [streamlit-eks-demo](./streamlit-eks-demo)
Interactive Streamlit application for managing AWS EKS clusters with a custom Strands agent.

**Features:**
- Natural language EKS operations via Strands agent
- AWS EKS cluster management
- .NET application deployment pipeline
- GitHub repository analysis
- Real-time monitoring

**Tech Stack:** Streamlit, boto3, Strands agent, kubectl, eksctl

### 🧠 [bedrock-agentcore-demo](./bedrock-agentcore-demo)
Complete tutorial for building and deploying AI agents using AWS Bedrock AgentCore Runtime.

**Features:**
- AgentCore Runtime deployment
- Strands Agents framework integration
- Memory (STM and LTM) support
- Gateway for tool connections
- Observability with CloudWatch
- Programmatic invocation examples

**Tech Stack:** AWS Bedrock AgentCore, Strands Agents, boto3, Claude

## Getting Started

Each project has its own README with detailed setup instructions. Navigate to the project directory to learn more.

## Requirements

### Common
- Python 3.10+
- AWS CLI configured
- AWS account with appropriate permissions

### Project-Specific
- **streamlit-eks-demo**: Docker, kubectl, eksctl
- **bedrock-agentcore-demo**: Claude Sonnet 4.0 model access in Bedrock

## License

MIT
