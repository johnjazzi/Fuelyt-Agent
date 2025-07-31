"""
Utility functions for the Fuelyt AI Agent.
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import re

from config import Config


def generate_unique_id(prefix: str = "") -> str:
    """Generate a unique ID with optional prefix."""
    unique_id = str(uuid.uuid4())[:8]
    timestamp = datetime.utcnow().strftime("%Y%m%d")
    return f"{prefix}_{timestamp}_{unique_id}" if prefix else f"{timestamp}_{unique_id}"


def calculate_nutrition_totals(foods: List[Dict[str, Any]]) -> Dict[str, float]:
    """Calculate total nutrition values from a list of foods."""
    totals = {
        "calories": 0.0,
        "protein_g": 0.0,
        "carbs_g": 0.0,
        "fat_g": 0.0,
        "fiber_g": 0.0,
        "sugar_g": 0.0,
        "sodium_mg": 0.0
    }
    
    for food in foods:
        macros = food.get("macros", {})
        totals["calories"] += food.get("calories", 0)
        totals["protein_g"] += macros.get("protein_g", 0)
        totals["carbs_g"] += macros.get("carbs_g", 0)
        totals["fat_g"] += macros.get("fat_g", 0)
        totals["fiber_g"] += macros.get("fiber_g", 0)
        totals["sugar_g"] += macros.get("sugar_g", 0)
        totals["sodium_mg"] += macros.get("sodium_mg", 0)
    
    return totals


def calculate_workout_calories(exercise_data: List[Dict[str, Any]], user_weight_kg: float) -> float:
    """Estimate calories burned during workout based on exercises and user weight."""
    
    # METs (Metabolic Equivalent of Task) values for common exercises
    mets_values = {
        "running": 8.0,
        "cycling": 6.0,
        "swimming": 7.0,
        "weightlifting": 3.5,
        "yoga": 2.5,
        "walking": 3.0,
        "rowing": 7.0,
        "elliptical": 5.0,
        "basketball": 6.5,
        "soccer": 7.0,
        "tennis": 5.0,
        "climbing": 8.0,
        "dancing": 4.5,
        "hiking": 4.0
    }
    
    total_calories = 0.0
    
    for exercise in exercise_data:
        exercise_name = exercise.get("name", "").lower()
        duration_minutes = exercise.get("duration_minutes", 0)
        
        # Find matching METs value
        mets = 3.5  # Default moderate activity
        for activity, met_value in mets_values.items():
            if activity in exercise_name:
                mets = met_value
                break
        
        # Calories = METs × weight (kg) × time (hours)
        calories = mets * user_weight_kg * (duration_minutes / 60)
        total_calories += calories
    
    return round(total_calories, 1)


def get_meal_timing_recommendations(workout_time: datetime, meal_type: str) -> Dict[str, Any]:
    """Get meal timing recommendations relative to workout."""
    
    recommendations = {
        "pre_workout": {
            "timing_minutes": 60,
            "focus": "easily digestible carbs with minimal fat and fiber",
            "examples": ["banana with honey", "oatmeal", "toast with jam"]
        },
        "during_workout": {
            "timing_minutes": 0,
            "focus": "quick carbs and electrolytes for sessions >60 minutes",
            "examples": ["sports drink", "banana", "energy gels"]
        },
        "post_workout": {
            "timing_minutes": 30,
            "focus": "protein and carbs for recovery",
            "examples": ["protein smoothie", "chocolate milk", "turkey sandwich"]
        }
    }
    
    return recommendations.get(meal_type, recommendations["post_workout"])


def assess_nutrition_adherence(current: Dict[str, float], targets: Dict[str, float]) -> Dict[str, Any]:
    """Assess how well current nutrition aligns with targets."""
    
    adherence = {}
    for nutrient in ["calories", "protein_g", "carbs_g", "fat_g"]:
        current_value = current.get(nutrient, 0)
        target_value = targets.get(nutrient, 1)  # Avoid division by zero
        
        percentage = (current_value / target_value) * 100 if target_value > 0 else 0
        adherence[nutrient] = {
            "percentage": round(percentage, 1),
            "difference": round(current_value - target_value, 1),
            "status": get_adherence_status(percentage)
        }
    
    # Overall adherence score
    avg_adherence = sum(adherence[nutrient]["percentage"] for nutrient in adherence) / len(adherence)
    adherence["overall"] = {
        "score": round(avg_adherence, 1),
        "grade": get_adherence_grade(avg_adherence)
    }
    
    return adherence


def get_adherence_status(percentage: float) -> str:
    """Get status description for adherence percentage."""
    if percentage >= 95:
        return "excellent"
    elif percentage >= 85:
        return "good"
    elif percentage >= 75:
        return "fair"
    elif percentage >= 60:
        return "needs_improvement"
    else:
        return "poor"


def get_adherence_grade(percentage: float) -> str:
    """Get letter grade for adherence percentage."""
    if percentage >= 95:
        return "A+"
    elif percentage >= 90:
        return "A"
    elif percentage >= 85:
        return "B+"
    elif percentage >= 80:
        return "B"
    elif percentage >= 75:
        return "C+"
    elif percentage >= 70:
        return "C"
    elif percentage >= 65:
        return "D"
    else:
        return "F"


def parse_food_description(description: str) -> Dict[str, Any]:
    """Parse natural language food description into structured data."""
    
    # Extract quantity and unit using regex
    quantity_pattern = r'(\d+(?:\.\d+)?)\s*(\w+)?'
    match = re.search(quantity_pattern, description)
    
    if match:
        quantity = float(match.group(1))
        unit = match.group(2) or "serving"
    else:
        quantity = 1.0
        unit = "serving"
    
    # Extract food name (remove quantity and unit)
    food_name = re.sub(quantity_pattern, '', description).strip()
    food_name = food_name.strip(',.- ')
    
    return {
        "name": food_name,
        "quantity": quantity,
        "unit": unit
    }


def format_nutrition_summary(nutrition_data: Dict[str, Any]) -> str:
    """Format nutrition data into a readable summary."""
    
    summary_parts = []
    
    if "calories" in nutrition_data:
        summary_parts.append(f"{nutrition_data['calories']:.0f} calories")
    
    macros = []
    if "protein_g" in nutrition_data:
        macros.append(f"{nutrition_data['protein_g']:.1f}g protein")
    if "carbs_g" in nutrition_data:
        macros.append(f"{nutrition_data['carbs_g']:.1f}g carbs")
    if "fat_g" in nutrition_data:
        macros.append(f"{nutrition_data['fat_g']:.1f}g fat")
    
    if macros:
        summary_parts.append(" | ".join(macros))
    
    return " • ".join(summary_parts)


def get_hydration_recommendations(
    workout_duration_minutes: int,
    intensity: str,
    environmental_temp: str = "moderate"
) -> Dict[str, Any]:
    """Get hydration recommendations based on workout parameters."""
    
    base_fluid_ml = 150  # ml per 15 minutes of exercise
    intensity_multipliers = {
        "low": 1.0,
        "moderate": 1.2,
        "high": 1.5,
        "max": 1.8
    }
    
    temp_multipliers = {
        "cold": 0.8,
        "moderate": 1.0,
        "hot": 1.3,
        "extreme": 1.5
    }
    
    intensity_mult = intensity_multipliers.get(intensity, 1.2)
    temp_mult = temp_multipliers.get(environmental_temp, 1.0)
    
    total_fluid_ml = (workout_duration_minutes / 15) * base_fluid_ml * intensity_mult * temp_mult
    
    return {
        "total_fluid_ml": round(total_fluid_ml),
        "pre_workout_ml": round(total_fluid_ml * 0.3),
        "during_workout_ml": round(total_fluid_ml * 0.5),
        "post_workout_ml": round(total_fluid_ml * 0.2),
        "recommendations": [
            "Start hydrating 2-3 hours before exercise",
            "Drink 150-250ml every 15-20 minutes during exercise",
            "Monitor urine color for hydration status",
            "Add electrolytes for sessions >60 minutes"
        ]
    }


def validate_user_data(user_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate user data structure and required fields."""
    
    errors = []
    
    # Check required top-level fields
    required_fields = ["user_id", "profile", "goals"]
    for field in required_fields:
        if field not in user_data:
            errors.append(f"Missing required field: {field}")
    
    # Validate profile data
    if "profile" in user_data:
        profile = user_data["profile"]
        profile_required = ["name", "age", "weight_kg", "height_cm"]
        for field in profile_required:
            if field not in profile:
                errors.append(f"Missing profile field: {field}")
        
        # Validate data types and ranges
        if "age" in profile and (not isinstance(profile["age"], int) or profile["age"] < 13 or profile["age"] > 100):
            errors.append("Age must be between 13 and 100")
        
        if "weight_kg" in profile and (not isinstance(profile["weight_kg"], (int, float)) or profile["weight_kg"] < 30 or profile["weight_kg"] > 300):
            errors.append("Weight must be between 30 and 300 kg")
    
    # Validate goals data
    if "goals" in user_data:
        goals = user_data["goals"]
        if "primary_goal" not in goals:
            errors.append("Missing primary goal")
        
        valid_goals = ["weight_loss", "muscle_gain", "endurance", "strength", "maintenance", "performance"]
        if goals.get("primary_goal") not in valid_goals:
            errors.append(f"Primary goal must be one of: {', '.join(valid_goals)}")
    
    return len(errors) == 0, errors


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """Sanitize user input text."""
    if not isinstance(text, str):
        return ""
    
    # Remove potentially harmful characters
    sanitized = re.sub(r'[<>"\']', '', text)
    
    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + "..."
    
    return sanitized.strip()


