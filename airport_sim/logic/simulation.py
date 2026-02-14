# Simulation Controller

class SimulationController:
    def __init__(
        self,
        departures_per_hour: int,
        landings_per_hour: int,
        total_runways: int,
        departure_runways: int,
        landing_runways: int,
        mixed_runways: int,
        cancellation_time: int,
    ):
        self.departures_per_hour = departures_per_hour
        self.landings_per_hour = landings_per_hour
        self.total_runways = total_runways
        self.departure_runways = departure_runways
        self.landing_runways = landing_runways
        self.mixed_runways = mixed_runways
        self.cancellation_time = cancellation_time

    def generateSimulation(self, preset: int) -> bool: # Consider if a preset exists according to Fede
        pass

    def generatePlane(self, is_departure: bool) -> bool:
        pass

    def generateQueue(self) -> bool:
        pass

    def generateRunway(self) -> bool:
        pass

    def update(self) -> bool:
        pass


