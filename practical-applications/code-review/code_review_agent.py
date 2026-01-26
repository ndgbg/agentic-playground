"""
Code Review Agent

Automated PR analysis and security scanning.
"""

from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent, tool

app = BedrockAgentCoreApp()

SAMPLE_CODE = """
def process_user_input(user_input):
    query = "SELECT * FROM users WHERE name = '" + user_input + "'"
    result = db.execute(query)
    return result
"""

@tool
def check_security_issues(code: str) -> list:
    """Check for security vulnerabilities"""
    issues = []
    
    if "eval(" in code:
        issues.append("Security: Avoid using eval()")
    if "exec(" in code:
        issues.append("Security: Avoid using exec()")
    if "SELECT * FROM" in code and "+" in code:
        issues.append("Security: SQL injection vulnerability detected")
    if "password" in code.lower() and "=" in code:
        issues.append("Security: Hardcoded password detected")
    
    return issues

@tool
def check_code_quality(code: str) -> list:
    """Check code quality issues"""
    issues = []
    
    if "TODO" in code:
        issues.append("Quality: TODO comment found")
    if len(code.split("\n")) > 50:
        issues.append("Quality: Function too long (>50 lines)")
    if "import *" in code:
        issues.append("Quality: Avoid wildcard imports")
    
    return issues

@tool
def suggest_improvements(code: str) -> list:
    """Suggest code improvements"""
    suggestions = []
    
    if "for i in range(len(" in code:
        suggestions.append("Use enumerate() instead of range(len())")
    if "if x == True" in code:
        suggestions.append("Use 'if x:' instead of 'if x == True:'")
    
    return suggestions

@app.entrypoint
def invoke(payload):
    """
    Code review agent.
    """
    code = payload.get("code", SAMPLE_CODE)
    
    agent = Agent()
    agent.add_tool(check_security_issues)
    agent.add_tool(check_code_quality)
    agent.add_tool(suggest_improvements)
    
    prompt = f"Review this code:\n\n{code}\n\nProvide security analysis, quality checks, and suggestions."
    result = agent(prompt)
    
    return {"review": result.message}

if __name__ == "__main__":
    print("Code Review Agent Demo")
    print("=" * 60)
    
    print(f"\nCode to Review:\n{SAMPLE_CODE}")
    print("-" * 60)
    
    response = invoke({"code": SAMPLE_CODE})
    print(f"\nReview:\n{response['review']}")
    print("=" * 60)
    
    app.run()
