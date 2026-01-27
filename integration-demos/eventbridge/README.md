# EventBridge Integration

Event-driven agent automation triggered by AWS events. Build reactive systems that respond to S3 uploads, CloudWatch alarms, custom events, and scheduled triggers.

## Overview

Connect agents to AWS EventBridge to create event-driven workflows. Automatically process files when uploaded to S3, respond to CloudWatch alarms, handle custom application events, or run on schedules.

## Quick Start

```bash
cd integration-demos/eventbridge
pip install -r requirements.txt
python eventbridge_agent.py
```

## Event Types Handled

### S3 Object Created

Triggered when files are uploaded to S3:

```json
{
  "source": "aws.s3",
  "detail-type": "Object Created",
  "detail": {
    "bucket": "my-data-bucket",
    "key": "uploads/data.csv",
    "size": 1024000
  }
}
```

**Agent Response:**
```
Processing S3 file: s3://my-data-bucket/uploads/data.csv
File size: 1.02 MB
Action: Download, analyze, and store results
```

### CloudWatch Alarm

Triggered when CloudWatch alarms change state:

```json
{
  "source": "aws.cloudwatch",
  "detail-type": "CloudWatch Alarm State Change",
  "detail": {
    "alarmName": "HighCPUUsage",
    "state": {
      "value": "ALARM"
    },
    "metric": "CPUUtilization",
    "threshold": 80
  }
}
```

**Agent Response:**
```
⚠️ ALARM: HighCPUUsage
Metric: CPUUtilization exceeded 80%
Action: Scaling up instances, notifying team
```

### Custom Application Events

Handle your own application events:

```json
{
  "source": "myapp.orders",
  "detail-type": "Order Placed",
  "detail": {
    "orderId": "order_123",
    "customerId": "cust_456",
    "amount": 99.99,
    "items": 3
  }
}
```

**Agent Response:**
```
New order received: order_123
Customer: cust_456
Amount: $99.99
Action: Send confirmation email, update inventory
```

### Scheduled Events

Run agents on a schedule:

```json
{
  "source": "aws.events",
  "detail-type": "Scheduled Event",
  "detail": {
    "schedule": "rate(1 hour)",
    "task": "generate_report"
  }
}
```

**Agent Response:**
```
Running scheduled task: generate_report
Generating hourly sales report...
Report saved to s3://reports/hourly/2026-01-26-16.pdf
```

## How It Works

### Event Processing Flow

1. **Event Received** → EventBridge sends event to Lambda/agent
2. **Event Parsed** → Extract source, type, and details
3. **Agent Invoked** → Process event with appropriate tools
4. **Action Taken** → Execute business logic
5. **Response Logged** → Store results in CloudWatch

### Event Router

```python
def route_event(event: dict) -> str:
    """Route events to appropriate handlers"""
    source = event.get("source")
    detail_type = event.get("detail-type")
    
    if source == "aws.s3" and detail_type == "Object Created":
        return handle_s3_event(event)
    elif source == "aws.cloudwatch":
        return handle_alarm(event)
    elif source == "myapp.orders":
        return handle_order(event)
    else:
        return handle_generic_event(event)
```

## Setup EventBridge Rules

### Create Rule for S3 Events

```bash
# Create EventBridge rule
aws events put-rule \
  --name s3-upload-processor \
  --event-pattern '{
    "source": ["aws.s3"],
    "detail-type": ["Object Created"],
    "detail": {
      "bucket": ["my-data-bucket"]
    }
  }'

# Add agent as target
aws events put-targets \
  --rule s3-upload-processor \
  --targets "Id"="1","Arn"="arn:aws:lambda:us-west-2:123:function:eventbridge-agent"
```

### Create Rule for CloudWatch Alarms

```bash
aws events put-rule \
  --name alarm-responder \
  --event-pattern '{
    "source": ["aws.cloudwatch"],
    "detail-type": ["CloudWatch Alarm State Change"],
    "detail": {
      "state": {
        "value": ["ALARM"]
      }
    }
  }'
```

### Create Scheduled Rule

```bash
# Run every hour
aws events put-rule \
  --name hourly-report \
  --schedule-expression "rate(1 hour)"

# Run daily at 9 AM
aws events put-rule \
  --name daily-summary \
  --schedule-expression "cron(0 9 * * ? *)"
```

### Create Custom Event Rule

```bash
aws events put-rule \
  --name order-processor \
  --event-pattern '{
    "source": ["myapp.orders"],
    "detail-type": ["Order Placed"]
  }'
```

## Deployment

### Deploy as Lambda Function

```python
# lambda_handler.py
from eventbridge_agent import process_event

def lambda_handler(event, context):
    """AWS Lambda handler"""
    response = process_event(event)
    return {
        'statusCode': 200,
        'body': response
    }
```

