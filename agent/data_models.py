from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import date

class Profile(BaseModel):
    name: str
    age: int
    gender: str
    height_cm: float
    weight_kg: float
    activity_level: Optional[str] = None
    sport: Optional[str] = None
    experience_level: Optional[str] = None
    dietary_restrictions: List[str] = []
    allergies: List[str] = []

class MacroTargets(BaseModel):
    protein_g: float
    carbs_g: float
    fat_g: float

class Goals(BaseModel):
    primary_goal: str
    target_weight_kg: Optional[float] = None
    daily_calorie_target: Optional[float] = None
    macro_targets: Optional[MacroTargets] = None

class PlannedWorkout(BaseModel):
    workout_date: date
    time_of_day: str  # E.g., "morning", "afternoon", "evening"
    workout_type: str
    intensity: str  # E.g., "low", "medium", "high"
    duration_minutes: Optional[int] = None
    notes: Optional[str] = None

class PlannedMeal(BaseModel):
    meal_date: date
    meal_type: str  # E.g., "breakfast", "lunch", "dinner", "snack"
    description: str
    calories: Optional[int] = None

class User(BaseModel):
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    profile: Profile
    goals: Goals
    workouts: Dict[str, List[Any]] = Field(default_factory=lambda: {"logged_workouts": [], "planned_workouts": []})
    nutrition: Dict[str, List[Any]] = Field(default_factory=lambda: {"daily_logs": [], "favorite_foods": [], "meal_plans": []})
    recipes: Dict[str, List[Any]] = Field(default_factory=lambda: {"saved_recipes": []})
    calendar: Dict[str, List[Any]] = Field(default_factory=lambda: {"scheduled_items": []})
    progress_tracking: Dict[str, List[Any]] = Field(default_factory=lambda: {"body_measurements": [], "performance_metrics": [], "energy_mood_tracking": []})
    ai_context: Dict[str, Any] = Field(default_factory=lambda: {"conversation_history": [], "preferences_learned": {}})

class ChatMessage(BaseModel):
    user_id: str
    message: str
