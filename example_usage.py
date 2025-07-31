"""
Example usage of the Fuelyt AI Agent.
This file demonstrates how to interact with the agent's various endpoints.
"""

import requests
import json
from datetime import datetime, timedelta

# Base URL for the API
BASE_URL = "http://localhost:8000"

def create_sample_user():
    """Create a sample user and demonstrate basic interactions."""
    
    print("🏃‍♂️ Creating sample athlete profile...")
    
    # Initial chat to create user profile
    response = requests.post(f"{BASE_URL}/chat", json={
        "user_id": "demo_athlete",
        "message": "Hi! I'm Sarah, a 25-year-old competitive swimmer. I train 6 days a week and want to optimize my nutrition for better performance and recovery.",
        "context": {
            "profile_data": {
                "name": "Sarah",
                "age": 25,
                "gender": "female",
                "height_cm": 168,
                "weight_kg": 60,
                "sport": "swimming",
                "activity_level": "very_active",
                "experience_level": "advanced",
                "primary_goal": "performance"
            }
        }
    })
    
    print("✅ User created!")
    print(f"Response: {response.json()['response'][:100]}...")
    return response.json()

def log_sample_workout():
    """Log a sample workout for the athlete."""
    
    print("\n🏊‍♀️ Logging a swim workout...")
    
    workout_data = {
        "type": "cardio",
        "duration_minutes": 90,
        "intensity": "high",
        "exercises": [
            {
                "name": "freestyle swimming",
                "duration_minutes": 60,
                "distance_km": 3.0,
                "calories_burned": 450
            },
            {
                "name": "interval training",
                "duration_minutes": 30,
                "sets": 10,
                "reps": 50,  # 50m sprints
                "calories_burned": 200
            }
        ],
        "energy_level": 8,
        "recovery_rating": 7,
        "performance_notes": "Felt strong during intervals, slight fatigue in the last 15 minutes"
    }
    
    response = requests.post(f"{BASE_URL}/log-workout?user_id=demo_athlete", json=workout_data)
    
    print("✅ Workout logged!")
    recommendations = response.json().get("recommendations", [])
    for rec in recommendations:
        print(f"📋 Recommendation: {rec}")

def log_sample_nutrition():
    """Log sample nutrition data."""
    
    print("\n🥗 Logging breakfast nutrition...")
    
    nutrition_data = {
        "type": "breakfast",
        "foods": [
            {
                "name": "Greek yogurt",
                "quantity": 200,
                "unit": "g",
                "calories": 130,
                "macros": {
                    "protein_g": 20,
                    "carbs_g": 8,
                    "fat_g": 0,
                    "fiber_g": 0
                }
            },
            {
                "name": "banana",
                "quantity": 1,
                "unit": "medium",
                "calories": 105,
                "macros": {
                    "protein_g": 1,
                    "carbs_g": 27,
                    "fat_g": 0,
                    "fiber_g": 3
                }
            },
            {
                "name": "almonds",
                "quantity": 30,
                "unit": "g",
                "calories": 175,
                "macros": {
                    "protein_g": 6,
                    "carbs_g": 6,
                    "fat_g": 15,
                    "fiber_g": 4
                }
            }
        ]
    }
    
    response = requests.post(f"{BASE_URL}/log-nutrition?user_id=demo_athlete", json=nutrition_data)
    
    print("✅ Nutrition logged!")
    analysis = response.json().get("analysis", [])
    for item in analysis:
        print(f"📊 Analysis: {item}")

def get_nutrition_recommendations():
    """Get personalized nutrition recommendations."""
    
    print("\n💡 Getting nutrition recommendations...")
    
    response = requests.get(f"{BASE_URL}/get-recommendations/demo_athlete?recommendation_type=nutrition")
    
    recommendations = response.json().get("recommendations", [])
    print(f"✅ Found {len(recommendations)} recommendations:")
    
    for i, rec in enumerate(recommendations[:3], 1):  # Show first 3
        print(f"\n{i}. {rec.get('title', 'Recommendation')}")
        print(f"   Priority: {rec.get('priority', 'medium')}")
        print(f"   Message: {rec.get('message', 'No message')}")
        
        actions = rec.get('specific_actions', [])
        if actions:
            print("   Actions:")
            for action in actions:
                print(f"   • {action}")

