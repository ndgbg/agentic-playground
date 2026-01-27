# API Gateway Integration

Production-ready REST API for agent invocation with authentication, rate limiting, and monitoring.

## Overview

Expose your agents as HTTP APIs with enterprise features like API key authentication, per-user rate limiting, request validation, and comprehensive error handling. Perfect for building multi-tenant agent platforms.

## Quick Start

```bash
cd integration-demos/api-gateway
pip install -r requirements.txt
python api_gateway.py
```

**Server starts on:** `http://localhost:8080`

## Making Requests

### Basic Request
```bash
curl -X POST http://localhost:8080/invocations \
  -H "X-API-Key: key_123" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is the weather today?"}'
```

**Response:**
```json
{
  "response": "I can help you check the weather...",
  "request_id": "req_abc123",
  "timestamp": "2026-01-26T16:00:00Z",
  "rate_limit": {
    "remaining": 99,
    "limit": 100,
    "reset": 3600
  }
}
```

### Invalid API Key
```bash
curl -X POST http://localhost:8080/invocations \
  -H "X-API-Key: invalid_key" \
  -d '{"prompt": "Hello"}'
```

**Response:**
```json
{
  "error": "Invalid API key",
  "status": 401
}
```

### Rate Limit Exceeded
```json
{
  "error": "Rate limit exceeded. Try again in 3600 seconds",
  "status": 429,
  "retry_after": 3600
}
```

## Features

### API Key Authentication

Each request requires a valid API key in the `X-API-Key` header:

```python
API_KEYS = {
    "key_123": {"user": "alice", "tier": "premium"},
    "key_456": {"user": "bob", "tier": "free"},
    "key_789": {"user": "charlie", "tier": "enterprise"}
}
```

### Rate Limiting

Per-user rate limits based on tier:
- **Free:** 10 requests/hour
- **Premium:** 100 requests/hour
- **Enterprise:** 1000 requests/hour

```python
RATE_LIMITS = {
    "free": 10,
    "premium": 100,
    "enterprise": 1000
}
```

### Request Validation

Validates all incoming requests:
- Required fields present
- Prompt length limits
- Content type validation
- JSON structure validation

### Error Handling

Comprehensive error responses:
- 400: Bad Request (invalid JSON, missing fields)
- 401: Unauthorized (invalid API key)
- 429: Too Many Requests (rate limit exceeded)
- 500: Internal Server Error (agent failures)

## API Endpoints

### POST /invocations

Invoke the agent with a prompt.

**Request:**
```json
{
  "prompt": "Your question here",
  "context": {
    "user_id": "user_123",
    "session_id": "session_456"
  }
}
```

**Response:**
```json
{
  "response": "Agent response",
  "request_id": "req_abc123",
  "timestamp": "2026-01-26T16:00:00Z",
  "metadata": {
    "model": "claude-3-sonnet",
    "tokens": 150
  }
}
```

### GET /health

Check API health status.

**Response:**
```json
{
  "status": "healthy",
  "uptime": 3600,
  "version": "1.0.0"
}
```

### GET /metrics

Get usage metrics (requires admin key).

**Response:**
```json
{
  "total_requests": 1523,
  "requests_by_user": {
    "alice": 450,
    "bob": 123
  },
  "average_response_time": 1.2
}
```

## Customization

### Add Custom Authentication

```python
import jwt

def verify_jwt_token(token: str) -> dict:
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.InvalidTokenError:
        return None

@app.before_request
def authenticate():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = verify_jwt_token(token)
    if not user:
        return jsonify({"error": "Invalid token"}), 401
    request.user = user
```

### Add Request Logging

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.after_request
def log_request(response):
    logger.info(f"{request.method} {request.path} - {response.status_code}")
    return response
```

### Add Response Caching

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=1000)
def cached_invoke(prompt_hash: str, prompt: str):
    return invoke({"prompt": prompt})

@app.route("/invocations", methods=["POST"])
def invoke_with_cache():
    prompt = request.json["prompt"]
    prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
    response = cached_invoke(prompt_hash, prompt)
    return jsonify(response)
```

