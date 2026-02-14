# Simulation Controller
from datetime import datetime, timedelta
from plane import Plane
from models import Runway
from queue_manager import QueueController
from report import PerformanceReport
import random

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
        p = Plane(is_departure, self.time)
        if is_departure:
            self.departure_queue.enqueue(p)
        else:
            self.landing_queue.enqueue(p)

        self.report.total_planes += 1

    def generateQueue(self) -> bool:
        pass

    def generateRunway(self) -> bool:
        self.runway_list = []
        runway_num = 1
        for i in range(self.departure_runways):
            self.runway_list.append(Runway(True, False, runway_num, True, True))
            runway_num += 1

        for i in range(self.landing_runways):
            self.runway_list.append(Runway(False, False, runway_num, True, True))
            runway_num += 1
        
        for i in range(self.mixed_runways):
            self.runway_list.append(Runway(True, True, runway_num, True, True))
            runway_num += 1
        return True

    def update(self) -> bool:
        pass