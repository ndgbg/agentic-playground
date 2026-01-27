# EventBridge Integration

Event-driven agent triggers for AWS events.

## Quick Start
```bash
pip install -r requirements.txt
python eventbridge_agent.py
```

## Handles
- S3 file uploads
- CloudWatch alarms
- Custom events
- Scheduled triggers

## Example Events
```json
{
  "detail-type": "Object Created",
  "detail": {"bucket": "my-bucket", "key": "data.csv"}
}
```

## Use Cases
- Automated workflows
- Event processing
- Monitoring responses
- Scheduled tasks

**Status:** ✅ Implemented | **Complexity:** Medium | **Time:** 45 min
