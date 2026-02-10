# QueueController Class
from typing import List
from queue import Queue
from models import Plane, Runway, EmergencyStatus
from datetime import datetime

class QueueController:
    def __init__(self, plane_queue: Queue[Plane], runway_list: List[Runway], is_departure: bool):
        self.plane_queue = plane_queue
        self.runway_list = runway_list
        self.is_departure = is_departure

    def checkRunways(self) -> bool: # I dont know what this returns
        pass

    def enqueue(self, p: Plane) -> bool:
        pass

    def checkCancelTime(self) -> datetime:
        pass

    def planeEmergency(self, p: Plane) -> EmergencyStatus:
        pass
