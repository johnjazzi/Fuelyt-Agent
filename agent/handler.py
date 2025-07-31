from .data_models import User, ChatMessage
from .database_manager import db_manager
from .config import settings
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage
import asyncio

class AgentHandler:
    def __init__(self):
        self.chat_model = ChatOpenAI(api_key=settings.OPENAI_API_KEY, model="gpt-4-turbo-preview", streaming=True)

    async def handle_chat(self, chat_message: ChatMessage):
        user = db_manager.get_user(chat_message.user_id)
        if not user:
            yield "data: {\"error\": \"User not found\"}\n\n"
            return

        user_profile_and_goals = {
            "profile": user.profile.dict(),
            "goals": user.goals.dict()
        }

        messages = [
            SystemMessage(content="You are a world-class athletic performance coach..."),
            HumanMessage(content=f"Here is my data: {user_profile_and_goals}"),
        ]
        
        clean_history = []
        for ch in user.ai_context.get("conversation_history", []):
            if isinstance(ch, dict) and "user" in ch and "ai" in ch:
                clean_history.append(ch)
                messages.append(HumanMessage(content=ch["user"]))
                messages.append(AIMessage(content=ch["ai"]))

        messages.append(HumanMessage(content=chat_message.message))

        full_response = ""
        try:
            async for chunk in self.chat_model.astream(messages):
                full_response += chunk.content
                yield f"data: {chunk.content}\n\n"
        
        finally:
            # Update conversation history once the full response is received
            clean_history.append({"user": chat_message.message, "ai": full_response})
            user.ai_context["conversation_history"] = clean_history
            db_manager.update_user(user.user_id, {"ai_context": user.ai_context})

agent_handler = AgentHandler()

