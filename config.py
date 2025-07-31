"""
Configuration settings for the Fuelyt AI Agent.
"""

import os
from typing import Dict, Any

class Config:
    """Configuration class for the Fuelyt AI Agent."""
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
    
    # Database Configuration
    DATABASE_PATH = os.getenv("DATABASE_PATH", "fuelyt_data.json")
    
    # API Configuration
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    
    # Agent Configuration
    MAX_CONVERSATION_HISTORY = int(os.getenv("MAX_CONVERSATION_HISTORY", "50"))
    MAX_RECOMMENDATIONS = int(os.getenv("MAX_RECOMMENDATIONS", "10"))
    
    # Nutrition Calculation Constants
    PROTEIN_CALORIES_PER_GRAM = 4
    CARB_CALORIES_PER_GRAM = 4
    FAT_CALORIES_PER_GRAM = 9
    
    # Default Macro Ratios by Goal
    MACRO_RATIOS: Dict[str, Dict[str, float]] = {
        "weight_loss": {"protein": 0.30, "carbs": 0.40, "fat": 0.30},
        "muscle_gain": {"protein": 0.25, "carbs": 0.45, "fat": 0.30},
        "endurance": {"protein": 0.15, "carbs": 0.65, "fat": 0.20},
        "strength": {"protein": 0.25, "carbs": 0.45, "fat": 0.30},
        "maintenance": {"protein": 0.20, "carbs": 0.50, "fat": 0.30},
        "performance": {"protein": 0.20, "carbs": 0.55, "fat": 0.25}
    }
    
    # Activity Multipliers for Calorie Calculation
    ACTIVITY_MULTIPLIERS: Dict[str, float] = {
        "sedentary": 1.2,
        "lightly_active": 1.375,
        "moderately_active": 1.55,
        "very_active": 1.725,
        "extremely_active": 1.9
    }
    
    # Protein Requirements (g/kg body weight) by Goal
    PROTEIN_REQUIREMENTS: Dict[str, float] = {
        "weight_loss": 2.0,
        "muscle_gain": 1.8,
        "endurance": 1.2,
        "strength": 1.6,
        "maintenance": 1.4,
        "performance": 1.6
    }
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate that required configuration is present."""
        if not cls.OPENAI_API_KEY:
            print("Warning: OPENAI_API_KEY not set. Add it to your environment variables.")
            return False
        return True
    
    @classmethod
    def get_macro_targets(cls, goal: str, total_calories: float) -> Dict[str, float]:
        """Calculate macro targets based on goal and total calories."""
        ratios = cls.MACRO_RATIOS.get(goal, cls.MACRO_RATIOS["maintenance"])
        
        protein_calories = total_calories * ratios["protein"]
        carb_calories = total_calories * ratios["carbs"]
        fat_calories = total_calories * ratios["fat"]
        
        return {
            "protein_g": protein_calories / cls.PROTEIN_CALORIES_PER_GRAM,
            "carbs_g": carb_calories / cls.CARB_CALORIES_PER_GRAM,
            "fat_g": fat_calories / cls.FAT_CALORIES_PER_GRAM
        }
    
    @classmethod
    def calculate_bmr(cls, weight_kg: float, height_cm: float, age: int, gender: str) -> float:
        """Calculate Basal Metabolic Rate using Mifflin-St Jeor equation."""
        if gender.lower() == "male":
            return 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
        else:
            return 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
    
    @classmethod
    def calculate_tdee(cls, bmr: float, activity_level: str) -> float:
        """Calculate Total Daily Energy Expenditure."""
        multiplier = cls.ACTIVITY_MULTIPLIERS.get(activity_level, 1.55)
        return bmr * multiplier


# Environment-specific configurations
class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True
    DATABASE_PATH = "dev_fuelyt_data.json"


class ProductionConfig(Config):
    """Production environment configuration."""
    DEBUG = False
    # Use environment variables for production settings


class TestConfig(Config):
    """Test environment configuration."""
    DATABASE_PATH = "test_fuelyt_data.json"
    OPENAI_API_KEY = "test-key"  # For testing without actual API calls


# Configuration factory
def get_config(env: str = None) -> Config:
    """Get configuration based on environment."""
    env = env or os.getenv("ENVIRONMENT", "development")
    
    configs = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "test": TestConfig
    }
    
    return configs.get(env, DevelopmentConfig)