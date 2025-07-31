"""
Data models and validation schemas for the Fuelyt AI Agent.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, validator
from enum import Enum


class ActivityLevel(str, Enum):
    SEDENTARY = "sedentary"
    LIGHTLY_ACTIVE = "lightly_active"
    MODERATELY_ACTIVE = "moderately_active"
    VERY_ACTIVE = "very_active"
    EXTREMELY_ACTIVE = "extremely_active"


class Goal(str, Enum):
    WEIGHT_LOSS = "weight_loss"
    MUSCLE_GAIN = "muscle_gain"
    ENDURANCE = "endurance"
    STRENGTH = "strength"
    MAINTENANCE = "maintenance"
    PERFORMANCE = "performance"


class WorkoutType(str, Enum):
    CARDIO = "cardio"
    STRENGTH = "strength"
    FLEXIBILITY = "flexibility"
    SPORT_SPECIFIC = "sport_specific"
    RECOVERY = "recovery"


class MealType(str, Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"
    PRE_WORKOUT = "pre_workout"
    POST_WORKOUT = "post_workout"
    DURING_WORKOUT = "during_workout"


class Macros(BaseModel):
    protein_g: float = 0.0
    carbs_g: float = 0.0
    fat_g: float = 0.0
    fiber_g: float = 0.0


class UserProfile(BaseModel):
    name: str
    age: int
    gender: str
    height_cm: float
    weight_kg: float
    activity_level: ActivityLevel
    sport: Optional[str] = None
    experience_level: str = "beginner"
    dietary_restrictions: List[str] = []
    allergies: List[str] = []


class Goals(BaseModel):
    primary_goal: Goal
    target_weight_kg: Optional[float] = None
    target_body_fat_percentage: Optional[float] = None
    performance_goals: List[str] = []
    timeline: Optional[str] = None
    daily_calorie_target: Optional[float] = None
    macro_targets: Optional[Macros] = None


class Food(BaseModel):
    name: str
    quantity: float
    unit: str
    calories: float
    macros: Macros
    micronutrients: Optional[Dict[str, float]] = {}


class Meal(BaseModel):
    id: str
    type: MealType
    time: datetime
    foods: List[Food]
    total_calories: float = 0.0
    total_macros: Optional[Macros] = None


class Exercise(BaseModel):
    name: str
    sets: Optional[int] = None
    reps: Optional[int] = None
    weight_kg: Optional[float] = None
    duration_minutes: Optional[float] = None
    distance_km: Optional[float] = None
    calories_burned: Optional[float] = None


class Workout(BaseModel):
    id: str
    date: datetime
    type: WorkoutType
    duration_minutes: float
    intensity: str
    exercises: List[Exercise]
    energy_level: Optional[int] = Field(None, ge=1, le=10)
    recovery_rating: Optional[int] = Field(None, ge=1, le=10)
    performance_notes: Optional[str] = None


class NutritionDay(BaseModel):
    date: datetime
    meals: List[Meal]
    daily_totals: Macros
    water_ml: float = 0.0


class UserData(BaseModel):
    user_id: str
    profile: UserProfile
    goals: Goals
    workouts: List[Workout] = []
    nutrition_logs: List[NutritionDay] = []
    created_at: datetime
    updated_at: datetime


# Request models for API endpoints
class WorkoutRequest(BaseModel):
    type: WorkoutType
    duration_minutes: float
    intensity: str
    exercises: List[Dict[str, Any]]
    notes: Optional[str] = None


class NutritionRequest(BaseModel):
    meal_type: MealType
    foods: List[Dict[str, Any]]
    time: Optional[datetime] = None


class RecommendationRequest(BaseModel):
    type: str  # "nutrition", "workout", "meal_plan", "recipes"
    context: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None