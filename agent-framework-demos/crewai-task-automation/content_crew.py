"""
CrewAI Content Creation Pipeline

Automated blog post creation with:
- Research agent
- Writer agent  
- Editor agent
"""

from crewai import Agent, Task, Crew
from langchain_aws import ChatBedrock

# Initialize LLM
llm = ChatBedrock(
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    region_name="us-west-2"
)

# Define agents
researcher = Agent(
    role="Research Specialist",
    goal="Find accurate and relevant information on the given topic",
    backstory="You are an expert researcher with a keen eye for credible sources and key insights.",
    llm=llm,
    verbose=True
)

writer = Agent(
    role="Content Writer",
    goal="Create engaging and informative blog posts",
    backstory="You are a skilled writer who can transform research into compelling narratives.",
    llm=llm,
    verbose=True
)

editor = Agent(
    role="Editor",
    goal="Polish content for clarity, grammar, and impact",
    backstory="You are a meticulous editor who ensures every piece is publication-ready.",
    llm=llm,
    verbose=True
)

def create_blog_post(topic: str) -> str:
    """Create a blog post on the given topic"""
    
    # Define tasks
    research_task = Task(
        description=f"Research the topic: {topic}. Find 5 key points and relevant examples.",
        agent=researcher,
        expected_output="A list of 5 key points with supporting details"
    )
    
    writing_task = Task(
        description=f"Write a 500-word blog post about {topic} using the research provided.",
        agent=writer,
        expected_output="A complete blog post with introduction, body, and conclusion",
        context=[research_task]
    )
    
    editing_task = Task(
        description="Edit the blog post for clarity, grammar, and engagement.",
        agent=editor,
        expected_output="A polished, publication-ready blog post",
        context=[writing_task]
    )
    
    # Create crew
    crew = Crew(
        agents=[researcher, writer, editor],
        tasks=[research_task, writing_task, editing_task],
        verbose=True
    )
    
    # Execute
    result = crew.kickoff()
    return result

if __name__ == "__main__":
    topic = "The Future of AI Agents in Enterprise"
    
    print(f"Creating blog post about: {topic}\n")
    print("=" * 60)
    
    blog_post = create_blog_post(topic)
    
    print("\n" + "=" * 60)
    print("FINAL BLOG POST:")
    print("=" * 60)
    print(blog_post)
