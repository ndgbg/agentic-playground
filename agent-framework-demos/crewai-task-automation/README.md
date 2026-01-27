# CrewAI Task Automation

Role-based agents working together as a crew. Define specialized roles, assign tasks, and let agents collaborate to achieve complex goals.

## Overview

CrewAI enables building teams of AI agents with specific roles and expertise. Agents work sequentially or in parallel, delegating tasks and sharing context to complete complex workflows.

## Quick Start

```bash
cd agent-framework-demos/crewai-task-automation
pip install -r requirements.txt
python content_crew.py
```

**Output:**
```
CrewAI Content Creation Crew
============================================================

Task: Create a blog post about quantum computing

[Research Specialist] Starting research...
Researching quantum computing...
Found 5 key topics:
- Quantum bits (qubits)
- Superposition and entanglement
- Quantum algorithms
- Current applications
- Future potential

[Content Writer] Creating article...
Writing 800-word article...
Draft complete with 4 sections and introduction.

[Editor] Reviewing content...
Checking grammar, style, and flow...
Made 12 improvements:
- Fixed 3 grammar issues
- Improved 5 transitions
- Enhanced 4 explanations

============================================================
Final Article:

# Understanding Quantum Computing: A Beginner's Guide

Quantum computing represents a paradigm shift in how we process 
information...

[Full 800-word article]

============================================================
Crew Performance:
- Research: 3 minutes
- Writing: 5 minutes
- Editing: 2 minutes
Total: 10 minutes
============================================================
```

## Architecture

### Crew Structure

```python
from crewai import Agent, Task, Crew

# Define agents
researcher = Agent(
    role="Research Specialist",
    goal="Find accurate, relevant information",
    backstory="Expert researcher with deep knowledge...",
    tools=[search_tool, scrape_tool]
)

writer = Agent(
    role="Content Writer",
    goal="Create engaging, informative content",
    backstory="Professional writer with 10 years experience...",
    tools=[writing_tool]
)

editor = Agent(
    role="Editor",
    goal="Polish content to publication quality",
    backstory="Meticulous editor focused on clarity...",
    tools=[grammar_tool, style_tool]
)

# Define tasks
research_task = Task(
    description="Research {topic} and gather key points",
    agent=researcher,
    expected_output="List of 5-10 key points with sources"
)

writing_task = Task(
    description="Write 800-word article about {topic}",
    agent=writer,
    expected_output="Complete article with introduction and conclusion",
    context=[research_task]  # Uses research output
)

editing_task = Task(
    description="Edit and polish the article",
    agent=editor,
    expected_output="Publication-ready article",
    context=[writing_task]
)

# Create crew
crew = Crew(
    agents=[researcher, writer, editor],
    tasks=[research_task, writing_task, editing_task],
    verbose=True
)

# Execute
result = crew.kickoff(inputs={"topic": "quantum computing"})
```

## Features

### Role-Based Agents

Each agent has a specific role and expertise:

```python
agent = Agent(
    role="Data Analyst",
    goal="Extract insights from data",
    backstory="""You are an experienced data analyst with expertise in 
    statistical analysis and data visualization. You excel at finding 
    patterns and communicating insights clearly.""",
    tools=[pandas_tool, visualization_tool],
    verbose=True,
    allow_delegation=True
)
```

### Task Dependencies

Tasks can depend on previous task outputs:

```python
task1 = Task(
    description="Gather data",
    agent=data_collector
)

task2 = Task(
    description="Analyze data from previous task",
    agent=analyst,
    context=[task1]  # Uses task1 output
)

task3 = Task(
    description="Create report from analysis",
    agent=reporter,
    context=[task1, task2]  # Uses both outputs
)
```

### Agent Delegation

Agents can delegate subtasks to other agents:

```python
manager = Agent(
    role="Project Manager",
    goal="Coordinate team and deliver project",
    allow_delegation=True,  # Can delegate to other agents
    tools=[planning_tool]
)

developer = Agent(
    role="Developer",
    goal="Implement features",
    allow_delegation=False,
    tools=[coding_tool]
)

# Manager can delegate coding tasks to developer
```

### Sequential vs Parallel Execution

```python
# Sequential (default)
crew = Crew(
    agents=[agent1, agent2, agent3],
    tasks=[task1, task2, task3],
    process=Process.sequential
)

# Parallel (tasks run concurrently when possible)
crew = Crew(
    agents=[agent1, agent2, agent3],
    tasks=[task1, task2, task3],
    process=Process.parallel
)
```

## Example Crews

### Content Creation Crew

```python
# Research → Write → Edit → SEO Optimize
researcher = Agent(role="Researcher", ...)
writer = Agent(role="Writer", ...)
editor = Agent(role="Editor", ...)
seo_specialist = Agent(role="SEO Specialist", ...)

crew = Crew(
    agents=[researcher, writer, editor, seo_specialist],
    tasks=[research_task, write_task, edit_task, seo_task]
)
```

