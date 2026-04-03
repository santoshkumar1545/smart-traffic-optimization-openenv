🚦 Smart Traffic Signal Control System

An AI-powered Smart Traffic Signal Control System built as a real-world reinforcement learning (RL) environment using the OpenEnv specification. The system dynamically controls traffic signals to optimize traffic flow and prioritize emergency vehicles.

📌 Project Description

This project simulates a real-world traffic intersection where an intelligent agent decides which lane should receive the green signal based on traffic conditions.

The system models:

🚗 Multiple traffic lanes (3 lanes)
📈 Dynamic vehicle flow and congestion
🚑 Emergency vehicle prioritization
⚖️ Fair traffic distribution
🎯 Reward-based optimization

At every step, the agent selects an action (which lane gets green signal) to maximize efficiency while minimizing waiting time and congestion.

The project also includes a real-time web dashboard where users can:

View traffic conditions
Control signals manually
Run automatic AI-based simulation
✨ Key Features
🚦 Adaptive traffic signal control
🚑 Emergency vehicle prioritization
🤖 Auto mode with intelligent decision-making
🔁 Manual lane control
📊 Reward tracking visualization
🌐 FastAPI-based backend APIs
🧠 Reinforcement learning environment design
🔄 Continuous simulation mode (demo)
📦 OpenEnv-compliant API (step/reset/state)
🧰 Tech Stack
Frontend
HTML5
CSS (Tailwind CSS + custom styles)
JavaScript (Vanilla JS)
Chart.js (for reward visualization)
Backend
Python
FastAPI (REST API)
Uvicorn (ASGI server)
Environment & Modeling
OpenEnv specification
Pydantic (typed models)
AI / Logic
Rule-based baseline agent
Emergency-aware decision logic
Reward-based optimization strategy
Deployment & Tools
Docker (containerization)
Hugging Face Spaces (deployment target)
GitHub (version control)
How to Run Locally
1️⃣ Install dependencies
pip install -r requirements.txt
2️⃣ Start backend server
uvicorn app:app --reload
3️⃣ Open dashboard

Open:

index.html

in your browser.

🔍 API Endpoints
✅ Health Check
GET /

Response:

{
  "message": "Smart Traffic Control API is running"
}
📊 Get Current State
GET /state
🔄 Reset Environment
POST /reset?task_id=easy
▶️ Take Action
POST /step

Request body:

{
  "action": 1
}
🧪 API Health Check Methods

You can verify that the API is working using the following:

✅ 1. Browser

Open:

http://127.0.0.1:8000
✅ 2. Swagger UI (Recommended)

Open:

http://127.0.0.1:8000/docs

Test all endpoints interactively.

✅ 3. Terminal (curl)
curl http://127.0.0.1:8000
curl http://127.0.0.1:8000/state
✅ 4. Postman
GET /state
POST /reset
POST /step
🤖 Auto Mode Logic

The Auto mode uses a simple intelligent policy:

🚑 If an emergency vehicle is present → prioritize that lane
🚗 Otherwise → select the lane with the highest traffic

This simulates how an AI agent interacts with the environment in real time.

🎯 Use Case

This project demonstrates how reinforcement learning environments can be applied to real-world infrastructure problems such as:

Smart city traffic management
Congestion reduction
Emergency response optimization