# PerformanceReport Class

class PerformanceReport:
    def __init__(self, diversions: int = 0, cancellations: int = 0, total_planes: int = 0, tot_wait_time: float = 0.0, tot_fuel_used: float = 0.0):
        self.diversions = diversions
        self.cancellations = cancellations
        self.total_planes = total_planes
        self.tot_wait_time = tot_wait_time
        self.tot_fuel_used = tot_fuel_used

    def output(self) -> str:
        pass

    def reset(self) -> bool:
        pass