def ask_specific_question():
    """Ask a specific nutrition question."""
    
    print("\n❓ Asking about pre-workout nutrition...")
    
    response = requests.post(f"{BASE_URL}/chat", json={
        "user_id": "demo_athlete",
        "message": "I have swim practice at 6 AM tomorrow. It's a 2-hour intense session with intervals. What should I eat tonight for dinner and tomorrow before practice?",
        "context": {
            "workout_scheduled": {
                "time": "06:00",
                "duration_minutes": 120,
                "intensity": "high",
                "type": "swimming"
            }
        }
    })
    
    print("✅ Got personalized advice!")
    print(f"Response: {response.json()['response']}")
    
    recommendations = response.json().get("recommendations", [])
    if recommendations:
        print("\n📋 Specific recommendations:")
        for rec in recommendations:
            print(f"• {rec}")

def plan_weekly_meals():
    """Request a weekly meal plan."""
    
    print("\n📅 Requesting weekly meal plan...")
    
    meal_request = {
        "duration_days": 7,
        "focus": "performance and recovery",
        "preferences": {
            "prep_time": "moderate",
            "budget": "medium",
            "dietary_restrictions": []
        },
        "training_schedule": {
            "monday": "high_intensity",
            "tuesday": "moderate",
            "wednesday": "high_intensity", 
            "thursday": "recovery",
            "friday": "high_intensity",
            "saturday": "moderate",
            "sunday": "rest"
        }
    }
    
    response = requests.post(f"{BASE_URL}/plan-meal?user_id=demo_athlete", json=meal_request)
    
    print("✅ Weekly meal plan created!")
    meal_plan = response.json().get("meal_plan", [])
    for plan in meal_plan[:2]:  # Show first 2 items
        print(f"📋 {plan}")

def check_dashboard():
    """Check the user's dashboard data."""
    
    print("\n📊 Checking dashboard data...")
    
    response = requests.get(f"{BASE_URL}/dashboard/demo_athlete")
    dashboard = response.json()
    
    print("✅ Dashboard data retrieved!")
    print(f"User: {dashboard.get('user_profile', {}).get('name', 'Unknown')}")
    print(f"Goal: {dashboard.get('user_profile', {}).get('goal', 'Not set')}")
    print(f"Sport: {dashboard.get('user_profile', {}).get('sport', 'Not set')}")
    
    nutrition_summary = dashboard.get('nutrition_summary', {})
    if nutrition_summary and nutrition_summary.get('current_averages'):
        avg = nutrition_summary['current_averages']
        print(f"Avg daily calories: {avg.get('calories', 0):.0f}")
        print(f"Avg daily protein: {avg.get('protein_g', 0):.1f}g")
    
    workout_summary = dashboard.get('workout_summary', {})
    if workout_summary:
        print(f"Recent workouts: {workout_summary.get('recent_workouts_count', 0)}")
        print(f"Avg energy level: {workout_summary.get('avg_energy_level', 0):.1f}/10")

def demonstrate_conversation_flow():
    """Demonstrate a natural conversation flow."""
    
    print("\n💬 Demonstrating conversation flow...")
    
    questions = [
        "I'm feeling tired during my afternoon practices. Any suggestions?",
        "What's the best post-workout snack for muscle recovery?", 
        "Should I eat differently on rest days vs training days?",
        "I'm trying to maintain my weight but increase lean muscle. How should I adjust my macros?"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n{i}. Question: {question}")
        
        response = requests.post(f"{BASE_URL}/chat", json={
            "user_id": "demo_athlete",
            "message": question
        })
        
        answer = response.json()['response']
        print(f"   Answer: {answer[:150]}{'...' if len(answer) > 150 else ''}")

def main():
    """Run all examples."""
    
    print("🚀 Fuelyt AI Agent - Example Usage")
    print("=" * 50)
    
    try:
        # Check if server is running
        health_response = requests.get(BASE_URL)
        print(f"✅ Server is running: {health_response.json()['status']}")
        print()
        
        # Run examples
        create_sample_user()
        log_sample_workout() 
        log_sample_nutrition()
        get_nutrition_recommendations()
        ask_specific_question()
        plan_weekly_meals()
        check_dashboard()
        demonstrate_conversation_flow()
        
        print("\n🎉 All examples completed successfully!")
        print("\nTry visiting http://localhost:8000/docs for the interactive API documentation.")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the Fuelyt API server.")
        print("Make sure the server is running with: python main.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()