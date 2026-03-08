# Simulation Controller
from datetime import datetime, timedelta
import random

from logic.plane import Plane
from logic.models import Runway
from logic.queue_manager import QueueController
# from airport_sim.logic.report import PerformanceReport
from logic.presets import PresetController
from logic.currentFrameActions import currentFrameActions

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
        self.all_runways = []

        self.cancellation_time = cancellation_time
        self.current_time = datetime(2000, 1, 1, 0, 0)
        self.end_time = self.current_time + timedelta(minutes=total_simulation_minutes)
        
        self.simulation_finished = False

        self.preset_mode = False

        self.planes_by_call_sign = {}
        self.preset_controller = PresetController()
        
        self.generateRunway()
        self.generateQueue()
        # Initialises the reportData global variable
        RD.init(total_runways, mixed_runways, departure_runways, landing_runways, landings_per_hour, self.current_time)


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

        self.preset_planes = preset_controller.plane_list.copy()

        RD.reportData = preset_controller.report

        self.preset_mode = True

        return True
        




    def getSimulationTime(self) -> datetime:
        return self.current_time



    def generatePlane(self, is_departure: bool) -> bool:
        p = Plane(is_departure)
        p.generated_at = self.current_time
        self.planes_by_call_sign[p.callsign] = p
        
        self.preset_controller.plane_list.append(p) # Adds generated plane to preset storage list

        if is_departure:
            self.departure_queue.enqueue(p)
            currentFrameActions.current_frame_actions.append([p.callsign, "spawnDeparture"])
        else:
            self.landing_queue.enqueue(p)
            currentFrameActions.current_frame_actions.append([p.callsign, "spawnLanding"])

        # Increases total number of planes
        RD.reportData.total_planes += 1

    def getAircraftByCallSign(self, plane_call_sign: str):
        return self.planes_by_call_sign.get(plane_call_sign, None)


    def generateQueue(self) -> bool: #departure and landing queue
        self.departure_queue = QueueController([], self.departure_list, True, self)
        self.landing_queue = QueueController([], self.landing_list, False, self)
        return True

    def getCurrentFrameActions(self):
        return currentFrameActions.current_frame_actions

    def generateRunway(self) -> bool:
        self.landing_list = []
        self.departure_list = []
        self.all_runways = []
        runway_num = 1
        for i in range(self.departure_runways):
            runway = Runway(True, False, runway_num, True, True)
            self.departure_list.append(runway)
            self.all_runways.append(runway)
            runway_num += 1

        for i in range(self.landing_runways):
            runway = Runway(False, False, runway_num, True, True)
            self.landing_list.append(runway)
            self.all_runways.append(runway)
            runway_num += 1
        
        for i in range(self.mixed_runways):
            temp = Runway(True, True, runway_num, True, True)
            self.landing_list.append(temp)
            self.departure_list.append(temp)
            self.all_runways.append(temp)
            runway_num += 1
        return True
    
    def get_runway_statuses(self):
        statuses = []
        for runway in self.all_runways:
            statuses.append(runway.checkStatus())

        return statuses
    

    def get_runway_modes(self):
        modes = []
        for runway in self.all_runways:
            if runway.mixed_mode:
                modes.append(0)
            else:
                if runway.is_departure:
                    modes.append(-1)
                else:
                    modes.append(1)

        return modes
    
    def get_runway_num(self):
        return self.total_runways
    
    def end_simulation(self):
        if self.simulation_finished:
            return False

        self.simulation_finished = True
        RD.reportData.setFinishTime(self.current_time)
        RD.reportData.generateReport()
        return False

    def update(self) -> bool:
        # tick_minutes controls how much simulated time passes each frame.
        # expected planes per tick = planes_per_hour × (tick_minutes / 60).
        # integer part generates fixed planes, fractional part handled randomly.

        currentFrameActions.current_frame_actions = []



        if self.current_time >= self.end_time:
            return self.end_simulation()
        
        self.current_time += timedelta(minutes=self.tick_minutes)

        # Process existing queue first — assign waiting planes to available runways
        self.departure_queue.checkRunways()
        self.landing_queue.checkRunways()

        # Then generate new planes (they will wait at least one tick in the queue)
        #random planes per tick generation

        if self.preset_mode:
            planes_to_spawn = [p for p in self.preset_planes if p.generated_at <= self.current_time]

            for plane in planes_to_spawn:
                if plane.is_departure:
                    self.departure_queue.enqueue(plane)
                else:
                    self.landing_queue.enqueue(plane)
                self.planes_by_call_sign[plane.callsign] = plane

            self.preset_planes = [p for p in self.preset_planes if p.generated_at > self.current_time]


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

        return True