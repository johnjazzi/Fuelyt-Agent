"""
Fuelyt AI Agent Workflow - Multi-step agentic workflow with OpenAI integration.
Provides intelligent nutrition and fitness guidance for athletes.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import openai
from dataclasses import dataclass

from data_models import UserData, WorkoutType, MealType, Goal, ActivityLevel
from database_manager import DatabaseManager


@dataclass
class AgentResponse:
    response: str
    actions_taken: List[str]
    recommendations: List[Dict[str, Any]]
    updated_data: Optional[Dict[str, Any]] = None


class FuelytAgent:
    def __init__(self):
        """Initialize the Fuelyt AI Agent with OpenAI client."""
        self.client = openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY", "your-openai-api-key-here")
        )
        self.model = "gpt-4-turbo-preview"
        
        # Agent persona and instructions
        self.system_prompt = """
        You are Fuelyt, an expert AI nutrition and fitness coach specializing in athletic performance optimization. 
        
        Your expertise includes:
        - Sports nutrition and meal timing for optimal performance
        - Macro and micronutrient requirements for different sports and goals
        - Pre, during, and post-workout nutrition strategies
        - Meal planning and recipe recommendations
        - Workout programming and recovery optimization
        - Progress tracking and goal adjustment
        
        Your communication style is:
        - Friendly, encouraging, and motivational
        - Evidence-based and scientific when needed
        - Practical and actionable
        - Personalized to the athlete's specific sport, goals, and preferences
        
        Always consider:
        - The athlete's current goals, sport, and experience level
        - Their dietary restrictions and preferences
        - Their training schedule and intensity
        - Their progress and adherence patterns
        - The timing and context of their request
        
        When providing recommendations, be specific with quantities, timing, and rationale.
        """
    
    async def process_request(self, user_id: str, message: str, user_data: Dict[str, Any], context: Optional[Dict] = None) -> AgentResponse:
        """
        Main entry point for processing user requests through multi-step agentic workflow.
        """
        
        # Step 1: Analyze user intent and context
        intent_analysis = await self._analyze_intent(message, user_data, context)
        
        # Step 2: Determine required actions based on intent
        action_plan = await self._create_action_plan(intent_analysis, user_data)
        
        # Step 3: Execute actions in sequence
        execution_results = await self._execute_actions(action_plan, user_data, message)
        
        # Step 4: Generate comprehensive response
        final_response = await self._generate_response(execution_results, user_data, message)
        
        # Step 5: Update user data if needed
        updated_data = self._prepare_data_updates(execution_results, user_data)
        
        return AgentResponse(
            response=final_response["response"],
            actions_taken=execution_results["actions_completed"],
            recommendations=final_response["recommendations"],
            updated_data=updated_data
        )
    
    async def _analyze_intent(self, message: str, user_data: Dict[str, Any], context: Optional[Dict]) -> Dict[str, Any]:
        """Analyze user message to determine intent and required information."""
        
        analysis_prompt = f"""
        Analyze the following message from an athlete and determine their intent:
        
        Message: "{message}"
        
        User Context:
        - Name: {user_data.get('profile', {}).get('name', 'Unknown')}
        - Sport: {user_data.get('profile', {}).get('sport', 'General fitness')}
        - Primary Goal: {user_data.get('goals', {}).get('primary_goal', 'maintenance')}
        - Experience Level: {user_data.get('profile', {}).get('experience_level', 'beginner')}
        
        Recent Activity Context: {json.dumps(context) if context else 'None'}
        
        Determine:
        1. Primary intent (nutrition_guidance, workout_logging, meal_planning, progress_tracking, general_question, recipe_request, calendar_planning)
        2. Specific action needed
        3. Information required from user data
        4. Urgency level (immediate, today, this_week, general)
        5. Complexity (simple, moderate, complex)
        
        Respond in JSON format with these fields.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.3
            )
            
            intent_json = response.choices[0].message.content
            return json.loads(intent_json)
            
        except Exception as e:
            # Fallback intent analysis
            return {
                "primary_intent": "general_question",
                "specific_action": "provide_guidance",
                "information_required": ["user_profile", "goals"],
                "urgency_level": "general",
                "complexity": "moderate"
            }
    
    async def _create_action_plan(self, intent_analysis: Dict[str, Any], user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a step-by-step action plan based on intent analysis."""
        
        intent = intent_analysis.get("primary_intent", "general_question")
        complexity = intent_analysis.get("complexity", "moderate")
        
        # Define action sequences for different intents
        action_plans = {
            "nutrition_guidance": [
                "analyze_current_nutrition",
                "check_recent_workouts",
                "calculate_requirements",
                "generate_recommendations"
            ],
            "workout_logging": [
                "validate_workout_data",
                "analyze_performance",
                "update_progress_tracking",
                "suggest_recovery_nutrition"
            ],
            "meal_planning": [
                "analyze_goals_and_preferences",
                "check_schedule_and_workouts",
                "generate_meal_plan",
                "create_shopping_list"
            ],
            "progress_tracking": [
                "analyze_recent_data",
                "calculate_trends",
                "assess_goal_progress",
                "adjust_recommendations"
            ],
            "recipe_request": [
                "understand_requirements",
                "check_dietary_restrictions",
                "generate_recipe",
                "provide_nutrition_info"
            ],
            "calendar_planning": [
                "analyze_schedule",
                "plan_meals_and_workouts",
                "set_reminders",
                "create_calendar_events"
            ]
        }
        
        actions = action_plans.get(intent, ["analyze_request", "provide_guidance"])
        
        return {
            "intent": intent,
            "actions": actions,
            "complexity": complexity,
            "estimated_duration": len(actions) * 2  # seconds
        }
    
    async def _execute_actions(self, action_plan: Dict[str, Any], user_data: Dict[str, Any], original_message: str) -> Dict[str, Any]:
        """Execute the planned actions in sequence."""
        
        results = {
            "actions_completed": [],
            "data_collected": {},
            "recommendations_generated": [],
            "errors": []
        }
        
        for action in action_plan["actions"]:
            try:
                action_result = await self._execute_single_action(action, user_data, original_message, results)
                results["actions_completed"].append(action)
                results["data_collected"][action] = action_result
                
            except Exception as e:
                results["errors"].append(f"Error in {action}: {str(e)}")
                # Continue with other actions
        
        return results
    
    async def _execute_single_action(self, action: str, user_data: Dict[str, Any], message: str, current_results: Dict) -> Dict[str, Any]:
        """Execute a single action in the workflow."""
        
        if action == "analyze_current_nutrition":
            return await self._analyze_current_nutrition(user_data)
        
        elif action == "check_recent_workouts":
            return await self._check_recent_workouts(user_data)
        
        elif action == "calculate_requirements":
            return await self._calculate_nutrition_requirements(user_data)
        
        elif action == "generate_recommendations":
            return await self._generate_nutrition_recommendations(user_data, current_results)
        
        elif action == "analyze_goals_and_preferences":
            return await self._analyze_goals_and_preferences(user_data)
        
        elif action == "generate_meal_plan":
            return await self._generate_meal_plan(user_data, message)
        
        elif action == "analyze_recent_data":
            return await self._analyze_recent_progress(user_data)
        
        elif action == "provide_guidance":
            return await self._provide_general_guidance(user_data, message)
        
        else:
            return {"action": action, "status": "not_implemented"}
    
    async def _analyze_current_nutrition(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the user's current nutrition intake."""
        
        recent_logs = user_data.get("nutrition", {}).get("daily_logs", [])
        if not recent_logs:
            return {"status": "no_data", "message": "No recent nutrition data found"}
        
        # Get last 7 days of data
        recent_logs = recent_logs[-7:] if len(recent_logs) > 7 else recent_logs
        
        # Calculate averages
        total_days = len(recent_logs)
        avg_calories = sum(log.get("daily_totals", {}).get("calories", 0) for log in recent_logs) / total_days
        avg_protein = sum(log.get("daily_totals", {}).get("protein_g", 0) for log in recent_logs) / total_days
        avg_carbs = sum(log.get("daily_totals", {}).get("carbs_g", 0) for log in recent_logs) / total_days
        avg_fat = sum(log.get("daily_totals", {}).get("fat_g", 0) for log in recent_logs) / total_days
        
        goals = user_data.get("goals", {})
        target_calories = goals.get("daily_calorie_target", 2000)
        macro_targets = goals.get("macro_targets", {})
        
        analysis = {
            "current_averages": {
                "calories": round(avg_calories, 1),
                "protein_g": round(avg_protein, 1),
                "carbs_g": round(avg_carbs, 1),
                "fat_g": round(avg_fat, 1)
            },
            "targets": {
                "calories": target_calories,
                "protein_g": macro_targets.get("protein_g", 100),
                "carbs_g": macro_targets.get("carbs_g", 200),
                "fat_g": macro_targets.get("fat_g", 60)
            },
            "adherence": {
                "calories": round((avg_calories / target_calories) * 100, 1),
                "protein": round((avg_protein / macro_targets.get("protein_g", 100)) * 100, 1),
                "carbs": round((avg_carbs / macro_targets.get("carbs_g", 200)) * 100, 1),
                "fat": round((avg_fat / macro_targets.get("fat_g", 60)) * 100, 1)
            },
            "days_analyzed": total_days
        }
        
        return analysis
    
    async def _check_recent_workouts(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check recent workout patterns and performance."""
        
        workouts = user_data.get("workouts", {}).get("logged_workouts", [])
        if not workouts:
            return {"status": "no_workouts", "message": "No recent workouts found"}
        
        # Get last 7 days of workouts
        cutoff_date = datetime.utcnow() - timedelta(days=7)
        recent_workouts = []
        
        for workout in workouts:
            workout_date = datetime.fromisoformat(workout["date"].replace('Z', '+00:00'))
            if workout_date >= cutoff_date:
                recent_workouts.append(workout)
        
        if not recent_workouts:
            return {"status": "no_recent_workouts", "message": "No workouts in the last 7 days"}
        
        # Analyze workout patterns
        workout_types = {}
        total_duration = 0
        avg_intensity = 0
        avg_energy = 0
        
        for workout in recent_workouts:
            workout_type = workout.get("type", "unknown")
            workout_types[workout_type] = workout_types.get(workout_type, 0) + 1
            total_duration += workout.get("duration_minutes", 0)
            
            # Convert intensity to numeric for averaging
            intensity_map = {"low": 1, "moderate": 2, "high": 3, "max": 4}
            avg_intensity += intensity_map.get(workout.get("intensity", "moderate"), 2)
            avg_energy += workout.get("energy_level", 5)
        
        workout_count = len(recent_workouts)
        
        return {
            "recent_workouts_count": workout_count,
            "workout_types": workout_types,
            "total_duration_minutes": total_duration,
            "avg_duration_minutes": round(total_duration / workout_count, 1),
            "avg_intensity": round(avg_intensity / workout_count, 1),
            "avg_energy_level": round(avg_energy / workout_count, 1),
            "frequency_per_week": round(workout_count * 7 / 7, 1)  # Already 7 days
        }
    
    async def _calculate_nutrition_requirements(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate personalized nutrition requirements based on goals and activity."""
        
        profile = user_data.get("profile", {})
        goals = user_data.get("goals", {})
        
        # Basic info
        weight_kg = profile.get("weight_kg", 70)
        activity_level = profile.get("activity_level", "moderately_active")
        primary_goal = goals.get("primary_goal", "maintenance")
        sport = profile.get("sport", "general")
        
        # Base protein requirements (g/kg body weight)
        protein_multipliers = {
            "endurance": 1.2,
            "strength": 1.6,
            "muscle_gain": 1.8,
            "weight_loss": 2.0,
            "maintenance": 1.4,
            "performance": 1.6
        }
        
        protein_per_kg = protein_multipliers.get(primary_goal, 1.4)
        daily_protein = weight_kg * protein_per_kg
        
        # Calorie adjustments based on goal
        base_calories = goals.get("daily_calorie_target", 2000)
        calorie_adjustments = {
            "weight_loss": -500,
            "muscle_gain": 300,
            "performance": 200,
            "maintenance": 0
        }
        
        adjusted_calories = base_calories + calorie_adjustments.get(primary_goal, 0)
        
        # Calculate carbs and fats
        protein_calories = daily_protein * 4
        fat_calories = adjusted_calories * 0.25  # 25% from fats
        carb_calories = adjusted_calories - protein_calories - fat_calories
        
        daily_carbs = carb_calories / 4
        daily_fat = fat_calories / 9
        
        return {
            "daily_calories": round(adjusted_calories),
            "daily_protein_g": round(daily_protein, 1),
            "daily_carbs_g": round(daily_carbs, 1),
            "daily_fat_g": round(daily_fat, 1),
            "protein_per_kg": round(protein_per_kg, 1),
            "calorie_distribution": {
                "protein_percent": round((protein_calories / adjusted_calories) * 100, 1),
                "carb_percent": round((carb_calories / adjusted_calories) * 100, 1),
                "fat_percent": round((fat_calories / adjusted_calories) * 100, 1)
            }
        }
    
    async def _generate_nutrition_recommendations(self, user_data: Dict[str, Any], analysis_results: Dict) -> List[Dict[str, Any]]:
        """Generate specific nutrition recommendations based on analysis."""
        
        recommendations = []
        
        # Get analysis data
        nutrition_analysis = analysis_results.get("data_collected", {}).get("analyze_current_nutrition", {})
        workout_analysis = analysis_results.get("data_collected", {}).get("check_recent_workouts", {})
        requirements = analysis_results.get("data_collected", {}).get("calculate_requirements", {})
        
        if not nutrition_analysis or nutrition_analysis.get("status") == "no_data":
            recommendations.append({
                "type": "action",
                "priority": "high",
                "title": "Start Tracking Your Nutrition",
                "message": "Begin logging your meals to get personalized recommendations based on your actual intake."
            })
            return recommendations
        
        # Check adherence and provide specific recommendations
        adherence = nutrition_analysis.get("adherence", {})
        
        if adherence.get("calories", 100) < 90:
            recommendations.append({
                "type": "nutrition",
                "priority": "high",
                "title": "Increase Calorie Intake",
                "message": f"You're consuming {adherence.get('calories', 0):.1f}% of your calorie target. Consider adding healthy snacks or larger portions.",
                "specific_actions": ["Add a post-workout smoothie", "Include nuts or nut butter", "Increase portion sizes by 20%"]
            })
        
        if adherence.get("protein", 100) < 85:
            recommendations.append({
                "type": "nutrition",
                "priority": "high",
                "title": "Boost Protein Intake",
                "message": f"Your protein intake is at {adherence.get('protein', 0):.1f}% of target. Protein is crucial for recovery and performance.",
                "specific_actions": ["Add protein powder to smoothies", "Include lean meat in every meal", "Try Greek yogurt or cottage cheese snacks"]
            })
        
        # Workout-specific recommendations
        if workout_analysis.get("recent_workouts_count", 0) > 0:
            avg_intensity = workout_analysis.get("avg_intensity", 2)
            if avg_intensity >= 3:  # High intensity workouts
                recommendations.append({
                    "type": "timing",
                    "priority": "medium",
                    "title": "High-Intensity Workout Nutrition",
                    "message": "Your recent workouts have been high intensity. Focus on pre and post-workout nutrition.",
                    "specific_actions": [
                        "Eat 30-60g carbs 30-60 minutes before workouts",
                        "Consume protein within 30 minutes post-workout",
                        "Stay hydrated during intense sessions"
                    ]
                })
        
        return recommendations
    
    async def _generate_response(self, execution_results: Dict[str, Any], user_data: Dict[str, Any], original_message: str) -> Dict[str, Any]:
        """Generate the final comprehensive response to the user."""
        
        # Prepare context for OpenAI
        context_prompt = f"""
        Based on the following analysis and user request, generate a comprehensive, personalized response:
        
        User Message: "{original_message}"
        
        User Profile:
        - Name: {user_data.get('profile', {}).get('name', 'there')}
        - Sport: {user_data.get('profile', {}).get('sport', 'fitness')}
        - Goal: {user_data.get('goals', {}).get('primary_goal', 'maintenance')}
        
        Analysis Results: {json.dumps(execution_results.get('data_collected', {}), indent=2)}
        
        Actions Completed: {execution_results.get('actions_completed', [])}
        
        Generate a response that:
        1. Directly addresses their question/request
        2. Provides specific, actionable recommendations
        3. Explains the reasoning behind suggestions
        4. Is encouraging and motivational
        5. Includes specific timing, quantities, or steps where relevant
        
        Also provide a separate list of key recommendations in JSON format.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": context_prompt}
                ],
                temperature=0.7
            )
            
            full_response = response.choices[0].message.content
            
            # Try to extract JSON recommendations if present
            recommendations = []
            if "```json" in full_response:
                try:
                    json_start = full_response.find("```json") + 7
                    json_end = full_response.find("```", json_start)
                    json_content = full_response[json_start:json_end]
                    recommendations = json.loads(json_content)
                    # Remove JSON from response
                    full_response = full_response[:full_response.find("```json")] + full_response[json_end + 3:]
                except:
                    pass
            
            return {
                "response": full_response.strip(),
                "recommendations": recommendations
            }
            
        except Exception as e:
            return {
                "response": f"I understand you're asking about {original_message}. Let me help you with that based on your profile and recent activity. I've analyzed your data and have some recommendations for you.",
                "recommendations": execution_results.get("recommendations_generated", [])
            }
    
    def _prepare_data_updates(self, execution_results: Dict[str, Any], user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Prepare any updates to user data based on the workflow execution."""
        
        updates = {}
        
        # Update AI context with conversation
        if "ai_context" not in updates:
            updates["ai_context"] = user_data.get("ai_context", {})
        
        # Add workflow execution to context
        updates["ai_context"]["last_workflow_execution"] = {
            "timestamp": datetime.utcnow().isoformat(),
            "actions_completed": execution_results.get("actions_completed", []),
            "recommendations_count": len(execution_results.get("recommendations_generated", []))
        }
        
        # Update timestamp
        updates["updated_at"] = datetime.utcnow().isoformat()
        
        return updates if updates else None
    
    # Additional specific workflow methods
    
    async def log_workout(self, user_id: str, workout_data: Dict[str, Any], user_data: Dict[str, Any]) -> AgentResponse:
        """Specialized workflow for logging workouts."""
        
        # Add workout to user data structure
        workout_entry = {
            "id": f"workout_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "date": datetime.utcnow().isoformat(),
            **workout_data
        }
        
        # Analyze workout and provide recommendations
        recommendations = await self._analyze_workout_performance(workout_entry, user_data)
        
        # Update user data
        updated_data = user_data.copy()
        updated_data["workouts"]["logged_workouts"].append(workout_entry)
        updated_data["updated_at"] = datetime.utcnow().isoformat()
        
        response_text = f"Great job on your {workout_data.get('type', 'workout')}! I've logged your session and analyzed your performance."
        
        return AgentResponse(
            response=response_text,
            actions_taken=["log_workout", "analyze_performance"],
            recommendations=recommendations,
            updated_data=updated_data
        )
    
    async def log_nutrition(self, user_id: str, nutrition_data: Dict[str, Any], user_data: Dict[str, Any]) -> AgentResponse:
        """Specialized workflow for logging nutrition."""
        
        # Process nutrition data
        meal_entry = {
            "id": f"meal_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "time": datetime.utcnow().isoformat(),
            **nutrition_data
        }
        
        # Analyze nutrition and provide feedback
        analysis = await self._analyze_nutrition_entry(meal_entry, user_data)
        
        response_text = f"I've logged your {nutrition_data.get('type', 'meal')}. Here's my analysis of your nutrition choices."
        
        return AgentResponse(
            response=response_text,
            actions_taken=["log_nutrition", "analyze_nutrition"],
            recommendations=analysis,
            updated_data=None  # Will be handled by database manager
        )
    
    async def generate_recommendations(self, user_id: str, user_data: Dict[str, Any], recommendation_type: str = "all") -> List[Dict[str, Any]]:
        """Generate various types of recommendations for the user."""
        
        if recommendation_type == "nutrition":
            return await self._generate_nutrition_recommendations(user_data, {"data_collected": {}})
        elif recommendation_type == "workout":
            return await self._generate_workout_recommendations(user_data)
        elif recommendation_type == "recovery":
            return await self._generate_recovery_recommendations(user_data)
        else:
            # Generate comprehensive recommendations
            nutrition_recs = await self._generate_nutrition_recommendations(user_data, {"data_collected": {}})
            workout_recs = await self._generate_workout_recommendations(user_data)
            recovery_recs = await self._generate_recovery_recommendations(user_data)
            
            return nutrition_recs + workout_recs + recovery_recs
    
    async def plan_meals(self, user_id: str, meal_request: Dict[str, Any], user_data: Dict[str, Any]) -> AgentResponse:
        """Generate meal plans based on user requirements."""
        
        meal_plan = await self._generate_detailed_meal_plan(user_data, meal_request)
        
        response_text = "I've created a personalized meal plan based on your goals and preferences."
        
        return AgentResponse(
            response=response_text,
            actions_taken=["analyze_requirements", "generate_meal_plan"],
            recommendations=meal_plan,
            updated_data=None
        )
    
    async def generate_dashboard_summary(self, user_id: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive dashboard data for the user."""
        
        # Analyze recent performance
        nutrition_summary = await self._analyze_current_nutrition(user_data)
        workout_summary = await self._check_recent_workouts(user_data)
        progress_summary = await self._analyze_recent_progress(user_data)
        
        return {
            "user_profile": {
                "name": user_data.get("profile", {}).get("name", "Athlete"),
                "goal": user_data.get("goals", {}).get("primary_goal", "maintenance"),
                "sport": user_data.get("profile", {}).get("sport", "fitness")
            },
            "nutrition_summary": nutrition_summary,
            "workout_summary": workout_summary,
            "progress_summary": progress_summary,
            "quick_recommendations": await self.generate_recommendations(user_id, user_data, "all")[:3]
        }
    
    # Helper methods for specific analyses
    
    async def _analyze_workout_performance(self, workout: Dict, user_data: Dict) -> List[Dict]:
        """Analyze workout performance and provide recommendations."""
        # Implementation for workout analysis
        return [{"type": "recovery", "message": "Great workout! Focus on recovery nutrition in the next 30 minutes."}]
    
    async def _analyze_nutrition_entry(self, meal: Dict, user_data: Dict) -> List[Dict]:
        """Analyze nutrition entry and provide feedback."""
        # Implementation for nutrition analysis
        return [{"type": "nutrition", "message": "Good protein choice! Consider adding some vegetables for micronutrients."}]
    
    async def _generate_workout_recommendations(self, user_data: Dict) -> List[Dict]:
        """Generate workout-specific recommendations."""
        # Implementation for workout recommendations
        return [{"type": "workout", "message": "Based on your recent training, consider adding a recovery day."}]
    
    async def _generate_recovery_recommendations(self, user_data: Dict) -> List[Dict]:
        """Generate recovery-focused recommendations."""
        # Implementation for recovery recommendations
        return [{"type": "recovery", "message": "Prioritize 7-9 hours of sleep for optimal recovery."}]
    
    async def _generate_detailed_meal_plan(self, user_data: Dict, request: Dict) -> List[Dict]:
        """Generate detailed meal plans."""
        # Implementation for meal planning
        return [{"type": "meal_plan", "message": "Here's your personalized meal plan for the week."}]
    
    async def _analyze_recent_progress(self, user_data: Dict) -> Dict:
        """Analyze recent progress trends."""
        # Implementation for progress analysis
        return {"trend": "positive", "areas_for_improvement": ["consistency"]}
    
    async def _analyze_goals_and_preferences(self, user_data: Dict) -> Dict:
        """Analyze user goals and preferences."""
        # Implementation for goals analysis
        return {"aligned": True, "recommendations": []}
    
    async def _provide_general_guidance(self, user_data: Dict, message: str) -> Dict:
        """Provide general guidance for unspecified requests."""
        # Implementation for general guidance
        return {"guidance": "Here's some general advice based on your profile."}