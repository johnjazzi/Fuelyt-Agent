from pydantic import BaseModel, Field
from typing import List, Optional

# --- Tool Input Schemas ---

class LogWorkoutInput(BaseModel):
    user_id: str = Field(..., description="The ID of the user logging the workout.")
    workout_type: str = Field(..., description="The type of workout (e.g., 'run', 'lift', 'cycle').")
    duration_minutes: int = Field(..., description="The duration of the workout in minutes.")
    calories_burned: Optional[int] = Field(None, description="The number of calories burned during the workout.")
    notes: Optional[str] = Field(None, description="Any additional notes about the workout.")

class LogMealInput(BaseModel):
    user_id: str = Field(..., description="The ID of the user logging the meal.")
    meal_type: str = Field(..., description="The type of meal (e.g., 'breakfast', 'lunch', 'dinner', 'snack').")
    description: str = Field(..., description="A description of the meal.")
    calories: Optional[int] = Field(None, description="The estimated number of calories in the meal.")
    protein_g: Optional[int] = Field(None, description="The estimated grams of protein.")
    carbs_g: Optional[int] = Field(None, description="The estimated grams of carbohydrates.")
    fat_g: Optional[int] = Field(None, description="The estimated grams of fat.")

class CreateOrUpdateGoalInput(BaseModel):
    user_id: str = Field(..., description="The ID of the user whose goal is being updated.")
    primary_goal: Optional[str] = Field(None, description="The user's primary fitness goal (e.g., 'weight_loss', 'muscle_gain').")
    target_weight_kg: Optional[float] = Field(None, description="The user's target weight in kilograms.")
    daily_calorie_target: Optional[int] = Field(None, description="The user's daily calorie target.")

class UpdateUserProfileInput(BaseModel):
    user_id: str = Field(..., description="The ID of the user to update.")
    name: Optional[str] = Field(None, description="The user's name.")
    age: Optional[int] = Field(None, description="The user's age.")
    gender: Optional[str] = Field(None, description="The user's gender.")
    height_cm: Optional[float] = Field(None, description="The user's height in centimeters.")
    weight_kg: Optional[float] = Field(None, description="The user's weight in kilograms.")
    activity_level: Optional[str] = Field(None, description="The user's activity level.")
    sport: Optional[str] = Field(None, description="The user's primary sport.")
    experience_level: Optional[str] = Field(None, description="The user's experience level.")
    dietary_restrictions: Optional[List[str]] = Field(None, description="A list of dietary restrictions.")
    allergies: Optional[List[str]] = Field(None, description="A list of allergies.")

# --- Tool Functions ---

def log_workout(user_id: str, workout_type: str, duration_minutes: int, calories_burned: Optional[int] = None, notes: Optional[str] = None) -> str:
    """Logs a new workout for the user."""
    from .database_manager import db_manager
    user = db_manager.get_user(user_id)
    if not user:
        return f"Error: User with ID '{user_id}' not found."

    workout_data = {
        "workout_type": workout_type,
        "duration_minutes": duration_minutes,
        "calories_burned": calories_burned,
        "notes": notes,
    }
    
    user.workouts["logged_workouts"].append(workout_data)
    db_manager.update_user(user_id, {"workouts": user.workouts})
    return f"Successfully logged a {duration_minutes}-minute {workout_type} workout for user {user_id}."

def log_meal(user_id: str, meal_type: str, description: str, calories: Optional[int] = None, protein_g: Optional[int] = None, carbs_g: Optional[int] = None, fat_g: Optional[int] = None) -> str:
    """Logs a new meal for the user."""
    from .database_manager import db_manager
    user = db_manager.get_user(user_id)
    if not user:
        return f"Error: User with ID '{user_id}' not found."

    meal_data = {
        "meal_type": meal_type,
        "description": description,
        "calories": calories,
        "protein_g": protein_g,
        "carbs_g": carbs_g,
        "fat_g": fat_g,
    }

    user.nutrition["daily_logs"].append(meal_data)
    db_manager.update_user(user_id, {"nutrition": user.nutrition})
    return f"Successfully logged a {meal_type} for user {user_id}."

def create_or_update_goal(user_id: str, primary_goal: Optional[str] = None, target_weight_kg: Optional[float] = None, daily_calorie_target: Optional[int] = None) -> str:
    """Creates or updates a user's fitness goals."""
    from .database_manager import db_manager
    user = db_manager.get_user(user_id)
    if not user:
        return f"Error: User with ID '{user_id}' not found."

    if primary_goal:
        user.goals.primary_goal = primary_goal
    if target_weight_kg:
        user.goals.target_weight_kg = target_weight_kg
    if daily_calorie_target:
        user.goals.daily_calorie_target = daily_calorie_target
    
    db_manager.update_user(user_id, {"goals": user.goals.dict()})
    return f"Successfully updated goals for user {user_id}."

def update_user_profile(user_id: str, **kwargs) -> str:
    """Updates a user's profile information."""
    from .database_manager import db_manager
    user = db_manager.get_user(user_id)
    if not user:
        return f"Error: User with ID '{user_id}' not found."

    updated_fields = {k: v for k, v in kwargs.items() if v is not None}
    if not updated_fields:
        return "No profile fields to update."

    for key, value in updated_fields.items():
        setattr(user.profile, key, value)
    
    db_manager.update_user(user_id, {"profile": user.profile.dict()})
    return f"Successfully updated profile for user {user_id}."