## Deployment

### Deploy to AWS Lambda + API Gateway

```bash
# Package
pip install -r requirements.txt -t package/
cp api_gateway.py package/
cd package && zip -r ../function.zip .

# Deploy
aws lambda create-function \
  --function-name agent-api \
  --runtime python3.11 \
  --handler api_gateway.lambda_handler \
  --zip-file fileb://function.zip

# Create API Gateway
aws apigatewayv2 create-api \
  --name agent-api \
  --protocol-type HTTP \
  --target arn:aws:lambda:us-west-2:123456789:function:agent-api
```

### Deploy with Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY api_gateway.py .

EXPOSE 8080
CMD ["python", "api_gateway.py"]
```

```bash
docker build -t agent-api .
docker run -p 8080:8080 agent-api
```

### Deploy to ECS

```bash
# Push to ECR
aws ecr create-repository --repository-name agent-api
docker tag agent-api:latest 123456789.dkr.ecr.us-west-2.amazonaws.com/agent-api
docker push 123456789.dkr.ecr.us-west-2.amazonaws.com/agent-api

# Create ECS service
aws ecs create-service \
  --cluster production \
  --service-name agent-api \
  --task-definition agent-api:1 \
  --desired-count 3 \
  --load-balancer targetGroupArn=arn:aws:elasticloadbalancing:...
```

## Monitoring

### CloudWatch Metrics

```python
import boto3

cloudwatch = boto3.client('cloudwatch')

def publish_metric(metric_name: str, value: float):
    cloudwatch.put_metric_data(
        Namespace='AgentAPI',
        MetricData=[{
            'MetricName': metric_name,
            'Value': value,
            'Unit': 'Count'
        }]
    )

# Track requests
publish_metric('Requests', 1)
publish_metric('ResponseTime', response_time)
```

### Request Tracing

```python
import uuid

@app.before_request
def add_trace_id():
    request.trace_id = str(uuid.uuid4())
    logger.info(f"[{request.trace_id}] {request.method} {request.path}")

@app.after_request
def add_trace_header(response):
    response.headers['X-Trace-ID'] = request.trace_id
    return response
```

## Use Cases

### Multi-Tenant SaaS Platform
Provide agent APIs to multiple customers with isolated rate limits and billing.

### Public Agent API
Expose agents to external developers with API key management.

### Microservices Architecture
Integrate agents into existing microservices with standard REST APIs.

### Mobile/Web Apps
Backend API for mobile and web applications using agents.

## Security Best Practices

### Use HTTPS
```python
# In production, always use HTTPS
if not request.is_secure and not app.debug:
    return redirect(request.url.replace("http://", "https://"))
```

### Rotate API Keys
```python
def rotate_api_key(user: str) -> str:
    new_key = f"key_{uuid.uuid4()}"
    API_KEYS[new_key] = API_KEYS.pop(old_key)
    return new_key
```

### Input Sanitization
```python
def sanitize_prompt(prompt: str) -> str:
    # Remove potential injection attacks
    prompt = prompt.replace("<script>", "")
    prompt = prompt[:1000]  # Limit length
    return prompt
```

## Testing

```python
import requests

# Test valid request
response = requests.post(
    "http://localhost:8080/invocations",
    headers={"X-API-Key": "key_123"},
    json={"prompt": "Hello"}
)
assert response.status_code == 200

# Test invalid key
response = requests.post(
    "http://localhost:8080/invocations",
    headers={"X-API-Key": "invalid"},
    json={"prompt": "Hello"}
)
assert response.status_code == 401

# Test rate limit
for i in range(101):
    response = requests.post(
        "http://localhost:8080/invocations",
        headers={"X-API-Key": "key_456"},  # Free tier
        json={"prompt": "Hello"}
    )
if i >= 10:
    assert response.status_code == 429
```
