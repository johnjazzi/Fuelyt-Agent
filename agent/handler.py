from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from .data_models import ChatMessage, User
from .database_manager import db_manager
from .config import settings
from .tools import (
    log_workout, update_user_profile, log_meal, create_or_update_goal,
    schedule_workout, schedule_meal, get_schedule,
    LogWorkoutInput, UpdateUserProfileInput, LogMealInput, CreateOrUpdateGoalInput,
    ScheduleWorkoutInput, ScheduleMealInput, GetScheduleInput
)
import json

# Load system prompt from file
with open("agent/system_prompt.txt", "r") as f:
    SYSTEM_PROMPT = f.read()

# Define the tools
tools = [
    tool(log_workout, args_schema=LogWorkoutInput),
    tool(update_user_profile, args_schema=UpdateUserProfileInput),
    tool(log_meal, args_schema=LogMealInput),
    tool(create_or_update_goal, args_schema=CreateOrUpdateGoalInput),
    tool(schedule_workout, args_schema=ScheduleWorkoutInput),
    tool(schedule_meal, args_schema=ScheduleMealInput),
    tool(get_schedule, args_schema=GetScheduleInput),
]

class AgentHandler:
    def __init__(self):
        self.chat_model = ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model="gpt-4-turbo-preview",
            streaming=True,
        )
        self.agent = create_openai_functions_agent(
            llm=self.chat_model,
            tools=tools,
            prompt=self._create_prompt(),
        )
        self.agent_executor = AgentExecutor(agent=self.agent, tools=tools, verbose=False)

    def _create_prompt(self):
        return ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

    async def handle_chat(self, chat_message: ChatMessage):
        user = db_manager.get_user(chat_message.user_id)
        if not user:
            # If user does not exist, create a new one with default values
            new_user_data = {
                "profile": {
                    "name": "Demo User",
                    "age": 30,
                    "gender": "Not specified",
                    "height_cm": 175,
                    "weight_kg": 70
                },
                "goals": {
                    "primary_goal": "maintenance"
                }
            }
            user = User(user_id=chat_message.user_id, **new_user_data)
            db_manager.create_user(user)

        chat_history = self._reconstruct_history(user)
        
        # Prepend the user_id to the message to ensure the agent has it
        augmented_message = f"User ID: {chat_message.user_id}\n\n{chat_message.message}"

        full_response = ""
        async for chunk in self.agent_executor.astream({
            "input": augmented_message,
            "chat_history": chat_history,
        }):
            if "output" in chunk:
                full_response += chunk["output"]
                yield f"data: {json.dumps({'content': chunk['output']})}\n\n"
        
        # After streaming is complete, save the conversation history
        self._update_conversation_history(user, chat_message.message, full_response)

    def _reconstruct_history(self, user: User):
        history = []
        for message in user.ai_context.get("conversation_history", []):
            if isinstance(message, dict) and "user" in message and "ai" in message:
                history.append(HumanMessage(content=message["user"]))
                history.append(AIMessage(content=message["ai"]))
        return history

    def _update_conversation_history(self, user: User, user_message: str, ai_response: str):
        history = user.ai_context.get("conversation_history", [])
        history.append({"user": user_message, "ai": ai_response})
        user.ai_context["conversation_history"] = history
        db_manager.update_user(user.user_id, {"ai_context": user.ai_context})

agent_handler = AgentHandler()
