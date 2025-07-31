"""
Database management for the Fuelyt AI Agent using TinyDB.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from tinydb import TinyDB, Query


class DatabaseManager:
    def __init__(self, db_path: str = "fuelyt_data.json"):
        """Initialize the database manager with TinyDB."""
        self.db_path = db_path
        self.db = TinyDB(db_path)
        self.users_table = self.db.table('users')
        
    def create_user(self, user_id: str, profile_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a new user with default data structure."""
        
        # Default profile if none provided
        if not profile_data:
            profile_data = {
                "name": f"User {user_id[:8]}",
                "age": 25,
                "gender": "not_specified",
                "height_cm": 170.0,
                "weight_kg": 70.0,
                "activity_level": "moderately_active",
                "sport": None,
                "experience_level": "beginner",
                "dietary_restrictions": [],
                "allergies": []
            }
        
        # Default user data structure based on schema
        user_data = {
            "user_id": user_id,
            "profile": profile_data,
            "goals": {
                "primary_goal": "maintenance",
                "target_weight_kg": profile_data.get("weight_kg", 70.0),
                "target_body_fat_percentage": None,
                "performance_goals": [],
                "timeline": None,
                "daily_calorie_target": self._calculate_default_calories(profile_data),
                "macro_targets": {
                    "protein_g": 100.0,
                    "carbs_g": 200.0,
                    "fat_g": 60.0,
                    "fiber_g": 25.0
                }
            },
            "workouts": {
                "logged_workouts": [],
                "planned_workouts": []
            },
            "nutrition": {
                "daily_logs": [],
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
                    "communication_style": "friendly",
                    "preferred_meal_types": [],
                    "workout_preferences": [],
                    "learning_patterns": {}
                }
            },
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Insert user into database
        self.users_table.insert(user_data)
        return user_data
    
    def get_user_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve user data by user_id."""
        User = Query()
        result = self.users_table.search(User.user_id == user_id)
        return result[0] if result else None
    
    def update_user_data(self, user_id: str, updated_data: Dict[str, Any]) -> bool:
        """Update user data in the database."""
        User = Query()
        
        # Add updated timestamp
        updated_data["updated_at"] = datetime.utcnow().isoformat()
        
        # Update the user record
        result = self.users_table.update(updated_data, User.user_id == user_id)
        return len(result) > 0
    
    def add_workout(self, user_id: str, workout_data: Dict[str, Any]) -> bool:
        """Add a workout to the user's logged workouts."""
        user_data = self.get_user_data(user_id)
        if not user_data:
            return False
        
        # Add workout to logged workouts
        user_data["workouts"]["logged_workouts"].append(workout_data)
        user_data["updated_at"] = datetime.utcnow().isoformat()
        
        User = Query()
        result = self.users_table.update(user_data, User.user_id == user_id)
        return len(result) > 0
    
    def add_nutrition_log(self, user_id: str, nutrition_data: Dict[str, Any]) -> bool:
        """Add nutrition data to the user's daily logs."""
        user_data = self.get_user_data(user_id)
        if not user_data:
            return False
        
        # Find existing log for the date or create new one
        log_date = nutrition_data.get("date", datetime.utcnow().date().isoformat())
        existing_log = None
        
        for log in user_data["nutrition"]["daily_logs"]:
            if log["date"] == log_date:
                existing_log = log
                break
        
        if existing_log:
            # Add meal to existing day
            existing_log["meals"].append(nutrition_data)
            # Recalculate daily totals
            self._recalculate_daily_totals(existing_log)
        else:
            # Create new daily log
            new_log = {
                "date": log_date,
                "meals": [nutrition_data],
                "daily_totals": {
                    "calories": nutrition_data.get("total_calories", 0),
                    "protein_g": nutrition_data.get("total_macros", {}).get("protein_g", 0),
                    "carbs_g": nutrition_data.get("total_macros", {}).get("carbs_g", 0),
                    "fat_g": nutrition_data.get("total_macros", {}).get("fat_g", 0),
                    "fiber_g": nutrition_data.get("total_macros", {}).get("fiber_g", 0),
                    "water_ml": 0
                },
                "adherence_to_goals": {}
            }
            user_data["nutrition"]["daily_logs"].append(new_log)
        
        user_data["updated_at"] = datetime.utcnow().isoformat()
        
        User = Query()
        result = self.users_table.update(user_data, User.user_id == user_id)
        return len(result) > 0
    
    def get_recent_workouts(self, user_id: str, days: int = 7) -> List[Dict[str, Any]]:
        """Get recent workouts for the user."""
        user_data = self.get_user_data(user_id)
        if not user_data:
            return []
        
        # Filter workouts from the last N days
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        recent_workouts = []
        
        for workout in user_data["workouts"]["logged_workouts"]:
            workout_date = datetime.fromisoformat(workout["date"].replace('Z', '+00:00'))
            if workout_date >= cutoff_date:
                recent_workouts.append(workout)
        
        return recent_workouts
    
    def get_recent_nutrition(self, user_id: str, days: int = 7) -> List[Dict[str, Any]]:
        """Get recent nutrition logs for the user."""
        user_data = self.get_user_data(user_id)
        if not user_data:
            return []
        
        # Filter nutrition logs from the last N days
        cutoff_date = datetime.utcnow().date() - timedelta(days=days)
        recent_logs = []
        
        for log in user_data["nutrition"]["daily_logs"]:
            log_date = datetime.fromisoformat(log["date"]).date()
            if log_date >= cutoff_date:
                recent_logs.append(log)
        
        return recent_logs
    
    def add_conversation_history(self, user_id: str, user_message: str, agent_response: str, context: Optional[Dict] = None):
        """Add conversation to user's AI context history."""
        user_data = self.get_user_data(user_id)
        if not user_data:
            return False
        
        conversation_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_message": user_message,
            "agent_response": agent_response,
            "context": context or {}
        }
        
        user_data["ai_context"]["conversation_history"].append(conversation_entry)
        
        # Keep only last 50 conversations to avoid database bloat
        if len(user_data["ai_context"]["conversation_history"]) > 50:
            user_data["ai_context"]["conversation_history"] = user_data["ai_context"]["conversation_history"][-50:]
        
        user_data["updated_at"] = datetime.utcnow().isoformat()
        
        User = Query()
        result = self.users_table.update(user_data, User.user_id == user_id)
        return len(result) > 0
    
    def _calculate_default_calories(self, profile_data: Dict[str, Any]) -> float:
        """Calculate default daily calorie target using Mifflin-St Jeor equation."""
        age = profile_data.get("age", 25)
        weight_kg = profile_data.get("weight_kg", 70)
        height_cm = profile_data.get("height_cm", 170)
        gender = profile_data.get("gender", "not_specified")
        activity_level = profile_data.get("activity_level", "moderately_active")
        
        # Base Metabolic Rate calculation
        if gender.lower() == "male":
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
        else:
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
        
        # Activity multipliers
        multipliers = {
            "sedentary": 1.2,
            "lightly_active": 1.375,
            "moderately_active": 1.55,
            "very_active": 1.725,
            "extremely_active": 1.9
        }
        
        return bmr * multipliers.get(activity_level, 1.55)
    
    def _recalculate_daily_totals(self, daily_log: Dict[str, Any]):
        """Recalculate daily totals for a nutrition log."""
        totals = {
            "calories": 0,
            "protein_g": 0,
            "carbs_g": 0,
            "fat_g": 0,
            "fiber_g": 0,
            "water_ml": 0
        }
        
        for meal in daily_log["meals"]:
            totals["calories"] += meal.get("total_calories", 0)
            meal_macros = meal.get("total_macros", {})
            totals["protein_g"] += meal_macros.get("protein_g", 0)
            totals["carbs_g"] += meal_macros.get("carbs_g", 0)
            totals["fat_g"] += meal_macros.get("fat_g", 0)
            totals["fiber_g"] += meal_macros.get("fiber_g", 0)
        
        daily_log["daily_totals"] = totals
    
    def close(self):
        """Close the database connection."""
        self.db.close()