### Software Development Crew

```python
# Plan → Code → Test → Review
architect = Agent(role="Software Architect", ...)
developer = Agent(role="Developer", ...)
tester = Agent(role="QA Tester", ...)
reviewer = Agent(role="Code Reviewer", ...)

crew = Crew(
    agents=[architect, developer, tester, reviewer],
    tasks=[design_task, code_task, test_task, review_task]
)
```

### Market Research Crew

```python
# Collect → Analyze → Visualize → Report
data_collector = Agent(role="Data Collector", ...)
analyst = Agent(role="Data Analyst", ...)
visualizer = Agent(role="Data Visualizer", ...)
reporter = Agent(role="Report Writer", ...)

crew = Crew(
    agents=[data_collector, analyst, visualizer, reporter],
    tasks=[collect_task, analyze_task, visualize_task, report_task]
)
```

## Customization

### Add Custom Tools

```python
from crewai_tools import tool

@tool("Search Database")
def search_database(query: str) -> str:
    """Search internal database for information"""
    results = db.query(query)
    return format_results(results)

agent = Agent(
    role="Database Specialist",
    tools=[search_database]
)
```

### Add Memory

```python
from crewai import Crew

crew = Crew(
    agents=[agent1, agent2],
    tasks=[task1, task2],
    memory=True,  # Enable memory across tasks
    verbose=True
)
```

### Add Callbacks

```python
def task_callback(output):
    print(f"Task completed: {output}")
    log_to_database(output)

task = Task(
    description="Analyze data",
    agent=analyst,
    callback=task_callback
)
```

### Custom Process

```python
from crewai import Process

class CustomProcess(Process):
    def execute(self, tasks, agents):
        # Custom execution logic
        results = []
        for task in tasks:
            result = task.execute()
            results.append(result)
        return results

crew = Crew(
    agents=[...],
    tasks=[...],
    process=CustomProcess()
)
```

## Integration Examples

### API Endpoint

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/create-content", methods=["POST"])
def create_content():
    topic = request.json["topic"]
    
    result = crew.kickoff(inputs={"topic": topic})
    
    return jsonify({
        "content": result,
        "status": "success"
    })
```

### Scheduled Jobs

```python
import schedule
import time

def daily_report():
    result = crew.kickoff(inputs={"date": datetime.now()})
    send_email(result)

schedule.every().day.at("09:00").do(daily_report)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### Slack Bot

```python
from slack_bolt import App

app = App(token=SLACK_TOKEN)

@app.command("/research")
def handle_research(ack, command, say):
    ack()
    
    topic = command['text']
    result = crew.kickoff(inputs={"topic": topic})
    
    say(f"Research complete:\n\n{result}")
```

## Deploy to Production

### Docker Container

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY content_crew.py .

CMD ["python", "content_crew.py"]
```

### AWS Lambda

```python
import json

def lambda_handler(event, context):
    topic = event['topic']
    
    result = crew.kickoff(inputs={"topic": topic})
    
    return {
        'statusCode': 200,
        'body': json.dumps({'result': result})
    }
```

## Use Cases

### Content Marketing
Research → Write → Edit → Optimize → Publish

### Customer Support
Classify → Research → Draft Response → Review → Send

### Data Analysis
Collect → Clean → Analyze → Visualize → Report

### Software Development
Design → Implement → Test → Review → Deploy

## Best Practices

### Clear Role Definitions
```python
# ✅ Specific role
role="Senior Python Developer specializing in backend APIs"

# ❌ Vague role
role="Developer"
```

### Detailed Task Descriptions
```python
# ✅ Clear task
description="""Research quantum computing and provide:
1. Definition and key concepts
2. Current applications
3. Future potential
4. 5 reputable sources"""

# ❌ Vague task
description="Research quantum computing"
```

### Appropriate Tools
```python
# Give agents only the tools they need
researcher = Agent(
    role="Researcher",
    tools=[search_tool, scrape_tool]  # Not writing tools
)

writer = Agent(
    role="Writer",
    tools=[writing_tool, grammar_tool]  # Not search tools
)
```

## Troubleshooting

**Agents Not Collaborating**
- Check task context dependencies
- Enable verbose mode to see interactions
- Verify allow_delegation settings

**Poor Output Quality**
- Improve agent backstories
- Make task descriptions more specific
- Add expected_output to tasks
- Provide better tools

**Slow Execution**
- Use parallel process when possible
- Optimize tool performance
- Cache expensive operations
- Reduce task complexity

## Next Steps

1. Define your crew roles
2. Create task workflow
3. Assign appropriate tools
4. Test with sample inputs
5. Deploy to production
