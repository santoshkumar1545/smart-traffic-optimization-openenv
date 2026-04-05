from env.models import TrafficState


class TrafficEnvironment:
    def __init__(self):
        self.state_data = None

    def reset(self):
        self.state_data = TrafficState(
            road1="Low Traffic",
            road2="Low Traffic",
            road3="Low Traffic",
            road4="Low Traffic",
            signal_times={
                "Road1": 20,
                "Road2": 20,
                "Road3": 20,
                "Road4": 20
            },
            priority_road="Road1"
        )
        return self.state_data

    def state(self):
        return self.state_data

    def step(self, action=None):
        return self.state_data