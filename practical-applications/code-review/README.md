# Code Review Agent

Automated code analysis for security vulnerabilities, code quality issues, and best practice violations. Get instant feedback on pull requests.

## Overview

Analyze code for security issues, bugs, code smells, and style violations. Provides actionable suggestions for improvement. Perfect for automated PR reviews and maintaining code quality.

## Quick Start

```bash
cd practical-applications/code-review
pip install -r requirements.txt
python code_review_agent.py
```

**Output:**
```
Code Review Agent
============================================================

File: api.py
Code:
```python
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return db.execute(query)
```

Review:
============================================================

🔴 SECURITY: SQL Injection Vulnerability
Line 2: Direct string interpolation in SQL query
Severity: CRITICAL

Suggestion: Use parameterized queries
```python
query = "SELECT * FROM users WHERE id = %s"
return db.execute(query, (user_id,))
```

============================================================

File: utils.py
Code:
```python
def process_data(data):
    result = []
    for item in data:
        if item != None:
            result.append(item)
    return result
```

Review:
============================================================

🟡 CODE QUALITY: Use list comprehension
Line 2-5: Loop can be simplified
Severity: LOW

Suggestion:
```python
def process_data(data):
    return [item for item in data if item is not None]
```

🟡 STYLE: Use 'is not None' instead of '!= None'
Line 4: PEP 8 recommendation
Severity: LOW

============================================================
```

## Features

### Security Analysis
Detect vulnerabilities:
- SQL injection
- XSS vulnerabilities
- Hardcoded secrets
- Insecure dependencies
- Authentication issues

### Code Quality
Find code smells:
- Duplicate code
- Complex functions
- Long methods
- Dead code
- Poor naming

### Best Practices
Enforce standards:
- PEP 8 (Python)
- ESLint rules (JavaScript)
- Language-specific conventions
- Team coding standards

### Performance Issues
Identify inefficiencies:
- N+1 queries
- Inefficient algorithms
- Memory leaks
- Unnecessary computations

## Available Tools

### review_code()
Analyze code snippet:
```python
review_code(
    code="def foo(): pass",
    language="python",
    checks=["security", "quality", "style"]
)
```

### check_security()
Security-focused analysis:
```python
check_security(code, language)
# Returns: [{"type": "sql_injection", "severity": "critical", ...}]
```

### suggest_improvements()
Get improvement suggestions:
```python
suggest_improvements(code, language)
# Returns: [{"issue": "...", "suggestion": "...", "example": "..."}]
```

### analyze_pr()
Review entire pull request:
```python
analyze_pr(pr_number, repo)
# Returns: {"files": [...], "summary": "...", "approve": False}
```

## Example Reviews

### SQL Injection

```python
# ❌ Vulnerable
query = f"SELECT * FROM users WHERE email = '{email}'"

# ✅ Fixed
query = "SELECT * FROM users WHERE email = %s"
cursor.execute(query, (email,))
```

### Hardcoded Secrets

```python
# ❌ Insecure
API_KEY = "sk-1234567890abcdef"

# ✅ Secure
API_KEY = os.getenv("API_KEY")
```

### XSS Vulnerability

```javascript
// ❌ Vulnerable
element.innerHTML = userInput;

// ✅ Safe
element.textContent = userInput;
```

### Performance Issue

```python
# ❌ Inefficient (N+1 queries)
for user in users:
    orders = db.query(f"SELECT * FROM orders WHERE user_id = {user.id}")

# ✅ Efficient (single query)
user_ids = [user.id for user in users]
orders = db.query("SELECT * FROM orders WHERE user_id IN %s", (user_ids,))
```

## Customization

### Add Custom Rules

```python
CUSTOM_RULES = [
    {
        "id": "no-print-statements",
        "pattern": r"print\(",
        "message": "Use logging instead of print statements",
        "severity": "medium"
    },
    {
        "id": "require-docstrings",
        "pattern": r"def \w+\([^)]*\):\s*(?!\"\"\")",
        "message": "Functions must have docstrings",
        "severity": "low"
    }
]

@tool
def check_custom_rules(code: str) -> list:
    """Check code against custom rules"""
    issues = []
    for rule in CUSTOM_RULES:
        if re.search(rule["pattern"], code):
            issues.append({
                "rule": rule["id"],
                "message": rule["message"],
                "severity": rule["severity"]
            })
    return issues
```

### Add Static Analysis Tools

```python
import subprocess
import json

@tool
def run_pylint(file_path: str) -> dict:
    """Run pylint analysis"""
    result = subprocess.run(
        ["pylint", "--output-format=json", file_path],
        capture_output=True,
        text=True
    )
    return json.loads(result.stdout)

@tool
def run_bandit(file_path: str) -> dict:
    """Run Bandit security scanner"""
    result = subprocess.run(
        ["bandit", "-f", "json", file_path],
        capture_output=True,
        text=True
    )
    return json.loads(result.stdout)
```

