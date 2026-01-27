# Evaluation Framework

Automated testing and quality metrics for agent systems. Measure accuracy, track performance, and ensure consistent agent behavior across deployments.

## Overview

Test your agents systematically with automated evaluation. Run test suites, measure accuracy, track confidence scores, and analyze performance by category. Essential for maintaining agent quality in production.

## Quick Start

```bash
cd advanced-patterns/evaluation-framework
pip install -r requirements.txt
python evaluation_agent.py
```

**Output:**
```
Agent Evaluation Framework
============================================================

Running 10 test cases...

Test 1: "What is 2+2?" 
Expected: "4"
Got: "The answer is 4"
✅ PASS (Confidence: 0.95)

Test 2: "Capital of France?"
Expected: "Paris"
Got: "Paris"
✅ PASS (Confidence: 0.98)

Test 3: "Who wrote Hamlet?"
Expected: "Shakespeare"
Got: "William Shakespeare"
✅ PASS (Confidence: 0.92)

...

============================================================
RESULTS:
Total Tests: 10
Passed: 9 (90%)
Failed: 1 (10%)
Average Confidence: 0.89

By Category:
- Math: 100% (3/3)
- Geography: 100% (2/2)
- Literature: 80% (4/5)
============================================================
```

## Features

### Automated Test Execution
Run test suites automatically:
```python
test_suite = [
    {"query": "What is 2+2?", "expected": "4", "category": "math"},
    {"query": "Capital of France?", "expected": "Paris", "category": "geography"}
]

results = run_evaluation(test_suite)
```

### Accuracy Measurement
Track pass/fail rates:
- Overall accuracy
- Per-category accuracy
- Confidence scores
- Error analysis

### Regression Testing
Detect performance degradation:
```python
# Compare against baseline
baseline_accuracy = 0.95
current_accuracy = 0.87

if current_accuracy < baseline_accuracy - 0.05:
    alert("Performance regression detected!")
```

### A/B Testing
Compare different agent versions:
```python
results_v1 = evaluate_agent(agent_v1, test_suite)
results_v2 = evaluate_agent(agent_v2, test_suite)

if results_v2.accuracy > results_v1.accuracy:
    promote_to_production(agent_v2)
```

## Available Tools

### run_test()
Execute single test case:
```python
run_test(
    query="What is Python?",
    expected="A programming language",
    category="programming"
)
```

### run_test_suite()
Execute multiple tests:
```python
run_test_suite(test_cases=test_suite)
```

### calculate_metrics()
Compute evaluation metrics:
```python
calculate_metrics(results)
# Returns: {accuracy, precision, recall, f1_score}
```

### compare_results()
Compare evaluation runs:
```python
compare_results(baseline_results, current_results)
```

## Test Case Format

```python
test_case = {
    "id": "test_001",
    "query": "What is 2+2?",
    "expected": "4",
    "category": "math",
    "metadata": {
        "difficulty": "easy",
        "tags": ["arithmetic", "basic"]
    }
}
```

## Evaluation Metrics

### Accuracy
```python
accuracy = correct_answers / total_tests
```

### Confidence Score
```python
# Agent's confidence in its answer
confidence = model_confidence_score  # 0.0 to 1.0
```

### Response Time
```python
import time

start = time.time()
response = agent.invoke(query)
response_time = time.time() - start
```

### Semantic Similarity
```python
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-MiniLM-L6-v2')

def semantic_similarity(expected: str, actual: str) -> float:
    embeddings = model.encode([expected, actual])
    similarity = util.cos_sim(embeddings[0], embeddings[1])
    return float(similarity)
```

## Customization

### Add Custom Metrics

```python
@tool
def calculate_custom_metrics(results: list) -> dict:
    """Calculate domain-specific metrics"""
    metrics = {
        "accuracy": sum(r["passed"] for r in results) / len(results),
        "avg_response_time": sum(r["time"] for r in results) / len(results),
        "avg_token_count": sum(r["tokens"] for r in results) / len(results),
        "cost": sum(r["tokens"] * 0.00001 for r in results)  # Estimate cost
    }
    return metrics
```

### Add Fuzzy Matching

```python
from fuzzywuzzy import fuzz

@tool
def fuzzy_match(expected: str, actual: str, threshold: int = 80) -> bool:
    """Match with fuzzy string comparison"""
    ratio = fuzz.ratio(expected.lower(), actual.lower())
    return ratio >= threshold
```

