"""Simulation Controller"""

from datetime import datetime, timedelta
import random

from logic.plane import Plane
from logic.models import Runway
from logic.queue_manager import QueueController
from logic.presets import PresetController
from logic.results import ResultsController
from logic.currentFrameActions import currentFrameActions

import logic.globals.reportData as RD


class SimulationController:
    """
    Main controller responsible for managing the airport simulation.

    It coordinates plane generation, runway management, queue processing,
    emergency events, and simulation timing. The controller advances the
    simulation in fixed time steps (ticks) and updates the state of all
    simulation components accordingly.
    """

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
        mechanical_emergency_prob: float,
        health_emergency_prob: float,
        fuel_emergency_prob: float,
        weather_closure_prob: float,
        maintenance_closure_prob: float,
        safety_closure_prob: float,
        construction_closure_prob: float,
        tick_minutes: int = 5
    ):
        """
        Initialise the simulation with configuration parameters.

        Parameters define traffic flow, runway configuration, emergency
        probabilities, closure probabilities, and total simulation duration.
        """

        self.tick_minutes = tick_minutes
        self.departures_per_hour = departures_per_hour
        self.landings_per_hour = landings_per_hour
        self.total_runways = total_runways
        self.departure_runways = departure_runways
        self.landing_runways = landing_runways
        self.mixed_runways = mixed_runways
        self.all_runways = []

        """Probabilities for plane emergencies and runway closures."""
        self.plane_emergency_prob = [
            mechanical_emergency_prob,
            health_emergency_prob,
            fuel_emergency_prob
        ]

        self.runway_closure_prob = [
            weather_closure_prob,
            maintenance_closure_prob,
            safety_closure_prob,
            construction_closure_prob
        ]

        """Simulation time tracking."""
        self.cancellation_time = cancellation_time
        self.current_time = datetime(2000, 1, 1, 0, 0)
        self.ticks_elapsed = 0
        self.end_time = self.current_time + timedelta(minutes=total_simulation_minutes)

        """Simulation state flags."""
        self.simulation_finished = False
        self.preset_mode = False

        """Dictionary storing aircraft indexed by callsign."""
        self.planes_by_call_sign = {}

        """Controller used to manage preset storage."""
        self.preset_controller = PresetController()

        """Initial runway and queue generation."""
        self.generateRunway()
        self.generateQueue()

        """Initialise global reporting structure."""
        RD.init(
            total_runways,
            mixed_runways,
            departure_runways,
            landing_runways,
            landings_per_hour,
            self.current_time
        )

    def generateSimulation(self, preset: int) -> bool:
        """
        Initialise simulation using a preset configuration if provided.

        If no preset is given, the simulation is generated using the
        current configuration parameters.
        """

        if preset is None:
            self.generateRunway()
            self.generateQueue()
            return True

        preset_controller = PresetController()

        if not preset_controller.loadPreset(preset):
            return False

        self.departure_runways = preset_controller.departure_runways
        self.landing_runways = preset_controller.landing_runways
        self.mixed_runways = preset_controller.mixed_runways

        self.generateRunway()
        self.generateQueue()

        """Load aircraft stored in the preset."""
        self.preset_planes = preset_controller.plane_list.copy()

        """Load the preset performance report."""
        RD.reportData = preset_controller.report

        self.preset_mode = True
        return True

    def getSimulationTime(self) -> datetime:
        """Return the current simulated time."""
        return self.current_time

    def generatePlane(self, is_departure: bool) -> bool:
        """
        Create a new aircraft and add it to the appropriate queue.
        """

        if is_departure:
            p = Plane(
                is_departure,
                self.departure_queue,
                self.cancellation_time,
                self.plane_emergency_prob
            )
        else:
            p = Plane(
                is_departure,
                self.landing_queue,
                self.cancellation_time,
                self.plane_emergency_prob
            )

        p.generated_at = self.current_time
        self.planes_by_call_sign[p.callsign] = p
        self.preset_controller.plane_list.append(p)

        if is_departure:
            self.departure_queue.enqueue(p)
            currentFrameActions.current_frame_actions.append(
                [p.callsign, "spawnDeparture"]
            )
        else:
            self.landing_queue.enqueue(p)
            currentFrameActions.current_frame_actions.append(
                [p.callsign, "spawnLanding"]
            )

        RD.reportData.total_planes += 1

    def getAircraftByCallSign(self, plane_call_sign: str):
        """Return aircraft object matching the given callsign."""
        return self.planes_by_call_sign.get(plane_call_sign, None)

    def generateQueue(self) -> bool:
        """
        Create landing and departure queues that manage aircraft waiting
        for runway allocation.
        """

        self.departure_queue = QueueController([], self.departure_list, True, self)
        self.landing_queue = QueueController([], self.landing_list, False, self)
        return True

    def getCurrentFrameActions(self):
        """
        Return actions recorded during the current simulation frame.
        """
        return currentFrameActions.current_frame_actions

    def generateRunway(self) -> bool:
        """
        Generate runway objects based on configured runway counts.

        Runways may operate in departure-only, landing-only,
        or mixed mode.
        """

        self.landing_list = []
        self.departure_list = []
        self.all_runways = []
        runway_num = 1

        for _ in range(self.departure_runways):
            runway = Runway(True, False, runway_num, True, True, self.runway_closure_prob)
            self.departure_list.append(runway)
            self.all_runways.append(runway)
            runway_num += 1

        for _ in range(self.landing_runways):
            runway = Runway(False, False, runway_num, True, True, self.runway_closure_prob)
            self.landing_list.append(runway)
            self.all_runways.append(runway)
            runway_num += 1

        for _ in range(self.mixed_runways):
            temp = Runway(True, True, runway_num, True, True, self.runway_closure_prob)
            self.landing_list.append(temp)
            self.departure_list.append(temp)
            self.all_runways.append(temp)
            runway_num += 1

        return True

    def get_runway_statuses(self):
        """
        Return a list indicating whether each runway is open or closed.
        """

        statuses = []
        for runway in self.all_runways:
            statuses.append(not runway.checkClosed())

        return statuses

    def get_runway_modes(self):
        """
        Return the operational mode of each runway.

        Mixed mode = 0  
        Departure only = -1  
        Arrival only = 1
        """

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
        """Return the total number of runways."""
        return self.total_runways

    def end_simulation(self):
        """
        Finish the simulation, generate reports, and store results.
        """

        if self.simulation_finished:
            return False

        self.simulation_finished = True
        RD.reportData.setFinishTime(self.current_time)
        RD.reportData.generateReport()

        self.preset_controller.departure_runways = self.departure_runways
        self.preset_controller.landing_runways = self.landing_runways
        self.preset_controller.mixed_runways = self.mixed_runways
        self.preset_controller.report = RD.reportData
        self.preset_controller.savePreset()

        self.results_controller = ResultsController()
        self.results_controller.saveResult()

        return False

    def get_tick_time(self):
        """Return the number of ticks elapsed."""
        return self.ticks_elapsed

    def update(self) -> bool:
        """
        Advance the simulation by one tick.

        Each tick represents a fixed number of simulated minutes.
        During a tick the following processes occur:

        - Aircraft fuel decreases and emergencies may trigger
        - Runway status updates (open/close events)
        - Queues process aircraft waiting for runways
        - New aircraft spawn based on traffic rates or presets
        """

        self.ticks_elapsed += 1

        currentFrameActions.current_frame_actions = []

        for runway in self.all_runways:
            runway.maxPlanes = 0

        if self.current_time >= self.end_time:
            return self.end_simulation()

        self.current_time += timedelta(minutes=self.tick_minutes)

        for plane in self.planes_by_call_sign.values():
            if not plane.left_simulation:
                plane.decrease_fuel()
                plane.update_emergency()

        for runway in self.all_runways:
            runway.updateStatus()

        self.landing_queue.checkCancelTime()
        self.departure_queue.checkCancelTime()

        self.landing_queue.checkRunways()
        self.departure_queue.checkRunways()

        if self.preset_mode:

            planes_to_spawn = [
                p for p in self.preset_planes
                if p.generated_at <= self.current_time
            ]

            for plane in planes_to_spawn:

                if plane.is_departure:
                    self.departure_queue.enqueue(plane)
                else:
                    self.landing_queue.enqueue(plane)

                self.planes_by_call_sign[plane.callsign] = plane

            self.preset_planes = [
                p for p in self.preset_planes
                if p.generated_at > self.current_time
            ]

        if not self.preset_mode:

            expected_departures = self.departures_per_hour * (self.tick_minutes / 60)
            expected_landings = self.landings_per_hour * (self.tick_minutes / 60)

            for _ in range(int(expected_departures)):
                self.generatePlane(True)

            for _ in range(int(expected_landings)):
                self.generatePlane(False)

            if random.random() < (expected_departures % 1):
                self.generatePlane(True)

            if random.random() < (expected_landings % 1):
                self.generatePlane(False)

        return True