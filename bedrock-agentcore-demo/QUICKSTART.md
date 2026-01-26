# AgentCore Demo - Quick Reference

## Setup (One Time)

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Verify installation
agentcore --help
```

## Local Development

```bash
# Start agent locally
python my_agent.py

# Test in another terminal
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello!"}'
```

## Deploy to AWS

```bash
# Configure (first time)
agentcore configure -e my_agent.py

# Deploy
agentcore deploy

# Test deployed agent
agentcore invoke '{"prompt": "Tell me a joke"}'

# Check status
agentcore status

# View logs
# CloudWatch → /aws/bedrock-agentcore/runtimes/{agent-id}-DEFAULT
```

## Invoke Programmatically

```bash
# Edit invoke_agent.py with your agent ARN
python invoke_agent.py
```

## Clean Up

```bash
agentcore destroy
```

## Common Commands

```bash
# List deployed agents
aws bedrock-agentcore-control list-agent-runtimes

# Get agent details
aws bedrock-agentcore-control describe-agent-runtime --agent-runtime-id <id>

# View CloudWatch logs
aws logs tail /aws/bedrock-agentcore/runtimes/<agent-id>-DEFAULT --follow
```

## Troubleshooting

### Check AWS credentials
```bash
aws sts get-caller-identity
```

### Check model access
Go to Bedrock console → Model access → Enable Claude Sonnet 4.0

### Port 8080 in use
```bash
# Mac/Linux
lsof -ti:8080 | xargs kill -9
```

### Memory not ready
```bash
agentcore status  # Wait 2-5 minutes for LTM provisioning
```

## Configuration Options

```bash
# Different region
agentcore configure -e my_agent.py -r us-east-1

# Disable memory
agentcore configure -e my_agent.py --disable-memory

# Custom IAM role
agentcore configure -e my_agent.py --execution-role arn:aws:iam::123456789012:role/MyRole

# Local build mode (requires Docker)
agentcore deploy --local-build
```

## File Structure

```
.bedrock_agentcore.yaml  # Created by agentcore configure
my_agent.py              # Your agent code
invoke_agent.py          # Invocation example
requirements.txt         # Dependencies
```

## Cost Estimate

- Runtime: ~$0.10/hour when active
- Claude Sonnet 4.0: ~$3 per 1M input tokens
- Memory (LTM): ~$0.30/GB-month
- Typical conversation: $0.01-$0.05

## Resources

- [AgentCore Docs](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/)
- [Starter Toolkit](https://aws.github.io/bedrock-agentcore-starter-toolkit/)
- [Strands Agents](https://strandsagents.com/)