### Add Dependency Scanning

```python
import requests

@tool
def check_dependencies(requirements_file: str) -> list:
    """Check for vulnerable dependencies"""
    with open(requirements_file) as f:
        packages = f.readlines()
    
    vulnerabilities = []
    for package in packages:
        name, version = package.strip().split("==")
        
        # Check against vulnerability database
        response = requests.get(
            f"https://pypi.org/pypi/{name}/{version}/json"
        )
        
        if response.json().get("vulnerabilities"):
            vulnerabilities.append({
                "package": name,
                "version": version,
                "vulnerabilities": response.json()["vulnerabilities"]
            })
    
    return vulnerabilities
```

## Integration Examples

### GitHub Actions

```yaml
# .github/workflows/code-review.yml
name: Automated Code Review

on: [pull_request]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Run Code Review
        run: |
          python code_review_agent.py --pr ${{ github.event.pull_request.number }}
      
      - name: Post Comment
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const review = fs.readFileSync('review.json', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: review
            });
```

### GitLab CI

```yaml
# .gitlab-ci.yml
code_review:
  stage: test
  script:
    - python code_review_agent.py --files $CI_MERGE_REQUEST_DIFF_BASE_SHA..$CI_COMMIT_SHA
    - cat review.md
  only:
    - merge_requests
```

### Pre-commit Hook

```python
# .git/hooks/pre-commit
#!/usr/bin/env python3

import subprocess
import sys

# Get staged files
result = subprocess.run(
    ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
    capture_output=True,
    text=True
)

files = result.stdout.strip().split('\n')
python_files = [f for f in files if f.endswith('.py')]

# Review each file
issues = []
for file in python_files:
    with open(file) as f:
        code = f.read()
    
    review = review_code(code, "python")
    critical_issues = [i for i in review if i["severity"] == "critical"]
    issues.extend(critical_issues)

if issues:
    print("❌ Critical issues found:")
    for issue in issues:
        print(f"  - {issue['message']}")
    sys.exit(1)

print("✅ Code review passed")
sys.exit(0)
```

## Deploy to Production

### Lambda Function for GitHub Webhooks

```python
import json
import boto3
from github import Github

def lambda_handler(event, context):
    # Parse webhook
    body = json.loads(event['body'])
    
    if body['action'] == 'opened' or body['action'] == 'synchronize':
        pr_number = body['pull_request']['number']
        repo_name = body['repository']['full_name']
        
        # Get PR files
        gh = Github(os.getenv('GITHUB_TOKEN'))
        repo = gh.get_repo(repo_name)
        pr = repo.get_pull(pr_number)
        
        # Review each file
        comments = []
        for file in pr.get_files():
            if file.filename.endswith('.py'):
                review = review_code(file.patch, 'python')
                
                for issue in review:
                    comments.append({
                        "path": file.filename,
                        "line": issue["line"],
                        "body": f"**{issue['severity'].upper()}**: {issue['message']}\n\n{issue['suggestion']}"
                    })
        
        # Post review
        pr.create_review(
            body="Automated code review completed",
            event="COMMENT",
            comments=comments
        )
    
    return {'statusCode': 200}
```

### API Endpoint

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/review", methods=["POST"])
def review_endpoint():
    code = request.json["code"]
    language = request.json.get("language", "python")
    
    review = review_code(code, language)
    
    return jsonify({
        "issues": review,
        "summary": generate_summary(review),
        "approve": all(i["severity"] != "critical" for i in review)
    })
```

## Use Cases

### Pull Request Reviews
Automatically review PRs before human review.

### Pre-commit Checks
Catch issues before code is committed.

### CI/CD Pipeline
Block deployments with critical issues.

### Code Quality Monitoring
Track code quality metrics over time.

## Best Practices

### Severity Levels
```python
SEVERITY = {
    "critical": "Blocks merge",
    "high": "Should fix before merge",
    "medium": "Fix soon",
    "low": "Nice to have"
}
```

### Actionable Feedback
```
❌ "Bad code"
✅ "Use parameterized queries to prevent SQL injection"

❌ "This is wrong"
✅ "Replace 'x == None' with 'x is None' per PEP 8"
```

### Context-Aware Rules
```python
# Different rules for different contexts
if file_path.startswith("tests/"):
    # Allow print statements in tests
    rules.remove("no-print-statements")
```

## Troubleshooting

**False Positives**
- Tune rule sensitivity
- Add exceptions for specific patterns
- Use allowlist for known safe code

**Missing Issues**
- Add more rules
- Use multiple analysis tools
- Increase check coverage

**Slow Reviews**
- Cache analysis results
- Review only changed lines
- Run checks in parallel

## Next Steps

1. Configure rules for your codebase
2. Integrate with your CI/CD pipeline
3. Set up GitHub/GitLab webhooks
4. Train team on addressing issues
5. Monitor and refine rules
