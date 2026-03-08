# QueueController Class
from datetime import datetime, timedelta
from typing import List
from queue import Queue

from logic.models import Runway
from logic.plane import Plane, EmergencyStatus

import logic.globals.reportData as RD
from logic.currentFrameActions import currentFrameActions
# from logic.simulation import SimulationController

class QueueController:
    def __init__(self, plane_queue: list[Plane], runway_list: list[Runway], is_departure: bool, sim):
        self.plane_queue = plane_queue # A list, treated as a queue
        self.runway_list = runway_list
        self.is_departure = is_departure # true = takeoff, false = landing 
        self.sim = sim
        self.current_frame_actions = []
        self.evenTurn = False


    # Runway algorithm - linearly search through the runway list, when one is available, direct the first plane to that runway
    def checkRunways(self): 
        if self.evenTurn: self.evenTurn = False
        else: self.evenTurn = True

        checked = 0
        while checked < len(self.runway_list):
            checked = 0
            for runway in self.runway_list:
                if runway.maxPlanes < 5 and len(self.plane_queue) != 0:
                    # Alternates each tick who can use mixed mode (allowing departure to use it too)
                    if self.evenTurn == True and self.is_departure == False and runway.mixed_mode == True:
                        checked += 1
                        continue

                    # Directs the plane to the runway
                    runway.maxPlanes += 1
                    removed = self.plane_queue.pop(0)
                    removed.goToRunway(runway.runway_number)
                    currentFrameActions.current_frame_actions.append([removed.callsign, runway.runway_number])
                    # Assigns the holding queue exit time to the plane object
                    removed.left_hold = self.sim.getSimulationTime()
                    delay = (removed.left_hold - removed.entered_hold).total_seconds()
                
                    # Adds the delay time to the report and decrements current queue size
                    RD.reportData.arrival_delay_times.append(delay)
                    RD.reportData.decQueueCurrent()
                else:
                    checked += 1


    def enqueue(self, p: Plane):
        # Adds plane to queue
        if(p.emergency_status != EmergencyStatus.NONE): 
            self.planeEmergency(p)
        else:
            self.plane_queue.append(p)

        # Assigns holding queue entry time to plane object and increments current queue size
        p.entered_hold = self.sim.getSimulationTime()
        RD.reportData.incQueueCurrent()



    # (For landing only) Checks if emergency_time_left <= 0, then cancel
    # Then checks if the plane is over the user specified cancellation time, then cancel
    def checkCancelTime(self):
        if len(self.plane_queue) == 0:
            return

        # If the emergency time exceeds the limit, diverts the plane
        if not self.is_departure and self.plane_queue[0].emergency_status != EmergencyStatus.NONE and self.plane_queue[0].emergency_time_left <= 0:
            # Cancels the plane (same logic for diversions)
            self.plane_queue[0].cancel()
            self.plane_queue.pop(0)
            # Increments diversions in the report
            RD.reportData.diversions += 1

        # If the plane exceeds the cancellation time
        if self.is_departure:
            for plane in self.plane_queue:
                if plane.cancellation_time <= 0:
                    # Cancels the plane and removes the queue
                    plane.cancel()
                    self.plane_queue.remove(plane)
                    RD.reportData.cancellations += 1



    # Given a plane with an EmergencyStatus, it sets the emergency_time_left, and changes its place in the queue accordingly
    def planeEmergency(self, p: Plane):
        currentFrameActions.current_frame_actions.append([p.callsign, "emergency"])
        match (p.emergency_status):
            case EmergencyStatus.FUEL:
                p.emergency_time_left = 10
            case EmergencyStatus.HEALTH:
                p.emergency_time_left = 20
            case EmergencyStatus.MECHANICAL:
                p.emergency_time_left = 30
        inserted = False
        for i, plane in enumerate(self.plane_queue):
            if plane.emergency_time_left == 0 or plane.emergency_time_left >= p.emergency_time_left:
                self.plane_queue.insert(i, p)
                inserted = True
                break
        if not inserted:
            self.plane_queue.append(p)


