# QueueController Class
from datetime import datetime
from typing import List
from queue import Queue

from logic.models import Runway
from logic.plane import Plane, EmergencyStatus



class QueueController:
    def __init__(self, plane_queue: list[Plane], runway_list: list[Runway], is_departure: bool):
        self.plane_queue = plane_queue # A list, treated as a queue
        self.runway_list = runway_list
        self.is_departure = is_departure # true = takeoff, false = landing 

    def checkRunways(self): 
        for runway in self.runway_list:
            if runway.is_available and len(self.plane_queue) != 0:
                self.plane_queue.pop(0).goToRunway(runway.runway_number)

    def enqueue(self, p: Plane):
        self.plane_queue.append(p)

    def checkCancelTime(self) -> datetime:
        if self.is_departure:
            for plane in self.plane_queue:
                if plane.emergency_status == EmergencyStatus.NONE:
                    time = plane.target_time
                    # Call simulationController -> get the specified cancellation time threshold
                    # if over the threshold, cancel plane
        

    def planeEmergency(self, p: Plane) -> EmergencyStatus:
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

