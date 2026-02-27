# Simulation Controller
from datetime import datetime, timedelta
import random

from logic.plane import Plane
from logic.models import Runway
from logic.queue_manager import QueueController
from airport_sim.logic.report import PerformanceReport
from logic.presets import PresetController

import globals.reportData as RD


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
        tick_minutes: int = 5
    ):
        self.tick_minutes = tick_minutes
        self.departures_per_hour = departures_per_hour
        self.landings_per_hour = landings_per_hour
        self.total_runways = total_runways
        self.departure_runways = departure_runways
        self.landing_runways = landing_runways
        self.mixed_runways = mixed_runways
        self.cancellation_time = cancellation_time
        self.current_time = datetime.now()
        
        self.generateRunway()
        self.generateQueue()
        # Initialises the reportData global variable
        RD.init()

    def generateSimulation(self, preset: int) -> bool: # Consider if a preset exists according to Fede
        self.generateRunway()
        self.generateQueue()
        return True

    def generatePlane(self, is_departure: bool) -> bool:
        p = Plane(is_departure)
        
        PresetController.plane_list.append(p) # Adds generated plane to preset storage list

        if is_departure:
            self.departure_queue.enqueue(p)
        else:
            self.landing_queue.enqueue(p)

        self.report.total_planes += 1 #to track total planes


    def generateQueue(self) -> bool: #departure and landing queue
        self.departure_queue = QueueController([], self.departure_list, True)
        self.landing_queue = QueueController([], self.landing_list, False)
        return True


    def generateRunway(self) -> bool:
        self.landing_list = []
        self.departure_list = []
        runway_num = 1
        for i in range(self.departure_runways):
            self.departure_list.append(Runway(True, False, runway_num, True, True))
            runway_num += 1

        for i in range(self.landing_runways):
            self.landing_list.append(Runway(False, False, runway_num, True, True))
            runway_num += 1
        
        for i in range(self.mixed_runways):
            temp = Runway(True, True, runway_num, True, True)
            self.landing_list.append(temp)
            self.departure_list.append(temp)
            runway_num += 1
        return True

    def update(self) -> bool:
        # tick_minutes controls how much simulated time passes each frame.
        # expected planes per tick = planes_per_hour × (tick_minutes / 60).
        # integer part generates fixed planes, fractional part handled randomly.
        
        self.current_time += timedelta(minutes=self.tick_minutes)
        #random planes per tick generation
        expected_departures = self.departures_per_hour * (self.tick_minutes / 60)
        expected_landings = self.landings_per_hour * (self.tick_minutes / 60)

        for _ in range(int(expected_departures)):
            self.generatePlane(True)

        for _ in range(int(expected_landings)):
            self.generatePlane(False)

        # fractional part
        if random.random() < (expected_departures % 1):
            self.generatePlane(True)

        if random.random() < (expected_landings % 1):
            self.generatePlane(False)
        #attempting to assign planes to available runways
        self.departure_queue.checkRunways()
        self.landing_queue.checkRunways()

        return True
    
