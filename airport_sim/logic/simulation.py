# Simulation Controller
from datetime import datetime, timedelta
import random

from logic.plane import Plane
from logic.models import Runway
from logic.queue_manager import QueueController
# from airport_sim.logic.report import PerformanceReport
from logic.presets import PresetController

import logic.globals.reportData as RD



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
        total_simulation_minutes: int,
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
        self.start_time = datetime.now()
        self.current_time = self.start_time
        self.end_time = self.start_time + timedelta(minutes=total_simulation_minutes)
        self.simulation_finished = False

        self.preset_mode = False
        self.preset_planes = []
        
        self.generateRunway()
        self.generateQueue()
        # Initialises the reportData global variable
        RD.init(total_runways, landings_per_hour, self.current_time)

    def generateSimulation(self, preset: int) -> bool: # Consider if a preset exists according to Fede
        if preset is None:
            self.generateRunway()
            self.generateQueue()
            return True

        preset_controller = PresetController()

        if not preset_controller.loadPreset(preset):
            return False

        # override runway configurations
        self.departure_runways = preset_controller.departure_runways
        self.landing_runways = preset_controller.landing_runways
        self.mixed_runways = preset_controller.mixed_runways

        self.generateRunway()
        self.generateQueue()

        for plane in preset_controller.plane_list:
            if plane.is_departure:
                self.departure_queue.enqueue(plane)
            else:
                self.landing_queue.enqueue(plane)

        RD.reportData = preset_controller.report

        self.preset_mode = True

        return True
        




    def getSimulationTime(self) -> datetime:
        return self.current_time



    def generatePlane(self, is_departure: bool) -> bool:
        p = Plane(is_departure)
        
        PresetController.plane_list.append(p) # Adds generated plane to preset storage list

        if is_departure:
            self.departure_queue.enqueue(p)
        else:
            self.landing_queue.enqueue(p)

        # Increases total number of planes
        RD.reportData.total_planes += 1


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
        if self.simulation_finished:
            return False

        if self.current_time >= self.end_time:
            self.simulation_finished = True
            return False
        
        self.current_time += timedelta(minutes=self.tick_minutes)
        #random planes per tick generation
        if not self.preset_mode:
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
    
