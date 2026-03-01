# QueueController Class
from datetime import datetime
from typing import List
from queue import Queue

from logic.models import Runway
from logic.plane import Plane, EmergencyStatus

import logic.globals.reportData as RD
# from logic.simulation import SimulationController

class QueueController:
    def __init__(self, plane_queue: list[Plane], runway_list: list[Runway], is_departure: bool, sim):
        self.plane_queue = plane_queue # A list, treated as a queue
        self.runway_list = runway_list
        self.is_departure = is_departure # true = takeoff, false = landing 
        self.sim = sim


    # Runway algorithm - linearly search through the runway list, when one is available, direct the first plane to that runway
    def checkRunways(self): 
        for runway in self.runway_list:
            if runway.is_available and len(self.plane_queue) != 0:
                # Dircts the plane to the runway
                removed = self.plane_queue.pop(0)
                removed.goToRunway(runway.runway_number)
                self.sim.current_frame_actions.append([removed.plane_id, runway.runway_number])
                # Assigns the holding queue exit time to the plane object
                removed.left_hold = self.sim.getSimulationTime()
                delay = datetime.total_seconds(removed.left_hold - removed.entered_hold)
            
                # Adds the delay time to the report and decrements current queue size
                RD.reportData.arrival_delay_times.append(delay)
                RD.reportData.decQueueCurrent()


    def enqueue(self, p: Plane):
        # Adds plane to queue
        self.plane_queue.append(p)

        # Assigns holding queue entry time to plane object and increments current queue size
        p.entered_hold = self.sim.getSimulationTime()
        RD.reportData.incQueueCurrent()



    # (For landing only) Checks if emergency_time_left <= 0, then cancel
    # Then checks if the plane is over the user specified cancellation time, then cancel
    def checkCancelTime(self):
        if not self.is_departure and self.plane_queue[0].emergency_status != EmergencyStatus.NONE and self.plane_queue[0].emergency_time_left <= 0:
            self.plane_queue.pop(0)

        for plane in self.plane_queue:
            pass
            # SimulationController.cancellation_time
            # Needs to keep of current time (the 'now')]


    # Given a plane with an EmergencyStatus, it sets the emergency_time_left, and changes its place in the queue accordingly
    def planeEmergency(self, p: Plane):
        match (p.emergency_status):
            case EmergencyStatus.FUEL:
                p.emergency_time_left = 10
            case EmergencyStatus.HEALTH:
                p.emergency_time_left = 20
            case EmergencyStatus.MECHANICAL:
                p.emergency_time_left = 30
        temp = 0
        for plane in self.plane_queue:
                if plane.emergency_time_left < p.emergency_time_left:
                    temp+= 1
                else:
                    self.plane_queue.insert(temp, p)
                    break

