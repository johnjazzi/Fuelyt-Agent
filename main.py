"""
Fuelyt AI Agent - Main API Server
Updated to work with the new serverless agent handler structure.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# Import the serverless handler
from agent.handler import FuelytAgentHandler, lambda_handler
from database_manager import DatabaseManager


# Initialize FastAPI app
app = FastAPI(title="Fuelyt AI Agent", version="2.0.0")

# Initialize database and agent
db_manager = DatabaseManager()
agent_handler = FuelytAgentHandler()


class AgentRequest(BaseModel):
    user_id: str
    message: str
    context: Optional[Dict[str, Any]] = None


class AgentResponse(BaseModel):
    response: str
    actions_taken: List[str]
    recommendations: List[Dict[str, Any]]


@app.get("/")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy", 
        "service": "Fuelyt AI Agent", 
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/chat", response_model=AgentResponse)
async def chat_with_agent(request: AgentRequest):
    """
    Main chat endpoint that uses the serverless handler.
    """
    try:
        # Use the serverless handler directly
        agent_response = await agent_handler.process_request(
            user_id=request.user_id,
            message=request.message,
            context=request.context
        )
        
        return AgentResponse(
            response=agent_response.response,
            actions_taken=agent_response.actions_taken,
            recommendations=agent_response.recommendations
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent processing error: {str(e)}")


@app.post("/lambda-test")
async def test_lambda_handler(request: AgentRequest):
    """
    Test endpoint that simulates the Lambda handler for local testing.
    """
    try:
        # Simulate Lambda event
        event = {
            "body": json.dumps({
                "user_id": request.user_id,
                "message": request.message,
                "context": request.context
            })
        }
        
        # Call the lambda handler
        lambda_response = lambda_handler(event, {})
        
        # Parse the response
        if lambda_response["statusCode"] == 200:
            response_data = json.loads(lambda_response["body"])
            return {
                "lambda_response": response_data,
                "status_code": lambda_response["statusCode"]
            }
        else:
            raise HTTPException(
                status_code=lambda_response["statusCode"],
                detail=json.loads(lambda_response["body"])
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lambda test error: {str(e)}")


@app.post("/log-workout")
async def log_workout(user_id: str, workout_data: Dict[str, Any]):
    """Log a completed workout for the user."""
    try:
        # Format workout data for the agent
        message = f"I just completed a workout: {workout_data.get('type', 'exercise')} for {workout_data.get('duration_minutes', 0)} minutes."
        
        # Add workout to user data via database manager
        success = db_manager.add_workout(user_id, workout_data)
        if not success:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get recommendations from agent
        agent_response = await agent_handler.process_request(
            user_id=user_id,
            message=message,
            context={"action": "workout_logged", "workout_data": workout_data}
        )
        
        return {
            "message": "Workout logged successfully",
            "recommendations": agent_response.recommendations,
            "agent_response": agent_response.response
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workout logging error: {str(e)}")


@app.post("/log-nutrition")
async def log_nutrition(user_id: str, nutrition_data: Dict[str, Any]):
    """Log nutrition intake for the user."""
    try:
        # Format nutrition data for the agent
        message = f"I just ate {nutrition_data.get('type', 'a meal')} with {len(nutrition_data.get('foods', []))} items."
        
        # Add nutrition to user data via database manager
        success = db_manager.add_nutrition_log(user_id, nutrition_data)
        if not success:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get analysis from agent
        agent_response = await agent_handler.process_request(
            user_id=user_id,
            message=message,
            context={"action": "nutrition_logged", "nutrition_data": nutrition_data}
        )
        
        return {
            "message": "Nutrition logged successfully",
            "analysis": agent_response.recommendations,
            "agent_response": agent_response.response
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Nutrition logging error: {str(e)}")


@app.get("/get-recommendations/{user_id}")
async def get_recommendations(user_id: str, recommendation_type: str = "all"):
    """Get personalized recommendations for the user."""
    try:
        # Format request for the agent
        message = f"Can you give me {recommendation_type} recommendations based on my recent activity?"
        
        agent_response = await agent_handler.process_request(
            user_id=user_id,
            message=message,
            context={"action": "get_recommendations", "type": recommendation_type}
        )
        
        return {
            "recommendations": agent_response.recommendations,
            "response": agent_response.response
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation error: {str(e)}")


@app.post("/plan-meal")
async def plan_meal(user_id: str, meal_request: Dict[str, Any]):
    """Generate meal plan recommendations."""
    try:
        # Format meal planning request
        duration = meal_request.get("duration_days", 1)
        focus = meal_request.get("focus", "general nutrition")
        message = f"Can you create a {duration}-day meal plan focused on {focus}?"
        
        agent_response = await agent_handler.process_request(
            user_id=user_id,
            message=message,
            context={"action": "meal_planning", "request": meal_request}
        )
        
        return {
            "meal_plan": agent_response.recommendations,
            "response": agent_response.response
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Meal planning error: {str(e)}")


@app.get("/dashboard/{user_id}")
async def get_dashboard_data(user_id: str):
    """Get comprehensive dashboard data for the user."""
    try:
        user_data = db_manager.get_user_data(user_id)
        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get recent workouts and nutrition
        recent_workouts = db_manager.get_recent_workouts(user_id, days=7)
        recent_nutrition = db_manager.get_recent_nutrition(user_id, days=7)
        
        dashboard_data = {
            "user_profile": {
                "name": user_data.get("profile", {}).get("name", "Athlete"),
                "goal": user_data.get("goals", {}).get("primary_goal", "maintenance"),
                "sport": user_data.get("profile", {}).get("sport", "fitness")
            },
            "recent_activity": {
                "workouts_count": len(recent_workouts),
                "nutrition_logs_count": len(recent_nutrition),
                "last_workout": recent_workouts[-1] if recent_workouts else None,
                "last_nutrition": recent_nutrition[-1] if recent_nutrition else None
            },
            "quick_stats": {
                "total_workouts": len(user_data.get("workouts", {}).get("logged_workouts", [])),
                "total_nutrition_logs": len(user_data.get("nutrition", {}).get("daily_logs", [])),
                "account_created": user_data.get("created_at", "Unknown")
            }
        }
        
        return dashboard_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard error: {str(e)}")


@app.get("/user/{user_id}")
async def get_user_data(user_id: str):
    """Get user data (for debugging)."""
    try:
        user_data = db_manager.get_user_data(user_id)
        if not user_data:
            # Create new user
            user_data = db_manager.create_user(user_id)
        
        return {"user_data": user_data}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"User data error: {str(e)}")


# CORS middleware for frontend
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# For local development
if __name__ == "__main__":
    print("🚀 Starting Fuelyt AI Agent Server")
    print("📊 API Documentation: http://localhost:8000/docs")
    print("🎯 Frontend: http://localhost:3000")
    print("🔬 Lambda Test: http://localhost:8000/lambda-test")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)