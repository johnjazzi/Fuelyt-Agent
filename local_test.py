"""
Local testing script for the Fuelyt AI Agent serverless function.
Tests the Lambda handler directly without needing AWS.
"""

import json
import asyncio
import sys
import os
from datetime import datetime

# Add the current directory to the path so we can import our modules
sys.path.append('.')

from agent.handler import lambda_handler, FuelytAgentHandler


def test_lambda_handler():
    """Test the Lambda handler with various scenarios."""
    
    print("🧪 Testing Fuelyt AI Agent Lambda Handler")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        {
            "name": "New User Introduction",
            "event": {
                "user_id": "test_athlete_1",
                "message": "Hi! I'm a marathon runner looking to improve my nutrition for better performance.",
                "context": {"source": "local_test"}
            }
        },
        {
            "name": "Nutrition Question",
            "event": {
                "user_id": "test_athlete_1",
                "message": "What should I eat before a long run tomorrow morning?",
                "context": {"workout_type": "long_run", "timing": "morning"}
            }
        },
        {
            "name": "Meal Planning Request",
            "event": {
                "user_id": "test_athlete_1",
                "message": "Can you create a 3-day meal plan for my training week?",
                "context": {"request_type": "meal_planning"}
            }
        },
        {
            "name": "Progress Check",
            "event": {
                "user_id": "test_athlete_1",
                "message": "How am I doing with my nutrition goals?",
                "context": {"request_type": "progress_check"}
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔬 Test {i}: {test_case['name']}")
        print("-" * 30)
        
        try:
            # Create Lambda event format
            event = {
                "body": json.dumps(test_case["event"])
            }
            
            # Call the handler
            response = lambda_handler(event, {})
            
            # Parse and display results
            if response["statusCode"] == 200:
                result = json.loads(response["body"])
                print(f"✅ Status: {response['statusCode']}")
                print(f"📝 Response: {result['response'][:200]}{'...' if len(result['response']) > 200 else ''}")
                print(f"⚡ Actions: {result.get('actions_taken', [])}")
                print(f"💡 Recommendations: {len(result.get('recommendations', []))} items")
                
                if result.get('recommendations'):
                    for j, rec in enumerate(result['recommendations'][:2], 1):
                        print(f"   {j}. {rec.get('title', 'Recommendation')}: {rec.get('message', '')[:100]}...")
            else:
                error = json.loads(response["body"])
                print(f"❌ Status: {response['statusCode']}")
                print(f"🚨 Error: {error.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"💥 Test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Lambda Handler Testing Complete")


async def test_agent_handler_directly():
    """Test the agent handler directly (async version)."""
    
    print("\n🔬 Testing Agent Handler Directly")
    print("=" * 50)
    
    try:
        # Initialize the handler
        handler = FuelytAgentHandler()
        
        # Test direct call
        response = await handler.process_request(
            user_id="direct_test_athlete",
            message="I'm a swimmer and I want to optimize my pre-workout nutrition. I usually train at 6 AM.",
            context={"test_type": "direct", "sport": "swimming"}
        )
        
        print("✅ Direct Handler Test Results:")
        print(f"📝 Response: {response.response[:300]}{'...' if len(response.response) > 300 else ''}")
        print(f"⚡ Actions Taken: {response.actions_taken}")
        print(f"💡 Recommendations: {len(response.recommendations)} items")
        
        for i, rec in enumerate(response.recommendations[:3], 1):
            print(f"   {i}. {rec.get('title', 'Recommendation')}")
            print(f"      {rec.get('message', '')[:150]}{'...' if len(rec.get('message', '')) > 150 else ''}")
        
    except Exception as e:
        print(f"💥 Direct handler test failed: {e}")


def test_error_handling():
    """Test error handling scenarios."""
    
    print("\n🚨 Testing Error Handling")
    print("=" * 30)
    
    error_cases = [
        {
            "name": "Missing user_id",
            "event": {"message": "Hello"}
        },
        {
            "name": "Missing message",
            "event": {"user_id": "test"}
        },
        {
            "name": "Empty message",
            "event": {"user_id": "test", "message": ""}
        }
    ]
    
    for case in error_cases:
        print(f"\n🔍 Testing: {case['name']}")
        
        try:
            event = {"body": json.dumps(case["event"])}
            response = lambda_handler(event, {})
            
            if response["statusCode"] == 400:
                print(f"✅ Correctly returned 400 error")
                error_msg = json.loads(response["body"]).get("error", "")
                print(f"📝 Error message: {error_msg}")
            else:
                print(f"⚠️  Expected 400, got {response['statusCode']}")
                
        except Exception as e:
            print(f"💥 Unexpected exception: {e}")


def test_performance():
    """Basic performance test."""
    
    print("\n⏱️  Testing Performance")
    print("=" * 30)
    
    start_time = datetime.now()
    
    try:
        event = {
            "body": json.dumps({
                "user_id": "perf_test_athlete",
                "message": "Quick nutrition question: what's a good post-workout snack?",
                "context": {"test_type": "performance"}
            })
        }
        
        response = lambda_handler(event, {})
        end_time = datetime.now()
        
        duration = (end_time - start_time).total_seconds()
        
        if response["statusCode"] == 200:
            print(f"✅ Performance Test Passed")
            print(f"⏱️  Response time: {duration:.2f} seconds")
            
            if duration < 10:
                print("🚀 Excellent response time!")
            elif duration < 20:
                print("👍 Good response time")
            else:
                print("⚠️  Response time could be improved")
        else:
            print(f"❌ Performance test failed with status {response['statusCode']}")
            
    except Exception as e:
        print(f"💥 Performance test failed: {e}")


def main():
    """Run all tests."""
    
    print("🏃‍♂️ Fuelyt AI Agent - Local Testing Suite")
    print("🧪 Testing the serverless Lambda handler locally")
    print("📅 " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print()
    
    # Check environment
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not set. Some tests may fail.")
        print("Set it with: export OPENAI_API_KEY='your-key-here'")
        print()
    
    # Run tests
    test_lambda_handler()
    
    # Run async test
    try:
        asyncio.run(test_agent_handler_directly())
    except Exception as e:
        print(f"💥 Async test failed: {e}")
    
    test_error_handling()
    test_performance()
    
    print("\n🎉 All tests completed!")
    print("\nNext steps:")
    print("• Run the API server: python main.py")
    print("• Start the frontend: cd frontend && npm run dev")
    print("• Test the full stack: python example_usage.py")


if __name__ == "__main__":
    main()