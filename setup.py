"""
Setup script for the Fuelyt AI Agent.
Helps with initial configuration and testing.
"""

import os
import sys
import json
from datetime import datetime

def check_requirements():
    """Check if all requirements are met."""
    print("🔍 Checking requirements...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        return False
    else:
        print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Check required packages
    required_packages = [
        "openai", "tinydb", "pydantic", "fastapi", "uvicorn"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} missing")
    
    if missing_packages:
        print(f"\n📦 Install missing packages with:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_openai_key():
    """Check if OpenAI API key is configured."""
    print("\n🔑 Checking OpenAI API key...")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY environment variable not set")
        print("Set it with: export OPENAI_API_KEY='your-api-key-here'")
        return False
    elif api_key == "your-openai-api-key-here":
        print("❌ Please replace the placeholder API key with your real key")
        return False
    else:
        print(f"✅ API key configured (ending in ...{api_key[-4:]})")
        return True

def create_sample_data():
    """Create sample user data for testing."""
    print("\n📋 Creating sample user data...")
    
    sample_user = {
        "user_id": "sample_athlete",
        "profile": {
            "name": "Demo Athlete",
            "age": 28,
            "gender": "not_specified",
            "height_cm": 175.0,
            "weight_kg": 70.0,
            "activity_level": "very_active",
            "sport": "running",
            "experience_level": "intermediate",
            "dietary_restrictions": [],
            "allergies": []
        },
        "goals": {
            "primary_goal": "performance",
            "target_weight_kg": 68.0,
            "target_body_fat_percentage": 12.0,
            "performance_goals": ["run sub-3 hour marathon"],
            "timeline": "6 months",
            "daily_calorie_target": 2800,
            "macro_targets": {
                "protein_g": 140.0,
                "carbs_g": 350.0,
                "fat_g": 93.0,
                "fiber_g": 35.0
            }
        },
        "workouts": {
            "logged_workouts": [
                {
                    "id": "workout_20241201_0700",
                    "date": datetime.utcnow().isoformat(),
                    "type": "cardio",
                    "duration_minutes": 45,
                    "intensity": "moderate",
                    "exercises": [
                        {
                            "name": "running",
                            "duration_minutes": 45,
                            "distance_km": 8.0,
                            "calories_burned": 400
                        }
                    ],
                    "energy_level": 8,
                    "recovery_rating": 7,
                    "performance_notes": "Good pace, felt strong throughout"
                }
            ],
            "planned_workouts": []
        },
        "nutrition": {
            "daily_logs": [
                {
                    "date": datetime.utcnow().date().isoformat(),
                    "meals": [
                        {
                            "id": "meal_breakfast_001",
                            "type": "breakfast",
                            "time": datetime.utcnow().isoformat(),
                            "foods": [
                                {
                                    "name": "oatmeal with banana",
                                    "quantity": 1,
                                    "unit": "serving",
                                    "calories": 350,
                                    "macros": {
                                        "protein_g": 12,
                                        "carbs_g": 65,
                                        "fat_g": 8,
                                        "fiber_g": 10
                                    }
                                }
                            ],
                            "total_calories": 350,
                            "total_macros": {
                                "protein_g": 12,
                                "carbs_g": 65,
                                "fat_g": 8,
                                "fiber_g": 10
                            }
                        }
                    ],
                    "daily_totals": {
                        "calories": 350,
                        "protein_g": 12,
                        "carbs_g": 65,
                        "fat_g": 8,
                        "fiber_g": 10,
                        "water_ml": 500
                    },
                    "adherence_to_goals": {
                        "calorie_percentage": 12.5,
                        "protein_percentage": 8.6,
                        "carbs_percentage": 18.6,
                        "fat_percentage": 8.6
                    }
                }
            ],
            "favorite_foods": [],
            "meal_plans": []
        },
        "recipes": {
            "saved_recipes": []
        },
        "calendar": {
            "scheduled_items": []
        },
        "progress_tracking": {
            "body_measurements": [],
            "performance_metrics": [],
            "energy_mood_tracking": []
        },
        "settings": {
            "units": {
                "weight": "kg",
                "distance": "km",
                "temperature": "celsius"
            },
            "notifications": {
                "meal_reminders": True,
                "workout_reminders": True,
                "hydration_reminders": True,
                "progress_check_ins": True
            },
            "privacy": {
                "share_data": False,
                "analytics": True
            }
        },
        "ai_context": {
            "conversation_history": [],
            "preferences_learned": {
                "communication_style": "encouraging",
                "preferred_meal_types": ["high-carb"],
                "workout_preferences": ["morning runs"],
                "learning_patterns": {}
            }
        },
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    # Save to file
    with open("sample_user_data.json", "w") as f:
        json.dump(sample_user, f, indent=2)
    
    print("✅ Sample user data created in sample_user_data.json")

def test_database():
    """Test database functionality."""
    print("\n💾 Testing database...")
    
    try:
        from tinydb import TinyDB
        
        # Create test database
        test_db = TinyDB("test_fuelyt.json")
        test_table = test_db.table('test_users')
        
        # Insert test data
        test_table.insert({"test": "data", "timestamp": datetime.utcnow().isoformat()})
        
        # Read back
        results = test_table.all()
        if results:
            print("✅ Database test successful")
            
            # Clean up
            os.remove("test_fuelyt.json")
            return True
        else:
            print("❌ Database test failed")
            return False
            
    except Exception as e:
        print(f"❌ Database test error: {e}")
        return False

def run_quick_test():
    """Run a quick functionality test."""
    print("\n🧪 Running quick functionality test...")
    
    try:
        # Test imports
        from data_models import UserProfile, Goals
        from database_manager import DatabaseManager
        from config import Config
        from utils import generate_unique_id, calculate_nutrition_totals
        
        # Test basic functionality
        unique_id = generate_unique_id("test")
        print(f"✅ Generated unique ID: {unique_id}")
        
        # Test nutrition calculation
        test_foods = [
            {"calories": 100, "macros": {"protein_g": 10, "carbs_g": 15, "fat_g": 2}},
            {"calories": 200, "macros": {"protein_g": 5, "carbs_g": 30, "fat_g": 8}}
        ]
        totals = calculate_nutrition_totals(test_foods)
        print(f"✅ Nutrition calculation test: {totals['calories']} calories")
        
        # Test config
        config_valid = Config.validate_config()
        if config_valid:
            print("✅ Configuration validation passed")
        else:
            print("⚠️  Configuration has warnings (check API key)")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def main():
    """Run the complete setup check."""
    print("🚀 Fuelyt AI Agent - Setup & Verification")
    print("=" * 50)
    
    all_good = True
    
    # Run all checks
    if not check_requirements():
        all_good = False
    
    if not check_openai_key():
        all_good = False
    
    if not test_database():
        all_good = False
    
    if not run_quick_test():
        all_good = False
    
    # Create sample data regardless
    create_sample_data()
    
    print("\n" + "=" * 50)
    
    if all_good:
        print("🎉 All checks passed! You're ready to run Fuelyt.")
        print("\nNext steps:")
        print("1. Run the server: python main.py")
        print("2. Test the API: python example_usage.py")
        print("3. Visit http://localhost:8000/docs for interactive docs")
    else:
        print("⚠️  Some issues found. Please fix them before running Fuelyt.")
        print("\nCommon fixes:")
        print("• Install dependencies: pip install -r requirements.txt")
        print("• Set API key: export OPENAI_API_KEY='your-key'")
        print("• Check Python version (3.8+ required)")

if __name__ == "__main__":
    main()