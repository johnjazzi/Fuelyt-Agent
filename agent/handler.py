"""
Fuelyt AI Agent Serverless Handler
Multi-step agentic workflow using LangChain for AWS Lambda or similar serverless platforms.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain

# Import our existing modules
import sys
sys.path.append('..')
from database_manager import DatabaseManager
from config import Config
from utils import generate_unique_id, calculate_nutrition_totals, assess_nutrition_adherence


@dataclass
class AgentResponse:
    response: str
    actions_taken: List[str]
    recommendations: List[Dict[str, Any]]
    updated_data: Optional[Dict[str, Any]] = None


class FuelytAgentHandler:
    """Serverless handler for the Fuelyt AI Agent using LangChain."""
    
    def __init__(self):
        """Initialize the agent with LangChain components."""
        
        # Initialize LangChain ChatOpenAI
        self.llm = ChatOpenAI(
            model_name=Config.OPENAI_MODEL,
            temperature=Config.OPENAI_TEMPERATURE,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Initialize database manager
        self.db_manager = DatabaseManager()
        
        # System prompt for the agent
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
        Format your response clearly and include actionable steps.
        """
        
        # Create the conversation chain
        self.conversation_chain = self._create_conversation_chain()
    
    def _create_conversation_chain(self) -> LLMChain:
        """Create a LangChain conversation chain with memory."""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])
        
        memory = ConversationBufferMemory(
            chat_memory=None,  # We'll manage this ourselves
            return_messages=True,
            memory_key="chat_history"
        )
        
        chain = LLMChain(
            llm=self.llm,
            prompt=prompt,
            memory=memory,
            verbose=False
        )
        
        return chain
    
    async def process_request(self, user_id: str, message: str, context: Optional[Dict] = None) -> AgentResponse:
        """
        Main entry point for processing user requests through multi-step agentic workflow.
        """
        
        try:
            # Step 1: Get or create user data
            user_data = self.db_manager.get_user_data(user_id)
            if not user_data:
                user_data = self.db_manager.create_user(user_id)
            
            # Step 2: Analyze user intent and context
            intent_analysis = await self._analyze_intent(message, user_data, context)
            
            # Step 3: Determine required actions based on intent
            action_plan = await self._create_action_plan(intent_analysis, user_data)
            
            # Step 4: Execute actions in sequence
            execution_results = await self._execute_actions(action_plan, user_data, message)
            
            # Step 5: Generate comprehensive response using LangChain
            final_response = await self._generate_response_with_langchain(
                message, user_data, execution_results
            )
            
            # Step 6: Update user data if needed
            updated_data = self._prepare_data_updates(execution_results, user_data, message, final_response["response"])
            
            if updated_data:
                self.db_manager.update_user_data(user_id, updated_data)
                
                # Also add to conversation history
                self.db_manager.add_conversation_history(
                    user_id, message, final_response["response"], context
                )
            
            return AgentResponse(
                response=final_response["response"],
                actions_taken=execution_results["actions_completed"],
                recommendations=final_response["recommendations"],
                updated_data=updated_data
            )
            
        except Exception as e:
            # Fallback response in case of errors
            error_response = f"I apologize, but I encountered an issue processing your request. Please try again. Error: {str(e)}"
            return AgentResponse(
                response=error_response,
                actions_taken=["error_handling"],
                recommendations=[],
                updated_data=None
            )
    
    async def _analyze_intent(self, message: str, user_data: Dict[str, Any], context: Optional[Dict]) -> Dict[str, Any]:
        """Analyze user message to determine intent using LangChain."""
        
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
        
        Respond ONLY with a valid JSON object containing these fields.
        """
        
        try:
            response = self.llm.invoke([HumanMessage(content=analysis_prompt)])
            intent_json = response.content
            
            # Try to parse JSON from response
            if '{' in intent_json and '}' in intent_json:
                start = intent_json.find('{')
                end = intent_json.rfind('}') + 1
                intent_json = intent_json[start:end]
            
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
            "general_question": [
                "analyze_request",
                "provide_guidance"
            ]
        }
        
        actions = action_plans.get(intent, ["analyze_request", "provide_guidance"])
        
        return {
            "intent": intent,
            "actions": actions,
            "complexity": complexity,
            "estimated_duration": len(actions) * 2
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
            return self._analyze_current_nutrition(user_data)
        
        elif action == "check_recent_workouts":
            return self._check_recent_workouts(user_data)
        
        elif action == "calculate_requirements":
            return self._calculate_nutrition_requirements(user_data)
        
        elif action == "generate_recommendations":
            return await self._generate_nutrition_recommendations(user_data, current_results)
        
        elif action == "analyze_request":
            return {"action": "analyze_request", "message": message}
        
        elif action == "provide_guidance":
            return await self._provide_general_guidance(user_data, message)
        
        else:
            return {"action": action, "status": "not_implemented"}
    
    def _analyze_current_nutrition(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
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
        
        current_data = {
            "calories": avg_calories,
            "protein_g": avg_protein,
            "carbs_g": avg_carbs,
            "fat_g": avg_fat
        }
        
        target_data = {
            "calories": target_calories,
            "protein_g": macro_targets.get("protein_g", 100),
            "carbs_g": macro_targets.get("carbs_g", 200),
            "fat_g": macro_targets.get("fat_g", 60)
        }
        
        adherence = assess_nutrition_adherence(current_data, target_data)
        
        return {
            "current_averages": current_data,
            "targets": target_data,
            "adherence": adherence,
            "days_analyzed": total_days
        }
    
    def _check_recent_workouts(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check recent workout patterns and performance."""
        
        workouts = user_data.get("workouts", {}).get("logged_workouts", [])
        if not workouts:
            return {"status": "no_workouts", "message": "No recent workouts found"}
        
        # Get last 7 days of workouts
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=7)
        recent_workouts = []
        
        for workout in workouts:
            try:
                workout_date = datetime.fromisoformat(workout["date"].replace('Z', '+00:00'))
                if workout_date >= cutoff_date:
                    recent_workouts.append(workout)
            except (ValueError, KeyError):
                continue
        
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
            "frequency_per_week": round(workout_count * 7 / 7, 1)
        }
    
    def _calculate_nutrition_requirements(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate personalized nutrition requirements based on goals and activity."""
        
        profile = user_data.get("profile", {})
        goals = user_data.get("goals", {})
        
        # Use config to calculate requirements
        age = profile.get("age", 25)
        weight_kg = profile.get("weight_kg", 70)
        height_cm = profile.get("height_cm", 170)
        gender = profile.get("gender", "not_specified")
        activity_level = profile.get("activity_level", "moderately_active")
        primary_goal = goals.get("primary_goal", "maintenance")
        
        # Calculate BMR and TDEE
        bmr = Config.calculate_bmr(weight_kg, height_cm, age, gender)
        tdee = Config.calculate_tdee(bmr, activity_level)
        
        # Adjust for goal
        calorie_adjustments = {
            "weight_loss": -500,
            "muscle_gain": 300,
            "performance": 200,
            "maintenance": 0
        }
        
        adjusted_calories = tdee + calorie_adjustments.get(primary_goal, 0)
        
        # Get macro targets
        macro_targets = Config.get_macro_targets(primary_goal, adjusted_calories)
        
        return {
            "daily_calories": round(adjusted_calories),
            "daily_protein_g": round(macro_targets["protein_g"], 1),
            "daily_carbs_g": round(macro_targets["carbs_g"], 1),
            "daily_fat_g": round(macro_targets["fat_g"], 1),
            "bmr": round(bmr),
            "tdee": round(tdee)
        }
    
    async def _generate_nutrition_recommendations(self, user_data: Dict[str, Any], analysis_results: Dict) -> List[Dict[str, Any]]:
        """Generate specific nutrition recommendations based on analysis."""
        
        recommendations = []
        
        # Get analysis data
        nutrition_analysis = analysis_results.get("data_collected", {}).get("analyze_current_nutrition", {})
        workout_analysis = analysis_results.get("data_collected", {}).get("check_recent_workouts", {})
        
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
        
        for nutrient in ["calories", "protein_g", "carbs_g", "fat_g"]:
            adherence_data = adherence.get(nutrient, {})
            percentage = adherence_data.get("percentage", 100)
            
            if percentage < 85:
                nutrient_name = nutrient.replace("_g", "").replace("_", " ").title()
                recommendations.append({
                    "type": "nutrition",
                    "priority": "high" if percentage < 70 else "medium",
                    "title": f"Increase {nutrient_name}",
                    "message": f"Your {nutrient_name.lower()} intake is at {percentage:.1f}% of target. This is important for your goals.",
                    "specific_actions": self._get_nutrient_suggestions(nutrient)
                })
        
        return recommendations
    
    def _get_nutrient_suggestions(self, nutrient: str) -> List[str]:
        """Get specific suggestions for increasing a nutrient."""
        
        suggestions = {
            "calories": ["Add healthy snacks between meals", "Increase portion sizes", "Include calorie-dense foods like nuts"],
            "protein_g": ["Add protein powder to smoothies", "Include lean meat in every meal", "Try Greek yogurt or cottage cheese"],
            "carbs_g": ["Add whole grains to meals", "Include fruits and vegetables", "Try oatmeal or quinoa"],
            "fat_g": ["Add nuts, seeds, or avocado", "Use olive oil in cooking", "Include fatty fish like salmon"]
        }
        
        return suggestions.get(nutrient, ["Consult with a nutritionist for specific guidance"])
    
    async def _provide_general_guidance(self, user_data: Dict[str, Any], message: str) -> Dict[str, Any]:
        """Provide general guidance for unspecified requests."""
        
        profile = user_data.get("profile", {})
        goals = user_data.get("goals", {})
        
        guidance_context = f"""
        User Profile:
        - Sport: {profile.get('sport', 'fitness')}
        - Goal: {goals.get('primary_goal', 'maintenance')}
        - Experience: {profile.get('experience_level', 'beginner')}
        
        User Question: {message}
        
        Provide helpful, specific guidance based on their profile and question.
        """
        
        try:
            response = self.llm.invoke([HumanMessage(content=guidance_context)])
            return {"guidance": response.content}
        except Exception as e:
            return {"guidance": "I'm here to help with your nutrition and fitness questions. Could you be more specific about what you'd like to know?"}
    
    async def _generate_response_with_langchain(self, message: str, user_data: Dict[str, Any], execution_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate the final comprehensive response using LangChain."""
        
        # Build context for the conversation
        profile = user_data.get("profile", {})
        goals = user_data.get("goals", {})
        
        # Get conversation history
        conversation_history = user_data.get("ai_context", {}).get("conversation_history", [])
        recent_history = conversation_history[-5:] if len(conversation_history) > 5 else conversation_history
        
        # Prepare enhanced input with context
        enhanced_input = f"""
        User Message: {message}
        
        User Context:
        - Name: {profile.get('name', 'there')}
        - Sport: {profile.get('sport', 'fitness')}
        - Goal: {goals.get('primary_goal', 'maintenance')}
        - Experience: {profile.get('experience_level', 'beginner')}
        
        Analysis Results: {json.dumps(execution_results.get('data_collected', {}), indent=2)}
        
        Actions Completed: {execution_results.get('actions_completed', [])}
        
        Please provide a helpful, personalized response that:
        1. Directly addresses their question/request
        2. Provides specific, actionable recommendations
        3. Explains the reasoning behind suggestions
        4. Is encouraging and motivational
        5. Includes specific timing, quantities, or steps where relevant
        """
        
        try:
            # Use the conversation chain
            response = self.conversation_chain.invoke({"input": enhanced_input})
            
            # Extract recommendations if any
            recommendations = self._extract_recommendations_from_response(response["text"])
            
            return {
                "response": response["text"],
                "recommendations": recommendations
            }
            
        except Exception as e:
            # Fallback response
            fallback_response = f"I understand you're asking about {message}. Based on your profile as a {profile.get('sport', 'fitness')} athlete, I'd be happy to help you with personalized guidance. Let me know if you'd like specific advice about nutrition, training, or meal planning."
            
            return {
                "response": fallback_response,
                "recommendations": []
            }
    
    def _extract_recommendations_from_response(self, response_text: str) -> List[Dict[str, Any]]:
        """Extract actionable recommendations from the response text."""
        
        recommendations = []
        
        # Look for structured recommendations in the response
        lines = response_text.split('\n')
        current_rec = None
        
        for line in lines:
            line = line.strip()
            
            # Look for recommendation patterns
            if line.startswith('**') and line.endswith('**'):
                # Bold text might be a recommendation title
                if current_rec:
                    recommendations.append(current_rec)
                
                current_rec = {
                    "title": line.strip('*'),
                    "message": "",
                    "type": "general",
                    "priority": "medium"
                }
            
            elif line.startswith('-') or line.startswith('•'):
                # Bullet points might be action items
                if current_rec:
                    current_rec["message"] += line + " "
                else:
                    recommendations.append({
                        "title": "Action Item",
                        "message": line,
                        "type": "action",
                        "priority": "medium"
                    })
        
        # Add the last recommendation if exists
        if current_rec:
            recommendations.append(current_rec)
        
        return recommendations[:5]  # Limit to 5 recommendations
    
    def _prepare_data_updates(self, execution_results: Dict[str, Any], user_data: Dict[str, Any], 
                            message: str, response: str) -> Optional[Dict[str, Any]]:
        """Prepare any updates to user data based on the workflow execution."""
        
        updates = {}
        
        # Update AI context
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


def lambda_handler(event, context):
    """
    AWS Lambda handler function for the Fuelyt AI Agent.
    """
    
    try:
        # Parse the incoming event
        if 'body' in event:
            # API Gateway event
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        else:
            # Direct invocation
            body = event
        
        # Extract required parameters
        user_id = body.get('user_id')
        message = body.get('message')
        request_context = body.get('context', {})
        
        if not user_id or not message:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "error": "Missing required parameters: user_id and message"
                })
            }
        
        # Initialize and run the agent
        agent = FuelytAgentHandler()
        
        # Process the request (note: we need to handle async in sync context)
        import asyncio
        
        async def process():
            return await agent.process_request(user_id, message, request_context)
        
        # Run the async function
        if hasattr(asyncio, 'run'):
            # Python 3.7+
            response = asyncio.run(process())
        else:
            # Fallback for older versions
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                response = loop.run_until_complete(process())
            finally:
                loop.close()
        
        # Format the response for serverless
        result = {
            "response": response.response,
            "actions_taken": response.actions_taken,
            "recommendations": response.recommendations
        }
        
        return {
            "statusCode": 200,
            "body": json.dumps(result)
        }
        
    except Exception as e:
        # Error handling
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": f"Internal server error: {str(e)}"
            })
        }


# For local testing
async def test_local():
    """Test the handler locally."""
    
    handler = FuelytAgentHandler()
    
    test_event = {
        "user_id": "test_athlete",
        "message": "Hi! I'm a runner and I want to improve my nutrition for better performance.",
        "context": {"source": "local_test"}
    }
    
    response = await handler.process_request(
        test_event["user_id"],
        test_event["message"],
        test_event["context"]
    )
    
    print("Response:", response.response)
    print("Actions:", response.actions_taken)
    print("Recommendations:", response.recommendations)


if __name__ == "__main__":
    # Local testing
    import asyncio
    asyncio.run(test_local())