```bash
# Package and deploy
zip function.zip eventbridge_agent.py lambda_handler.py
aws lambda create-function \
  --function-name eventbridge-agent \
  --runtime python3.11 \
  --handler lambda_handler.lambda_handler \
  --zip-file fileb://function.zip \
  --role arn:aws:iam::123:role/lambda-execution
```

### Grant EventBridge Permissions

```bash
aws lambda add-permission \
  --function-name eventbridge-agent \
  --statement-id eventbridge-invoke \
  --action lambda:InvokeFunction \
  --principal events.amazonaws.com \
  --source-arn arn:aws:events:us-west-2:123:rule/s3-upload-processor
```

## Use Cases

### Automated Data Processing

Process files automatically when uploaded:
```
S3 Upload → EventBridge → Agent → Process → Store Results
```

**Example:** CSV uploaded → Parse → Validate → Load to database

### Incident Response

Respond to infrastructure issues:
```
CloudWatch Alarm → EventBridge → Agent → Diagnose → Take Action
```

**Example:** High CPU → Scale instances → Notify team → Log incident

### Order Processing

Handle e-commerce events:
```
Order Placed → EventBridge → Agent → Validate → Fulfill → Notify
```

**Example:** New order → Check inventory → Send confirmation → Update CRM

### Scheduled Maintenance

Run periodic tasks:
```
Schedule → EventBridge → Agent → Execute Task → Report
```

**Example:** Daily backup → Verify → Cleanup old files → Send report

## Customization

### Add S3 Processing

```python
import boto3

s3 = boto3.client('s3')

@tool
def process_s3_file(bucket: str, key: str) -> str:
    """Download and process S3 file"""
    # Download
    s3.download_file(bucket, key, '/tmp/file')
    
    # Process
    with open('/tmp/file', 'r') as f:
        data = f.read()
        # Your processing logic
    
    # Upload results
    s3.upload_file('/tmp/results', bucket, f'processed/{key}')
    return f"Processed {key}"
```

### Add SNS Notifications

```python
sns = boto3.client('sns')

@tool
def send_notification(message: str, topic_arn: str) -> str:
    """Send SNS notification"""
    sns.publish(
        TopicArn=topic_arn,
        Subject='Agent Alert',
        Message=message
    )
    return "Notification sent"
```

### Add DynamoDB Logging

```python
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('event-logs')

@tool
def log_event(event_id: str, details: dict) -> str:
    """Log event to DynamoDB"""
    table.put_item(Item={
        'event_id': event_id,
        'timestamp': datetime.now().isoformat(),
        'details': details
    })
    return "Event logged"
```

## Testing Locally

### Send Test Events

```python
import json

# Test S3 event
s3_event = {
    "source": "aws.s3",
    "detail-type": "Object Created",
    "detail": {
        "bucket": "test-bucket",
        "key": "test.csv"
    }
}

response = process_event(s3_event)
print(response)
```

### Use AWS CLI

```bash
# Send test event
aws events put-events \
  --entries '[{
    "Source": "myapp.orders",
    "DetailType": "Order Placed",
    "Detail": "{\"orderId\": \"test_123\"}"
  }]'
```

## Monitoring

### CloudWatch Logs

```python
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def process_event(event):
    logger.info(f"Processing event: {event['detail-type']}")
    # Process...
    logger.info("Event processed successfully")
```

### CloudWatch Metrics

```python
cloudwatch = boto3.client('cloudwatch')

def publish_metric(metric_name: str, value: float):
    cloudwatch.put_metric_data(
        Namespace='EventBridgeAgent',
        MetricData=[{
            'MetricName': metric_name,
            'Value': value,
            'Unit': 'Count'
        }]
    )

# Track events processed
publish_metric('EventsProcessed', 1)
```

### X-Ray Tracing

```python
from aws_xray_sdk.core import xray_recorder

@xray_recorder.capture('process_event')
def process_event(event):
    # Your code here
    pass
```

## Best Practices

### Idempotency

Ensure events can be processed multiple times safely:

```python
processed_events = set()

def process_event(event):
    event_id = event['id']
    if event_id in processed_events:
        return "Already processed"
    
    # Process event
    processed_events.add(event_id)
```

### Error Handling

```python
def process_event(event):
    try:
        # Process event
        return "Success"
    except Exception as e:
        logger.error(f"Error processing event: {e}")
        # Send to DLQ
        send_to_dlq(event)
        raise
```

### Retry Logic

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def process_with_retry(event):
    # Your processing logic
    pass
```

## Architecture Patterns

### Fan-Out Pattern

One event triggers multiple agents:
```
S3 Upload → EventBridge → [Agent 1: Validate]
                        → [Agent 2: Transform]
                        → [Agent 3: Notify]
```

### Chain Pattern

Events trigger sequential processing:
```
Event 1 → Agent 1 → Event 2 → Agent 2 → Event 3 → Agent 3
```

### Filter Pattern

Route events based on content:
```
All Events → EventBridge Filter → [High Priority → Agent 1]
                                → [Low Priority → Agent 2]
```
