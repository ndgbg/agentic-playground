"""
Evaluation Framework

Automated testing and quality metrics for agents.
"""

from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent
from typing import List, Dict

app = BedrockAgentCoreApp()

# Test cases
TEST_CASES = [
    {"input": "What is 2+2?", "expected": "4", "category": "math"},
    {"input": "What is the capital of France?", "expected": "Paris", "category": "geography"},
    {"input": "Who wrote Romeo and Juliet?", "expected": "Shakespeare", "category": "literature"}
]

def evaluate_response(response: str, expected: str) -> dict:
    """Evaluate agent response"""
    response_lower = response.lower()
    expected_lower = expected.lower()
    
    # Check if expected answer is in response
    correct = expected_lower in response_lower
    
    # Calculate confidence (simulated)
    confidence = 0.9 if correct else 0.3
    
    return {
        "correct": correct,
        "confidence": confidence,
        "response": response
    }

def run_evaluation(test_cases: List[Dict]) -> dict:
    """Run evaluation on test cases"""
    agent = Agent()
    results = []
    
    for test in test_cases:
        result = agent(test["input"])
        evaluation = evaluate_response(result.message, test["expected"])
        
        results.append({
            "input": test["input"],
            "expected": test["expected"],
            "actual": result.message,
            "correct": evaluation["correct"],
            "confidence": evaluation["confidence"],
            "category": test["category"]
        })
    
    # Calculate metrics
    total = len(results)
    correct = sum(1 for r in results if r["correct"])
    accuracy = correct / total if total > 0 else 0
    avg_confidence = sum(r["confidence"] for r in results) / total if total > 0 else 0
    
    return {
        "results": results,
        "metrics": {
            "total_tests": total,
            "correct": correct,
            "accuracy": accuracy,
            "avg_confidence": avg_confidence
        }
    }

@app.entrypoint
def invoke(payload):
    """
    Evaluation framework for agents.
    """
    test_cases = payload.get("test_cases", TEST_CASES)
    
    evaluation = run_evaluation(test_cases)
    
    return evaluation

if __name__ == "__main__":
    print("Evaluation Framework Demo")
    print("=" * 60)
    
    evaluation = invoke({"test_cases": TEST_CASES})
    
    print("\nTest Results:")
    for result in evaluation["results"]:
        status = "✅" if result["correct"] else "❌"
        print(f"\n{status} {result['category'].upper()}")
        print(f"Q: {result['input']}")
        print(f"Expected: {result['expected']}")
        print(f"Got: {result['actual'][:100]}...")
        print(f"Confidence: {result['confidence']:.2f}")
    
    print("\n" + "=" * 60)
    print("Metrics:")
    metrics = evaluation["metrics"]
    print(f"Total Tests: {metrics['total_tests']}")
    print(f"Correct: {metrics['correct']}")
    print(f"Accuracy: {metrics['accuracy']:.2%}")
    print(f"Avg Confidence: {metrics['avg_confidence']:.2f}")
    
    app.run()
