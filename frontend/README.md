# Fuelyt Frontend

A minimalist Vue.js chat interface for the Fuelyt AI nutrition coach.

## Setup

1. **Install dependencies:**
```bash
cd frontend
npm install
```

2. **Start the development server:**
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Features

- **Clean Chat Interface**: Modern, responsive chat UI
- **Real-time Messaging**: Instant communication with the AI agent
- **Recommendations Display**: Shows structured recommendations from the AI
- **User Management**: Simple user ID input for multi-user support
- **Error Handling**: Graceful error handling and user feedback

## Usage

1. **Start the backend**: Make sure the Fuelyt API server is running on port 8000
2. **Enter User ID**: Use any identifier like "athlete_123" or "demo_athlete"
3. **Start Chatting**: Ask about nutrition, log workouts, request meal plans

## API Proxy

The frontend proxies API requests to the backend:
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- Proxy: `/api/*` routes to backend

## Example Conversations

Try these sample messages:
- "Hi! I'm a marathon runner looking to improve my nutrition."
- "What should I eat before a 5K race tomorrow morning?"
- "Can you create a 3-day meal plan for my training week?"
- "I just completed a 10-mile run. What should I eat for recovery?"

## Development

- **Hot Reload**: Vite provides instant hot reload for development
- **Vue 3**: Uses the latest Vue.js with Composition API
- **Responsive**: Works on desktop and mobile devices
- **Modern CSS**: Clean, modern styling with gradients and animations