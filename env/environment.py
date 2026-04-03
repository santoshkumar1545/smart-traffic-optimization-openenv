import random
from env.models import TrafficState


class TrafficEnv:
    def __init__(self):
        self.tasks = {
            "easy": {"max_steps": 10, "arrival_range": (0, 2), "emergency_prob": 0.1},
            "medium": {"max_steps": 15, "arrival_range": (1, 3), "emergency_prob": 0.2},
            "hard": {"max_steps": 20, "arrival_range": (2, 4), "emergency_prob": 0.3},
        }
        self.current_task = "easy"
        self.state = None
        self.last_served = {1: 0, 2: 0, 3: 0}

    def reset(self, task_id="easy"):
        if task_id not in self.tasks:
            task_id = "easy"

        self.current_task = task_id
        config = self.tasks[task_id]

        emergency_lane = random.choice([1, 2, 3]) if random.random() < config["emergency_prob"] else None

        self.state = TrafficState(
            lane_1_cars=random.randint(5, 12),
            lane_2_cars=random.randint(5, 12),
            lane_3_cars=random.randint(5, 12),
            current_signal=1,
            emergency_lane=emergency_lane,
            step_count=0,
            max_steps=config["max_steps"],
            done=False
        )

        self.last_served = {1: 0, 2: 0, 3: 0}
        return self.state

    def get_state(self):
        return self.state

    def step(self, action: int):
        if self.state is None:
            self.reset(self.current_task)

        if self.state.done:
            return self.state, 0.0, True, {"message": "Episode already finished"}

        reward = 0.0

        # Invalid action handling
        if action not in [1, 2, 3]:
            reward -= 0.5
            action = self.state.current_signal

        # Signal switching penalty
        if action != self.state.current_signal:
            reward -= 0.1

        self.state.current_signal = action

        # Emergency vehicle reward/penalty
        if self.state.emergency_lane is not None:
            if action == self.state.emergency_lane:
                reward += 1.0
            else:
                reward -= 0.8

        # Cars cleared
        lane_attr = f"lane_{action}_cars"
        current_cars = getattr(self.state, lane_attr)
        cars_cleared = min(5, current_cars)
        setattr(self.state, lane_attr, current_cars - cars_cleared)

        reward += cars_cleared * 0.25

        # Fairness tracking
        for lane in self.last_served:
            self.last_served[lane] += 1
        self.last_served[action] = 0

        if max(self.last_served.values()) <= 4:
            reward += 0.1
        else:
            reward -= 0.2

        # New traffic arrival
        arrival_min, arrival_max = self.tasks[self.current_task]["arrival_range"]
        self.state.lane_1_cars += random.randint(arrival_min, arrival_max)
        self.state.lane_2_cars += random.randint(arrival_min, arrival_max)
        self.state.lane_3_cars += random.randint(arrival_min, arrival_max)

        # Congestion penalty
        total_waiting = (
            self.state.lane_1_cars +
            self.state.lane_2_cars +
            self.state.lane_3_cars
        )
        reward -= total_waiting * 0.01

        # Throughput bonus
        if total_waiting < 20:
            reward += 0.2
        elif total_waiting < 30:
            reward += 0.1

        # Generate next emergency event
        emergency_prob = self.tasks[self.current_task]["emergency_prob"]
        self.state.emergency_lane = random.choice([1, 2, 3]) if random.random() < emergency_prob else None
        self.state.step_count += 1
        self.state.done = False

        info = {
            "cars_cleared": cars_cleared,
            "total_waiting": total_waiting,
            "fairness": dict(self.last_served),
            "emergency_lane": self.state.emergency_lane
        }

        return self.state, round(reward, 3), self.state.done, info