### Add LLM-as-Judge

```python
@tool
def llm_judge(query: str, expected: str, actual: str) -> dict:
    """Use LLM to evaluate answer quality"""
    prompt = f"""
    Query: {query}
    Expected: {expected}
    Actual: {actual}
    
    Is the actual answer correct? Rate 0-10 and explain.
    """
    
    response = llm.invoke(prompt)
    return {
        "score": extract_score(response),
        "explanation": response
    }
```

## Integration Examples

### CI/CD Pipeline

```yaml
# .github/workflows/test-agent.yml
name: Agent Evaluation

on: [push, pull_request]

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Evaluation
        run: |
          python evaluation_agent.py
          
      - name: Check Threshold
        run: |
          accuracy=$(cat results.json | jq '.accuracy')
          if (( $(echo "$accuracy < 0.90" | bc -l) )); then
            echo "Accuracy below threshold!"
            exit 1
          fi
```

### Scheduled Monitoring

```python
import schedule

def daily_evaluation():
    results = run_evaluation(production_test_suite)
    
    if results["accuracy"] < 0.90:
        send_alert(f"Agent accuracy dropped to {results['accuracy']}")
    
    log_metrics(results)

schedule.every().day.at("09:00").do(daily_evaluation)
```

### Load Testing

```python
from concurrent.futures import ThreadPoolExecutor
import time

def load_test(num_requests: int, concurrency: int):
    start = time.time()
    
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [
            executor.submit(agent.invoke, test_query)
            for _ in range(num_requests)
        ]
        results = [f.result() for f in futures]
    
    duration = time.time() - start
    
    return {
        "total_requests": num_requests,
        "duration": duration,
        "requests_per_second": num_requests / duration,
        "avg_latency": duration / num_requests
    }
```

## Deploy Evaluation

### CloudWatch Dashboard

```python
import boto3

cloudwatch = boto3.client('cloudwatch')

def publish_metrics(results: dict):
    cloudwatch.put_metric_data(
        Namespace='AgentEvaluation',
        MetricData=[
            {
                'MetricName': 'Accuracy',
                'Value': results['accuracy'],
                'Unit': 'Percent'
            },
            {
                'MetricName': 'AvgConfidence',
                'Value': results['avg_confidence'],
                'Unit': 'None'
            }
        ]
    )
```

### Store Results in S3

```python
import json
import boto3
from datetime import datetime

s3 = boto3.client('s3')

def save_results(results: dict):
    timestamp = datetime.now().isoformat()
    key = f"evaluations/{timestamp}.json"
    
    s3.put_object(
        Bucket='agent-evaluations',
        Key=key,
        Body=json.dumps(results)
    )
```

## Use Cases

### Quality Assurance
Run tests before deploying new agent versions to catch regressions.

### Performance Monitoring
Track agent accuracy and response times in production.

### A/B Testing
Compare different prompts, models, or configurations.

### Compliance Validation
Ensure agents meet accuracy requirements for regulated industries.

## Best Practices

### Comprehensive Test Coverage
```python
test_categories = [
    "factual_questions",
    "reasoning",
    "math",
    "coding",
    "edge_cases",
    "adversarial"
]
```

### Regular Evaluation
```python
# Run evaluations:
- Before each deployment
- Daily in production
- After configuration changes
- When adding new features
```

### Version Control Tests
```python
# Store test suites in git
tests/
  ├── unit_tests.json
  ├── integration_tests.json
  ├── regression_tests.json
  └── performance_tests.json
```

### Set Thresholds
```python
THRESHOLDS = {
    "accuracy": 0.90,
    "confidence": 0.80,
    "response_time": 2.0,  # seconds
    "cost_per_query": 0.01  # dollars
}
```

## Troubleshooting

**Low Accuracy**
- Review failed test cases
- Improve prompts
- Add more context
- Use better models

**Inconsistent Results**
- Set temperature=0 for deterministic output
- Use larger sample sizes
- Check for data leakage

**Slow Evaluation**
- Run tests in parallel
- Use smaller test suites for quick checks
- Cache model responses

## Next Steps

1. Create test suite for your agent
2. Set accuracy thresholds
3. Integrate into CI/CD
4. Monitor production metrics
5. Iterate and improve
