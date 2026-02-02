# AWS MCP Servers

Model Context Protocol (MCP) servers that extend AI agents with AWS-specific capabilities. These servers provide tools and resources for interacting with AWS services, analyzing infrastructure, and automating cloud operations.

## Available Servers

### 1. AWS Resource Inspector
**Purpose:** Query and analyze AWS resources across your accounts
**Tools:**
- List EC2 instances with filtering
- Get S3 bucket details and policies
- Query RDS databases
- List Lambda functions
- Get CloudWatch metrics

**Use Cases:**
- Infrastructure audits
- Cost analysis
- Security reviews
- Resource inventory

### 2. AWS Cost Optimizer
**Purpose:** Analyze AWS costs and provide optimization recommendations
**Tools:**
- Get cost breakdown by service
- Identify unused resources
- Recommend rightsizing opportunities
- Analyze Reserved Instance coverage
- Forecast future costs

**Use Cases:**
- Monthly cost reviews
- Budget optimization
- FinOps automation
- Cost anomaly detection

### 3. AWS Security Auditor
**Purpose:** Security posture assessment and compliance checking
**Tools:**
- Check S3 bucket public access
- Audit IAM policies
- Review security groups
- Check encryption status
- Scan for compliance violations

**Use Cases:**
- Security audits
- Compliance reporting
- Vulnerability scanning
- Best practice validation

### 4. AWS CloudWatch Insights
**Purpose:** Query and analyze CloudWatch logs and metrics
**Tools:**
- Run CloudWatch Insights queries
- Get metric statistics
- Analyze log patterns
- Create custom dashboards
- Set up alarms

**Use Cases:**
- Troubleshooting
- Performance analysis
- Log aggregation
- Monitoring automation

### 5. AWS Well-Architected Advisor
**Purpose:** Assess workloads against AWS Well-Architected Framework
**Tools:**
- Assess Operational Excellence pillar
- Assess Security pillar
- Assess Reliability pillar
- Assess Performance Efficiency pillar
- Assess Cost Optimization pillar
- Generate comprehensive reports

**Use Cases:**
- Architecture reviews
- Best practice validation
- Workload optimization
- Compliance assessment

## Installation

### Prerequisites
```bash
pip install mcp boto3
```

### Configure AWS Credentials
```bash
aws configure
# Or set environment variables:
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-east-1
```

### Run a Server
```bash
# Start the resource inspector
python aws_resource_inspector.py

# Start the cost optimizer
python aws_cost_optimizer.py

# Start the security auditor
python aws_security_auditor.py

# Start CloudWatch insights
python aws_cloudwatch_insights.py

# Start Well-Architected advisor
python aws_well_architected_advisor.py
```

## Using with Kiro CLI

Add to your Kiro CLI configuration:

```json
{
  "mcpServers": {
    "aws-resources": {
      "command": "python",
      "args": ["/path/to/aws_resource_inspector.py"]
    },
    "aws-costs": {
      "command": "python",
      "args": ["/path/to/aws_cost_optimizer.py"]
    },
    "aws-security": {
      "command": "python",
      "args": ["/path/to/aws_security_auditor.py"]
    },
    "aws-cloudwatch": {
      "command": "python",
      "args": ["/path/to/aws_cloudwatch_insights.py"]
    },
    "aws-well-architected": {
      "command": "python",
      "args": ["/path/to/aws_well_architected_advisor.py"]
    }
  }
}
```

## Example Queries

### Resource Inspector
```
"Show me all EC2 instances in us-east-1"
"List S3 buckets with public access"
"What Lambda functions are using Python 3.8?"
```

### Cost Optimizer
```
"What are my top 5 most expensive services this month?"
"Find unused EBS volumes"
"Show me EC2 instances that could be rightsized"
```

### Security Auditor
```
"Check all S3 buckets for public access"
"Find IAM users with admin access"
"Show security groups with port 22 open to 0.0.0.0/0"
```

### CloudWatch Insights
```
"Show me error logs from the last hour"
"What's the average response time for my API?"
"Find all 5xx errors in production"
```

### Well-Architected Advisor
```
"Assess my security posture"
"Generate a Well-Architected report for my workload"
"What are my reliability issues?"
```

## Architecture

Each MCP server follows this pattern:

```python
from mcp.server import Server
import boto3

server = Server("server-name")

@server.list_tools()
async def list_tools():
    return [
        {
            "name": "tool_name",
            "description": "What it does",
            "inputSchema": {...}
        }
    ]

@server.call_tool()
async def call_tool(name, arguments):
    # AWS API calls using boto3
    client = boto3.client('service')
    result = client.operation(**arguments)
    return result
```

## Security Best Practices

1. **Use IAM roles** instead of access keys when possible
2. **Principle of least privilege** - Grant only required permissions
3. **Enable CloudTrail** to audit MCP server actions
4. **Use AWS Organizations** to limit scope
5. **Rotate credentials** regularly

## Required IAM Permissions

### Resource Inspector
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "ec2:Describe*",
      "s3:List*",
      "s3:GetBucketPolicy",
      "rds:Describe*",
      "lambda:List*",
      "cloudwatch:GetMetricStatistics"
    ],
    "Resource": "*"
  }]
}
```

### Cost Optimizer
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "ce:GetCostAndUsage",
      "ce:GetCostForecast",
      "ec2:Describe*",
      "rds:Describe*",
      "elasticache:Describe*"
    ],
    "Resource": "*"
  }]
}
```

### Security Auditor
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "s3:GetBucketPublicAccessBlock",
      "iam:List*",
      "iam:Get*",
      "ec2:DescribeSecurityGroups",
      "kms:DescribeKey"
    ],
    "Resource": "*"
  }]
}
```

### CloudWatch Insights
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "logs:StartQuery",
      "logs:GetQueryResults",
      "cloudwatch:GetMetricStatistics",
      "cloudwatch:ListMetrics"
    ],
    "Resource": "*"
  }]
}
```

## Extending the Servers

Add new tools by implementing the tool pattern:

```python
@server.call_tool()
async def call_tool(name, arguments):
    if name == "your_new_tool":
        client = boto3.client('service')
        result = client.your_operation(**arguments)
        return {"result": result}
```

## Troubleshooting

**Connection Issues:**
- Check AWS credentials are configured
- Verify IAM permissions
- Ensure region is set correctly

**Performance:**
- Use pagination for large result sets
- Cache frequently accessed data
- Implement rate limiting

**Errors:**
- Enable debug logging: `export MCP_DEBUG=1`
- Check CloudTrail for API errors
- Verify boto3 version compatibility

## Contributing

Add new tools or servers following these guidelines:
1. Use async/await for all operations
2. Include comprehensive error handling
3. Document required IAM permissions
4. Add usage examples
5. Test with multiple AWS accounts

## Resources

- [MCP Specification](https://modelcontextprotocol.io)
- [Boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [AWS CLI Reference](https://docs.aws.amazon.com/cli/)
