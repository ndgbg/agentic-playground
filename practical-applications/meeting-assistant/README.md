# Meeting Assistant

Extract action items, participants, and key decisions from meeting transcripts. Automatically generate summaries and track follow-ups.

## Overview

Process meeting transcripts to identify action items, participants, decisions, and deadlines. Perfect for automating meeting notes and ensuring nothing falls through the cracks.

## Quick Start

```bash
cd practical-applications/meeting-assistant
pip install -r requirements.txt
python meeting_assistant.py
```

**Output:**
```
Meeting Assistant
============================================================

Transcript: "Team meeting on Jan 26. Alice will handle the backend API 
by Wednesday. Bob agreed to review the designs by Friday. We decided 
to use PostgreSQL for the database. Charlie raised concerns about 
the timeline."

Analysis:
============================================================

📋 ACTION ITEMS:
1. Alice: Implement backend API
   Deadline: Wednesday, Jan 29
   Priority: High

2. Bob: Review designs
   Deadline: Friday, Jan 31
   Priority: Medium

============================================================

👥 PARTICIPANTS:
- Alice (Backend Developer)
- Bob (Designer)
- Charlie (Project Manager)

============================================================

✅ DECISIONS:
- Use PostgreSQL for database
- Timeline concerns raised by Charlie

============================================================

📝 SUMMARY:
Team discussed backend implementation and design review. Key decision
made to use PostgreSQL. Timeline concerns need to be addressed.

============================================================
```

## Features

### Action Item Extraction
Automatically identify tasks and assignments:
- Who is responsible
- What needs to be done
- When it's due
- Priority level

### Participant Identification
Track who attended and their roles:
- Names mentioned
- Speaking patterns
- Role inference

### Decision Tracking
Capture key decisions made:
- What was decided
- Who made the decision
- Context and reasoning

### Summary Generation
Create concise meeting summaries:
- Key topics discussed
- Main outcomes
- Next steps

## Available Tools

### extract_action_items()
Find all action items:
```python
extract_action_items(transcript)
# Returns: [
#   {"assignee": "Alice", "task": "Implement API", "deadline": "Wednesday"},
#   {"assignee": "Bob", "task": "Review designs", "deadline": "Friday"}
# ]
```

### identify_participants()
List all participants:
```python
identify_participants(transcript)
# Returns: ["Alice", "Bob", "Charlie"]
```

### extract_decisions()
Find decisions made:
```python
extract_decisions(transcript)
# Returns: ["Use PostgreSQL", "Approve budget increase"]
```

### generate_summary()
Create meeting summary:
```python
generate_summary(transcript)
# Returns: "Team discussed... Key decisions: ..."
```

## Example Transcripts

### Project Planning Meeting
```
"Sprint planning for Q1. Sarah will lead the frontend redesign, 
targeting completion by Feb 15. Mike commits to API documentation 
by Feb 10. Team agreed to use React for the new UI. Budget approved 
for additional testing resources."
```

### Sales Call
```
"Call with Acme Corp. They're interested in the Enterprise plan. 
John will send proposal by EOD. Follow-up meeting scheduled for 
next Tuesday. They need integration with Salesforce. Decision: 
Offer 20% discount for annual commitment."
```

### Technical Review
```
"Architecture review meeting. Decided to migrate to microservices. 
Lisa will create migration plan by next week. Tom raised performance 
concerns about the API gateway. Action: Run load tests before 
proceeding."
```

## Customization

### Add Calendar Integration

```python
from google.oauth2 import service_account
from googleapiclient.discovery import build

@tool
def create_calendar_events(action_items: list) -> str:
    """Create calendar events for action items"""
    creds = service_account.Credentials.from_service_account_file('credentials.json')
    service = build('calendar', 'v3', credentials=creds)
    
    for item in action_items:
        event = {
            'summary': item['task'],
            'description': f"Assigned to: {item['assignee']}",
            'start': {'date': item['deadline']},
            'end': {'date': item['deadline']},
            'reminders': {'useDefault': True}
        }
        service.events().insert(calendarId='primary', body=event).execute()
    
    return f"Created {len(action_items)} calendar events"
```

### Add Email Notifications

```python
import smtplib
from email.mime.text import MIMEText

@tool
def send_action_item_emails(action_items: list) -> str:
    """Email action items to assignees"""
    for item in action_items:
        email = get_user_email(item['assignee'])
        
        msg = MIMEText(f"""
        You have a new action item from today's meeting:
        
        Task: {item['task']}
        Deadline: {item['deadline']}
        Priority: {item['priority']}
        """)
        
        msg['Subject'] = f"Action Item: {item['task']}"
        msg['From'] = 'meetings@company.com'
        msg['To'] = email
        
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login('user', 'password')
            server.send_message(msg)
    
    return f"Sent {len(action_items)} emails"
```

