"""
AutoGen Code Assistant

Multi-agent conversation for code generation and execution.
"""

import autogen

# Configure LLM
config_list = [
    {
        "model": "anthropic.claude-3-sonnet-20240229-v1:0",
        "api_type": "bedrock",
        "aws_region": "us-west-2"
    }
]

llm_config = {
    "config_list": config_list,
    "temperature": 0.7,
}

# Create assistant agent
assistant = autogen.AssistantAgent(
    name="CodeAssistant",
    llm_config=llm_config,
    system_message="""You are a helpful AI assistant that writes Python code.
    When asked to create code, provide clean, well-documented solutions.
    Always include example usage."""
)

# Create user proxy (executor)
user_proxy = autogen.UserProxyAgent(
    name="Executor",
    human_input_mode="NEVER",  # Fully automated
    max_consecutive_auto_reply=10,
    code_execution_config={
        "work_dir": "coding",
        "use_docker": False  # Set to True for safer execution
    }
)

def run_code_task(task: str):
    """Run a coding task with AutoGen agents"""
    print(f"Task: {task}\n")
    print("=" * 60)
    
    # Initiate conversation
    user_proxy.initiate_chat(
        assistant,
        message=task
    )

if __name__ == "__main__":
    # Example tasks
    tasks = [
        "Create a function to calculate the fibonacci sequence up to n terms",
        "Write a function to check if a string is a palindrome"
    ]
    
    for task in tasks:
        run_code_task(task)
        print("\n" + "=" * 60 + "\n")
