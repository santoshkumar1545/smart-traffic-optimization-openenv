from pydantic import BaseModel
from typing import Optional


class TrafficState(BaseModel):
    lane_1_cars: int
    lane_2_cars: int
    lane_3_cars: int
    current_signal: int
    emergency_lane: Optional[int] = None
    step_count: int
    max_steps: int
    done: bool


class StepAction(BaseModel):
    action: int


class StepResponse(BaseModel):
    state: TrafficState
    reward: float
    done: bool
    info: dict


class ResetResponse(BaseModel):
    state: TrafficState
    task_id: str
    description: str