### Add Jira Integration

```python
from jira import JIRA

@tool
def create_jira_tickets(action_items: list) -> str:
    """Create Jira tickets for action items"""
    jira = JIRA('https://company.atlassian.net', basic_auth=('user', 'token'))
    
    for item in action_items:
        issue = jira.create_issue(
            project='PROJ',
            summary=item['task'],
            description=f"Assigned to: {item['assignee']}\nDeadline: {item['deadline']}",
            issuetype={'name': 'Task'},
            assignee={'name': item['assignee'].lower()}
        )
        print(f"Created {issue.key}")
    
    return f"Created {len(action_items)} Jira tickets"
```

## Integration Examples

### Zoom Integration

```python
import requests

def process_zoom_recording(meeting_id: str):
    # Get recording
    response = requests.get(
        f"https://api.zoom.us/v2/meetings/{meeting_id}/recordings",
        headers={"Authorization": f"Bearer {ZOOM_TOKEN}"}
    )
    
    # Download transcript
    transcript_url = response.json()['recording_files'][0]['download_url']
    transcript = requests.get(transcript_url).text
    
    # Process
    action_items = extract_action_items(transcript)
    summary = generate_summary(transcript)
    
    return {"action_items": action_items, "summary": summary}
```

### Slack Integration

```python
from slack_sdk import WebClient

slack = WebClient(token=SLACK_TOKEN)

def post_meeting_summary(channel: str, transcript: str):
    action_items = extract_action_items(transcript)
    summary = generate_summary(transcript)
    
    message = f"""
    📋 *Meeting Summary*
    
    {summary}
    
    *Action Items:*
    """
    
    for item in action_items:
        message += f"\n• {item['assignee']}: {item['task']} (Due: {item['deadline']})"
    
    slack.chat_postMessage(channel=channel, text=message)
```

### Microsoft Teams Integration

```python
import requests

def post_to_teams(webhook_url: str, transcript: str):
    action_items = extract_action_items(transcript)
    
    card = {
        "@type": "MessageCard",
        "summary": "Meeting Summary",
        "sections": [{
            "activityTitle": "Action Items",
            "facts": [
                {"name": item['assignee'], "value": item['task']}
                for item in action_items
            ]
        }]
    }
    
    requests.post(webhook_url, json=card)
```

## Deploy to Production

### Lambda Function for Zoom Webhooks

```python
import json

def lambda_handler(event, context):
    # Parse Zoom webhook
    body = json.loads(event['body'])
    
    if body['event'] == 'recording.completed':
        meeting_id = body['payload']['object']['id']
        
        # Process recording
        result = process_zoom_recording(meeting_id)
        
        # Send notifications
        send_action_item_emails(result['action_items'])
        
    return {'statusCode': 200}
```

### API Endpoint

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/process-transcript", methods=["POST"])
def process_transcript():
    transcript = request.json["transcript"]
    
    result = {
        "action_items": extract_action_items(transcript),
        "participants": identify_participants(transcript),
        "decisions": extract_decisions(transcript),
        "summary": generate_summary(transcript)
    }
    
    return jsonify(result)
```

## Use Cases

### Automated Meeting Notes
Replace manual note-taking with automatic extraction.

### Action Item Tracking
Ensure tasks are captured and assigned.

### Compliance Documentation
Maintain records of decisions and discussions.

### Team Productivity
Track commitments and follow-ups across meetings.

## Best Practices

### Clear Transcripts
```
✅ "Alice will implement the API by Wednesday"
❌ "Someone should probably do that thing soon"
```

### Structured Meetings
- Use clear language for assignments
- State deadlines explicitly
- Confirm decisions verbally

### Validation
```python
def validate_action_items(items: list) -> list:
    validated = []
    for item in items:
        if item.get('assignee') and item.get('task'):
            validated.append(item)
    return validated
```

## Troubleshooting

**Missing Action Items**
- Ensure clear assignment language
- Check transcript quality
- Adjust extraction prompts

**Incorrect Participants**
- Verify speaker labels in transcript
- Use consistent name formats
- Add participant list manually if needed

**Wrong Deadlines**
- Use explicit date formats
- Confirm dates in meeting
- Add timezone handling

## Next Steps

1. Connect to your meeting platform (Zoom, Teams, etc.)
2. Set up automatic processing
3. Integrate with task management tools
4. Configure notifications
5. Monitor and refine extraction accuracy
