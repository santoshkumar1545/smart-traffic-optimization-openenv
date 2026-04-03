from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from env.environment import TrafficEnv
from env.models import StepAction, StepResponse, ResetResponse, TrafficState

app = FastAPI(title="OpenEnv Traffic Signal Control")

# Allow frontend dashboard to access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

env = TrafficEnv()


@app.get("/")
def home():
    return {"message": "Traffic Signal OpenEnv is running"}


@app.post("/reset", response_model=ResetResponse)
def reset(task_id: str = Query(default="easy")):
    state = env.reset(task_id=task_id)
    return ResetResponse(
        state=state,
        task_id=task_id,
        description=f"Traffic control task initialized for {task_id} difficulty"
    )


@app.get("/state", response_model=TrafficState)
def state():
    if env.get_state() is None:
        return env.reset("easy")
    return env.get_state()


@app.post("/step", response_model=StepResponse)
def step(action_data: StepAction):
    state, reward, done, info = env.step(action_data.action)
    return StepResponse(
        state=state,
        reward=reward,
        done=done,
        info=info
    )