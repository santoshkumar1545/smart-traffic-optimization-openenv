from pydantic import BaseModel
from typing import Dict


class TrafficState(BaseModel):
    road1: str
    road2: str
    road3: str
    road4: str
    signal_times: Dict[str, int]
    priority_road: str