def format_datetime_for_display(dt: datetime) -> str:
    """Format datetime for user-friendly display."""
    now = datetime.utcnow()
    diff = now - dt
    
    if diff.days == 0:
        return "Today"
    elif diff.days == 1:
        return "Yesterday"
    elif diff.days < 7:
        return f"{diff.days} days ago"
    else:
        return dt.strftime("%B %d, %Y")


def calculate_progress_trends(data_points: List[Dict[str, Any]], metric: str) -> Dict[str, Any]:
    """Calculate trends for progress tracking metrics."""
    
    if len(data_points) < 2:
        return {"trend": "insufficient_data", "change": 0, "direction": "stable"}
    
    # Sort by date
    sorted_data = sorted(data_points, key=lambda x: x.get("date", ""))
    
    # Get recent values
    recent_values = [point.get(metric, 0) for point in sorted_data[-5:]]
    older_values = [point.get(metric, 0) for point in sorted_data[-10:-5]] if len(sorted_data) >= 10 else []
    
    if not recent_values:
        return {"trend": "no_data", "change": 0, "direction": "stable"}
    
    recent_avg = sum(recent_values) / len(recent_values)
    
    if older_values:
        older_avg = sum(older_values) / len(older_values)
        change = recent_avg - older_avg
        change_percentage = (change / older_avg * 100) if older_avg != 0 else 0
    else:
        change = 0
        change_percentage = 0
    
    # Determine direction
    if abs(change_percentage) < 2:
        direction = "stable"
    elif change_percentage > 0:
        direction = "increasing"
    else:
        direction = "decreasing"
    
    return {
        "trend": direction,
        "change": round(change, 2),
        "change_percentage": round(change_percentage, 1),
        "recent_average": round(recent_avg, 2),
        "direction": direction
    }