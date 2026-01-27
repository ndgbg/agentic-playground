# API Gateway Integration

REST API for agent invocation with authentication and rate limiting.

## Quick Start
```bash
pip install -r requirements.txt
python api_gateway.py
```

## Features
- API key authentication
- Rate limiting per user
- Request validation
- Error handling

## Example
```bash
curl -X POST http://localhost:8080/invocations \
  -H "X-API-Key: key_123" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello"}'
```

## Use Cases
- Public API for agents
- Multi-tenant systems
- Usage tracking
- Access control

**Status:** ✅ Implemented | **Complexity:** Low-Medium | **Time:** 30 min
