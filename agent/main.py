from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse
from .data_models import ChatMessage, User
from .handler import agent_handler, tools
from .database_manager import db_manager

app = FastAPI(
    title="Fuelyt AI Agent",
    description="AI agent to help athletes optimize their nutrition and performance.",
    version="0.1.0",
)

# CORS configuration
origins = [
    "http://localhost:5173",  # Assuming default Vite dev server port
    "http://127.0.0.1:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Health Check"])
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

@app.post("/chat", tags=["Agent"])
async def chat(chat_message: ChatMessage):
    """Main agent interaction endpoint."""
    return StreamingResponse(agent_handler.handle_chat(chat_message), media_type="text/event-stream")

@app.post("/users", tags=["Users"])
async def create_user(user: User):
    """Create a new user."""
    return db_manager.create_user(user)

@app.get("/tools", tags=["Agent"])
async def get_tools():
    """Return the list of available tools."""
    return {"tools": [tool.name for tool in tools]}
