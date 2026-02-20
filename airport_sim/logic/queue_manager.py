# QueueController Class
from datetime import datetime
from typing import List
from queue import Queue

from logic.models import Runway
from logic.plane import Plane, EmergencyStatus
from logic.simulation import SimulationController

import globals.reportData as RD


class QueueController:
    def __init__(self, plane_queue: list[Plane], runway_list: list[Runway], is_departure: bool):
        self.plane_queue = plane_queue # A list, treated as a queue
        self.runway_list = runway_list # List of suitable runways (e.g. if is_departure == true, then should be just mixed mode / take off runways)
        self.is_departure = is_departure # true = takeoff, false = landing 

    # Runway algorithm - linearly search through the runway list, when one is available, direct the first plane to that runway
    def checkRunways(self): 
        for runway in self.runway_list:
            if runway.is_available and len(self.plane_queue) != 0:
                RD.reportData.decQueueCurrent()
                self.plane_queue.pop(0).goToRunway(runway.runway_number)


    # Adds a plane to the back of the queue
    def enqueue(self, p: Plane):
        RD.reportData.incQueueCurrent()
        self.plane_queue.append(p)



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
        # Places plane in queue based on asc. emergency_time_left
        for plane in self.plane_queue:
                if plane.emergency_time_left < p.emergency_time_left:
                    temp+= 1
                else:
                    self.plane_queue.insert(temp, p)
                    break

