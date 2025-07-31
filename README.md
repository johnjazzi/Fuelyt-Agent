# Fuelyt AI Agent

This project is an AI-powered nutrition and performance coach designed to help athletes optimize their health and training. It's built with a FastAPI backend, a Vue.js frontend, and leverages LangChain and OpenAI for its AI capabilities.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- Python 3.10+
- Node.js and npm
- An OpenAI API key

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/Fuelyt-Agent.git
    cd Fuelyt-Agent
    ```

2.  **Set up the backend:**

    - Create a virtual environment:
      ```bash
      python3 -m venv venv
      source venv/bin/activate
      ```
    - Install the required Python packages:
      ```bash
      pip install -r agent/requirements.txt
      ```
    - Create a `.env` file in the `agent` directory and add your OpenAI API key:
      ```
      OPENAI_API_KEY="your_openai_api_key"
      ```

3.  **Set up the frontend:**

    - Navigate to the `frontend` directory:
      ```bash
      cd frontend
      ```
    - Install the required npm packages:
      ```bash
      npm install
      ```

## Running the Application

1.  **Start the backend server:**

    - From the project's root directory, run the following command:
      ```bash
      bash start.sh
      ```
    - The backend will be running at `http://localhost:8000`.

2.  **Start the frontend development server:**

    - In a separate terminal, navigate to the `frontend` directory and run:
      ```bash
      npm run dev
      ```
    - The frontend will be running at `http://localhost:3000`.

3.  **Access the application:**

    - Open your web browser and navigate to `http://localhost:3000`.

## Project Structure

```
Fuelyt-Agent/
├── agent/
│   ├── main.py             # FastAPI application entry point
│   ├── handler.py          # Core agent logic
│   ├── data_models.py      # Pydantic data models
│   ├── database_manager.py # TinyDB database manager
│   ├── config.py           # Configuration settings
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.vue         # Main Vue component
│   │   └── main.js         # Frontend entry point
│   ├── package.json        # Frontend dependencies
│   └── vite.config.js      # Vite configuration
├── venv/                   # Python virtual environment
├── start.sh                # Script to start the backend server
└── README.md               # This file
```
