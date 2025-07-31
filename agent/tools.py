from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
import json

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

class ScheduleWorkoutInput(BaseModel):
    user_id: str = Field(..., description="The ID of the user for whom to schedule the workout.")
    workout_date: date = Field(..., description="The date of the workout.")
    time_of_day: str = Field(..., description="The time of day for the workout (e.g., 'morning', 'afternoon', 'evening').")
    workout_type: str = Field(..., description="The type of workout to schedule.")
    intensity: str = Field(..., description="The intensity of the workout (e.g., 'low', 'medium', 'high').")
    duration_minutes: Optional[int] = Field(None, description="The duration of the workout in minutes.")
    notes: Optional[str] = Field(None, description="Any additional notes for the workout.")

class ScheduleMealInput(BaseModel):
    user_id: str = Field(..., description="The ID of the user for whom to schedule the meal.")
    meal_date: date = Field(..., description="The date of the meal.")
    meal_type: str = Field(..., description="The type of meal to schedule (e.g., 'breakfast', 'lunch', 'dinner', 'snack').")
    description: str = Field(..., description="A description of the meal.")
    calories: Optional[int] = Field(None, description="The estimated number of calories in the meal.")

class GetScheduleInput(BaseModel):
    user_id: str = Field(..., description="The ID of the user whose schedule should be retrieved.")
    start_date: date = Field(..., description="The start date of the schedule to retrieve.")
    end_date: Optional[date] = Field(None, description="The end date of the schedule to retrieve. Defaults to the start date.")

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

def schedule_workout(user_id: str, workout_date: date, time_of_day: str, workout_type: str, intensity: str, duration_minutes: Optional[int] = None, notes: Optional[str] = None) -> str:
    """Schedules a new workout for the user."""
    from .database_manager import db_manager
    from .data_models import PlannedWorkout
    user = db_manager.get_user(user_id)
    if not user:
        return f"Error: User with ID '{user_id}' not found."

    planned_workout = PlannedWorkout(
        workout_date=workout_date,
        time_of_day=time_of_day,
        workout_type=workout_type,
        intensity=intensity,
        duration_minutes=duration_minutes,
        notes=notes,
    )
    
    user.calendar["scheduled_items"].append(planned_workout.dict())
    db_manager.update_user(user_id, {"calendar": user.calendar})
    return f"Successfully scheduled a {workout_type} workout for user {user_id} on {workout_date} in the {time_of_day}."

def schedule_meal(user_id: str, meal_date: date, meal_type: str, description: str, calories: Optional[int] = None) -> str:
    """Schedules a new meal for the user."""
    from .database_manager import db_manager
    from .data_models import PlannedMeal
    user = db_manager.get_user(user_id)
    if not user:
        return f"Error: User with ID '{user_id}' not found."

    planned_meal = PlannedMeal(
        meal_date=meal_date,
        meal_type=meal_type,
        description=description,
        calories=calories,
    )

    user.calendar["scheduled_items"].append(planned_meal.dict())
    db_manager.update_user(user_id, {"calendar": user.calendar})
    return f"Successfully scheduled a {meal_type} for user {user_id} on {meal_date}."

def get_schedule(user_id: str, start_date: date, end_date: Optional[date] = None) -> str:
    """Retrieves the user's schedule for a given date range."""
    from .database_manager import db_manager
    user = db_manager.get_user(user_id)
    if not user:
        return f"Error: User with ID '{user_id}' not found."

    if end_date is None:
        end_date = start_date

    schedule = [
        item for item in user.calendar.get("scheduled_items", [])
        if start_date <= date.fromisoformat(item["workout_date" if "workout_date" in item else "meal_date"]) <= end_date
    ]

    if not schedule:
        return f"No scheduled items found for user {user_id} between {start_date} and {end_date}."
    
    return json.dumps(schedule, default=str)
