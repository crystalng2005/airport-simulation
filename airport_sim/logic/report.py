# PerformanceReport Class

class PerformanceReport:
    def __init__(self, diversions: int = 0, cancellations: int = 0, total_planes: int = 0, tot_wait_time: float = 0.0, tot_fuel_used: float = 0.0):
        self.diversions = diversions
        self.cancellations = cancellations
        self.total_planes = total_planes
        self.tot_wait_time = tot_wait_time
        self.tot_fuel_used = tot_fuel_used

    def output(self) -> dict:
        avg_wait = (
            self.tot_wait_time / self.total_planes
            if self.total_planes > 0
            else 0
        )

        return {
            "total_planes": self.total_planes,
            "cancellations": self.cancellations,
            "diversions": self.diversions,
            "average_wait_time": round(avg_wait, 2),
            "total_fuel_used": round(self.tot_fuel_used, 2),
        }

    def reset(self) -> bool:
        self.__init__()
        return True