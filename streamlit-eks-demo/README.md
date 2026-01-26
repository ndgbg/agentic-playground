# 🚀 EKS Deployment Demo with Strands Agent

Interactive Streamlit application for managing AWS EKS clusters using natural language and deploying .NET applications.

## 📁 Project Structure

```
streamlit-eks-demo/
├── eks_demo.py              # Main Streamlit application
├── strands_eks_agent.py     # Strands agent for natural language EKS operations
├── requirements.txt         # Python dependencies
├── setup_prerequisites.sh   # Install AWS tools (kubectl, eksctl)
├── run.sh                  # Quick start script
└── README.md               # This file
```

## 🎯 What This Demo Does

This Streamlit application demonstrates agentic AI for AWS EKS management:

**Core Features:**
- **Strands Agent Integration**: Built-in AI agent that understands natural language commands for EKS operations
  - "List all clusters" → Fetches and displays clusters via boto3
  - "Check cluster health" → Analyzes cluster status and metrics
  - "Create cluster plan" → Generates deployment plans with cost estimates
- **Direct AWS Integration**: Uses boto3 to interact with EKS, ECR, and EC2 services
- **.NET Deployment Pipeline**: Analyzes GitHub repos, builds Docker images, deploys to Kubernetes
- **MCP Config Generator**: Creates configuration files for Kiro IDE integration (doesn't run MCP server itself)
- **Live Monitoring**: Real-time pod status, logs, and cluster health via Kubernetes API

**What This Is:**
- ✅ Working demo of Strands agent for EKS operations
- ✅ Complete .NET to EKS deployment workflow
- ✅ Tool to generate MCP server configs for Kiro IDE

**What This Is NOT:**
- ❌ Does not run an MCP server (generates configs only)
- ❌ Not a production deployment tool

## 🚀 Quick Start

### 1. Setup Prerequisites (One Time)
```bash
cd streamlit-eks-demo
./setup_prerequisites.sh  # Installs kubectl, eksctl, Docker
aws configure             # Configure your AWS credentials
```

### 2. Run the Demo
```bash
./run.sh
```

### 3. Open Browser
Navigate to `http://localhost:8501`

## 📱 Demo Features

### 🏠 **Main Demo Page**
- AWS connection status
- GitHub repository analysis
- EKS cluster creation
- Application deployment
- Real-time monitoring

### 🤖 **Strands Agent**
Natural language interface for EKS operations using a custom AI agent implementation:
- Execute tasks like "List all clusters" or "Check cluster health"
- Quick action buttons for common operations
- Context-aware cluster management
- Agent parses requests and routes to AWS APIs
- Returns structured responses with next steps

### 🔧 **MCP Configuration Generator**
Generate MCP server configurations for external use:
- Creates `mcp.json` files for Kiro IDE
- Configures EKS MCP server settings
- Download and use in `.kiro/settings/mcp.json`
- Note: This generates configs, doesn't run the MCP server

### 📚 **Example Commands**
- Natural language EKS commands
- Copy-paste ready for Kiro
- Organized by category

### 🔍 **Live Cluster Monitor**
- Real-time pod status
- kubectl commands
- Namespace management

## 🎯 Demo Flow

This is what happens when you use the demo from start to finish:

### 1. **Connect to AWS**
The application uses your AWS credentials (from `aws configure`) to establish a session with boto3. It verifies access by calling `sts.get_caller_identity()` and displays your account ID and active region.

```
✅ AWS Connected
Account: 1234...5678
Region: us-west-2
```

### 2. **Use Strands Agent (Optional)**
Interact with your EKS infrastructure using natural language:
- Type: "List all EKS clusters" - Agent fetches and displays all clusters
- Type: "Check cluster health" - Agent analyzes cluster status and health metrics
- Type: "Create cluster plan" - Agent generates a deployment plan with cost estimates
- Use quick action buttons for common tasks

The Strands agent parses your request, routes it to the appropriate AWS API calls, and returns structured responses with actionable next steps.

### 3. **Analyze GitHub Project**
When you provide a GitHub URL, the demo:
- Fetches the repository metadata using GitHub API
- Scans for `.csproj` files to detect .NET projects
- Checks for existing `Dockerfile` and Kubernetes manifests
- Identifies the .NET version and project type (Web API, MVC, etc.)

```
GitHub URL: https://github.com/your-username/dotnet-api
✅ Repository found - .NET 8 Web API
❌ No Dockerfile found
```

### 4. **Deploy to EKS**
The deployment process executes these steps:
- **Cluster Creation**: Runs `eksctl create cluster` with managed node groups, configures VPC and subnets
- **Namespace Setup**: Creates a Kubernetes namespace to isolate your application
- **Image Build**: If no Dockerfile exists, generates one based on detected .NET version, builds and pushes to ECR
- **Deployment**: Applies Kubernetes deployment and service manifests, creates LoadBalancer for external access
- **Health Check**: Waits for pods to reach "Running" state and LoadBalancer to provision

```
🏗️ Creating EKS cluster... ✅
📦 Creating namespace... ✅
🚀 Deploying application... ✅
🌐 LoadBalancer ready... ✅

Result: http://a1b2c3-123456789.us-west-2.elb.amazonaws.com
```

## 🔧 Prerequisites

### Required Tools
- **Python 3.8+**
- **AWS CLI** (configured with credentials)
- **kubectl** (installed by setup script)
- **eksctl** (installed by setup script)
- **Docker** (for building images)

### AWS Setup
```bash
# Install AWS CLI
pip install awscli

# Configure credentials
aws configure
# Enter: Access Key, Secret Key, Region (us-west-2), Format (json)

# Verify connection
aws sts get-caller-identity
```

## 💰 Cost Awareness

**Real AWS resources = real costs:**
- EKS Cluster: ~$0.10/hour ($72/month)
- EC2 Nodes: ~$0.04/hour per t3.medium node
- LoadBalancer: ~$0.025/hour
- **Total**: ~$5-10/day for testing

**Always clean up when done:**
```bash
eksctl delete cluster --name dotnet-demo-cluster --region us-west-2
```

## 🎓 What You'll Learn

1. **Agentic AI Patterns** - Building AI agents that understand natural language and route to APIs
2. **EKS Operations** - Hands-on cluster management with boto3
3. **Kubernetes Deployment** - Pod and service creation  
4. **AWS Integration** - ECR, LoadBalancers, VPC setup
5. **MCP Protocol** - Generating Model Context Protocol configurations
6. **Live Monitoring** - Cluster health checks and real-time status

## 🔗 Integration with Your Projects

### Use Your Own .NET Repository
```
GitHub URL: https://github.com/your-username/your-dotnet-project
```

The demo will:
- ✅ Analyze your repository structure
- ✅ Detect .NET framework and dependencies
- ✅ Deploy to your EKS cluster
- ✅ Provide working endpoints

### Integration with Kiro IDE
1. **Generate MCP config** in the "🔧 MCP Configuration" page
2. **Download `mcp.json`** file
3. **Place in `.kiro/settings/mcp.json`**
4. **Restart Kiro** to load the MCP server
5. **Use natural language** commands in Kiro (via the actual EKS MCP server, not this demo)

Note: This demo generates the config file. Kiro will connect to the actual AWS EKS MCP server.

## 🚨 Important Notes

- **This creates real AWS resources** that incur costs
- **Always clean up** clusters when done testing
- **Monitor your AWS billing** during experimentation
- **Use appropriate IAM permissions** for security

## 🎉 Success Indicators

When working correctly, you'll see:
- ✅ Cluster names in AWS Console
- ✅ Pods running in Kubernetes
- ✅ Working LoadBalancer endpoints
- ✅ Application responses
- ✅ kubectl commands that work

## 🔄 Next Steps

After running the demo:
1. **Use Strands agent** for natural language cluster management
2. **Deploy your own .NET applications**
3. **Set up CI/CD pipelines** 
4. **Configure monitoring and logging**
5. **Integrate with EKS MCP server in Kiro**
6. **Scale to production workloads**

## 🤖 Strands Agent Capabilities

The integrated Strands agent is a custom implementation that demonstrates agentic AI patterns:

**How It Works:**
1. User enters natural language command
2. Agent parses and identifies intent
3. Routes to appropriate AWS API handler (boto3)
4. Executes operation and formats response
5. Returns structured data with actionable next steps

**Supported Operations:**
- **List Clusters**: `"List all EKS clusters"` → Calls `eks_client.list_clusters()`
- **Describe Cluster**: `"Describe cluster my-cluster"` → Calls `eks_client.describe_cluster()`
- **Check Health**: `"Check cluster health"` → Analyzes cluster status and endpoint
- **Create Plan**: `"Create cluster plan"` → Generates deployment plan with cost estimates
- **Get Status**: `"Get cluster status"` → Returns current cluster state

**Example Interactions:**
```
You: "List all EKS clusters"
Agent: ✅ Found 3 cluster(s) in us-west-2
       [my-cluster, dev-cluster, prod-cluster]

You: "Check cluster health for my-cluster"  
Agent: ✅ Cluster is healthy
       Status: ACTIVE, Version: 1.28, Endpoint accessible

You: "Create a cluster plan with 3 nodes"
Agent: ✅ Cluster creation plan generated
       Estimated time: 15-20 minutes
       Estimated cost: ~$0.22/hour
```

This is a working example of how to build AI agents that bridge natural language and cloud APIs.

This demo bridges the gap between learning and doing - you're working with AWS infrastructure, not simulations!