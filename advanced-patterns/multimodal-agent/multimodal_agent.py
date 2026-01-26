"""
Multi-Modal Agent

Image + text processing with vision models.
"""

from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent
import base64

app = BedrockAgentCoreApp()

def analyze_image(image_data: str) -> dict:
    """Simulate image analysis"""
    # In production, use actual vision model
    return {
        "objects": ["person", "laptop", "desk"],
        "scene": "office workspace",
        "text_detected": "Welcome"
    }

@app.entrypoint
def invoke(payload):
    """
    Multi-modal agent handling text and images.
    """
    prompt = payload.get("prompt")
    image = payload.get("image")  # base64 encoded
    
    agent = Agent()
    
    if image:
        # Analyze image
        analysis = analyze_image(image)
        
        # Combine with text prompt
        context = f"""
        Image Analysis:
        - Objects: {', '.join(analysis['objects'])}
        - Scene: {analysis['scene']}
        - Text: {analysis['text_detected']}
        
        User Question: {prompt}
        """
        
        result = agent(context)
        
        return {
            "answer": result.message,
            "image_analysis": analysis
        }
    else:
        result = agent(prompt)
        return {"answer": result.message}

if __name__ == "__main__":
    print("Multi-Modal Agent Demo")
    print("=" * 60)
    
    tests = [
        {"prompt": "What do you see?", "image": "fake_base64_data"},
        {"prompt": "Describe this workspace", "image": "fake_base64_data"},
        {"prompt": "Hello", "image": None}
    ]
    
    for test in tests:
        print(f"\nPrompt: {test['prompt']}")
        print(f"Has Image: {test['image'] is not None}")
        response = invoke(test)
        print(f"Answer: {response['answer']}")
        if "image_analysis" in response:
            print(f"Analysis: {response['image_analysis']}")
        print("-" * 60)
    
    app.run()
