# Fuelyt AI Agent

A Python-based AI agent that helps athletes optimize their nutrition and performance through intelligent, multi-step agentic workflows powered by OpenAI.

## 🏃‍♂️ What Fuelyt Does

Fuelyt is your personal AI nutrition and fitness coach that provides:

- **Prescriptive Nutrition Guidance**: Personalized recommendations for what to eat before, during, and after workouts
- **Macro & Calorie Tracking**: Intelligent analysis of your daily nutrition intake
- **Workout Logging**: Track your training sessions with performance insights
- **Meal Planning & Recipes**: Custom meal plans and recipe recommendations
- **Calendar Integration**: Schedule meals and workouts with smart reminders
- **Progress Tracking**: Monitor your journey toward your fitness goals

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key

### Installation

1. **Clone or create the project**:
```bash
mkdir fuelyt-agent
cd fuelyt-agent
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**:
```bash
export OPENAI_API_KEY="your-openai-api-key-here"
# Optional configurations
export ENVIRONMENT="development"
export API_PORT="8000"
```

4. **Run the agent**:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## 📊 Database Setup

Fuelyt uses **TinyDB** for local development - a lightweight, JSON-based database that requires zero configuration:

- **File location**: `fuelyt_data.json` (created automatically)
- **Format**: Human-readable JSON
- **Zero setup**: No installation or configuration needed
- **Perfect for**: Development, testing, and single-user deployments

### Alternative Databases for Production

- **MongoDB Atlas** (recommended for production)
- **DynamoDB** (for AWS Lambda)
- **Firestore** (for Google Cloud Functions)

## 🎯 Core Features

### 1. Chat Interface

```python
POST /chat
{
    "user_id": "athlete_123",
    "message": "What should I eat before my 5k run tomorrow morning?",
    "context": {"workout_time": "07:00", "workout_type": "cardio"}
}
```

### 2. Workout Logging

```python
POST /log-workout
{
    "user_id": "athlete_123",
    "workout_data": {
        "type": "cardio",
        "duration_minutes": 30,
        "intensity": "moderate",
        "exercises": [
            {
                "name": "running",
                "duration_minutes": 30,
                "distance_km": 5.0
            }
        ]
    }
}
```

### 3. Nutrition Tracking

```python
POST /log-nutrition
{
    "user_id": "athlete_123",
    "nutrition_data": {
        "type": "breakfast",
        "foods": [
            {
                "name": "oatmeal",
                "quantity": 1,
                "unit": "cup",
                "calories": 300,
                "macros": {
                    "protein_g": 10,
                    "carbs_g": 54,
                    "fat_g": 6,
                    "fiber_g": 8
                }
            }
        ]
    }
}
```

### 4. Get Recommendations

```python
GET /get-recommendations/athlete_123?recommendation_type=nutrition
```

### 5. Dashboard Data

```python
GET /dashboard/athlete_123
```

## 🏗️ Architecture

### Multi-Step Agentic Workflow

Fuelyt uses a sophisticated multi-step workflow:

1. **Intent Analysis**: Understands what the athlete needs
2. **Action Planning**: Creates a step-by-step plan
3. **Execution**: Runs analysis and calculations
4. **Response Generation**: Provides personalized recommendations
5. **Data Updates**: Stores insights for future use

### Project Structure

```
fuelyt-agent/
├── main.py                 # FastAPI serverless function
├── agent_workflow.py       # Multi-step AI workflow engine
├── data_models.py         # Pydantic data models
├── database_manager.py    # TinyDB database operations
├── config.py             # Configuration and constants
├── utils.py              # Utility functions
├── requirements.txt      # Python dependencies
├── user_schema.json      # JSON schema documentation
├── database_recommendations.md  # Database options
└── examples/
    ├── example_usage.py   # Usage examples
    └── test_data.json    # Sample user data
```

## 🎮 Example Usage

### Creating a New User

```python
import requests

# Create user with basic profile
response = requests.post("http://localhost:8000/chat", json={
    "user_id": "new_athlete",
    "message": "Hi, I'm a runner training for a marathon. I want to improve my nutrition.",
    "context": {
        "profile": {
            "name": "Alex",
            "age": 28,
            "sport": "running",
            "goal": "endurance",
            "experience_level": "intermediate"
        }
    }
})

print(response.json())
```

### Getting Meal Recommendations

```python
response = requests.post("http://localhost:8000/chat", json={
    "user_id": "new_athlete",
    "message": "I have a long run planned for 6 AM. What should I eat tonight and tomorrow morning?"
})

recommendations = response.json()["recommendations"]
for rec in recommendations:
    print(f"- {rec['title']}: {rec['message']}")
```

## 🔧 Configuration

### Environment Variables

```bash
# Required
OPENAI_API_KEY=your-api-key

# Optional
ENVIRONMENT=development          # development, production, test
API_HOST=0.0.0.0
API_PORT=8000
DATABASE_PATH=fuelyt_data.json
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_TEMPERATURE=0.7
MAX_CONVERSATION_HISTORY=50
```

### Customizing Goals and Calculations

Edit `config.py` to customize:

- Macro ratio recommendations by goal
- Protein requirements by sport
- Activity level multipliers
- BMR calculations

## 📈 User Data Schema

The agent stores comprehensive user data including:

- **Profile**: Personal info, sport, goals, restrictions
- **Workouts**: Logged sessions with performance data
- **Nutrition**: Daily meal logs with macro tracking
- **Progress**: Body measurements and performance metrics
- **Calendar**: Scheduled meals and workout plans
- **AI Context**: Conversation history and learned preferences

See `user_schema.json` for the complete schema.

## 🚀 Deployment

### Local Development
```bash
python main.py
```

### AWS Lambda
```bash
pip install aws-lambda-powertools
# Configure serverless.yml or use AWS CDK
```

### Google Cloud Functions
```bash
pip install functions-framework
functions-framework --target=app --port=8000
```

### Docker
```bash
docker build -t fuelyt-agent .
docker run -p 8000:8000 -e OPENAI_API_KEY=your-key fuelyt-agent
```

## 🧪 Testing

```bash
# Run basic health check
curl http://localhost:8000/

# Test chat endpoint
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "message": "Hello Fuelyt!"}'
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your improvements
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

- Check the issues tab for common problems
- Review the database recommendations for scaling
- Ensure your OpenAI API key is valid and has sufficient credits

---

**Built with ❤️ for athletes who want to fuel their performance through intelligent nutrition.**