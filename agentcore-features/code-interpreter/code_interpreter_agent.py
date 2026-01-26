"""
AgentCore Code Interpreter Demo

Demonstrates safe code execution for data analysis and automation.
"""

from bedrock_agentcore import BedrockAgentCoreApp
from bedrock_agentcore.code_interpreter import CodeInterpreter
from strands import Agent
import json

app = BedrockAgentCoreApp()
code_interpreter = CodeInterpreter()

@app.entrypoint
def invoke(payload):
    """
    Agent with code execution capabilities.
    """
    user_message = payload.get("prompt")
    
    # Create agent
    agent = Agent()
    
    # Agent can generate and execute code
    result = agent(f"""
    {user_message}
    
    You can write and execute Python code to solve this.
    Use the code interpreter to run calculations, analyze data, or create visualizations.
    """)
    
    # If agent generated code, execute it
    if "```python" in result.message:
        # Extract code
        code = result.message.split("```python")[1].split("```")[0].strip()
        
        # Execute in sandbox
        execution_result = code_interpreter.execute(
            language="python",
            code=code
        )
        
        return {
            "answer": result.message,
            "code": code,
            "execution_result": execution_result.get("output"),
            "error": execution_result.get("error")
        }
    
    return {
        "answer": result.message
    }

if __name__ == "__main__":
    print("Code Interpreter Demo")
    print("=" * 60)
    
    test_queries = [
        "Calculate the fibonacci sequence up to 10 numbers",
        "Create a list of prime numbers between 1 and 50",
        "Calculate the mean, median, and mode of [5, 2, 8, 2, 9, 1, 3, 2]",
        "Generate a simple bar chart showing sales data: Jan=100, Feb=150, Mar=120"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 60)
        
        response = invoke({"prompt": query})
        
        print(f"Answer: {response['answer']}")
        
        if "code" in response:
            print(f"\nGenerated Code:")
            print(response['code'])
            print(f"\nExecution Result:")
            print(response.get('execution_result', 'No output'))
        
        print("=" * 60)
    
    print("\nStarting server on port 8080...")
    app.run()
