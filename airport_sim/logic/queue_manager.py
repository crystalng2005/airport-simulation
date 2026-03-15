# QueueController Class
from logic.models import Runway
from logic.plane import Plane, EmergencyStatus

from logic.currentFrameActions import currentFrameActions
import logic.globals.reportData as RD

MINUTES_PER_TICK = 5

class QueueController:
    def __init__(self, plane_queue: list[Plane], runway_list: list[Runway], is_departure: bool, sim) -> None:
        """
        Initialises the QueueController.

        The controller manages a queue of planes waiting to either take off
        or land and assigns them to available runways.

        Args:
            plane_queue: A list of Plane objects representing the holding queue.
            runway_list: A list of Runway objects that planes can be assigned to.
            is_departure: True if the queue is for departures, False if it is for arrivals.
            sim: Reference to the SimulationController used to access simulation time.
        """
        self.plane_queue = plane_queue # A list, treated as a queue
        self.runway_list = runway_list
        self.is_departure = is_departure # true = takeoff, false = landing 
        self.sim = sim
        self.current_frame_actions = []
        self.even_turn = False

    def check_runways(self) -> None:
        """
        Checks the runway list and assigns planes from the queue to available runways.

        Each runway is checked to determine if it can accept another plane. If a runway
        has available capacity and the queue is not empty, the next plane in the queue
        is directed to that runway.

        For mixed-mode runways, landing and departure access alternates every tick
        using the even_turn flag to prevent starvation of either queue.

        When a plane leaves the queue:
        - It is assigned to a runway.
        - Delay and holding time statistics are calculated.
        - The relevant metrics in reportData are updated.
        """ 
        if self.even_turn: self.even_turn = False
        else: self.even_turn = True

        checked = 0
        while checked < len(self.runway_list):
            checked = 0
            for runway in self.runway_list:
                #if not runway.is_operational:
                #    print("closed11!!")
                if runway.max_planes < 5 and self.plane_queue and runway.is_operational: # NOTE: added check for runway closure
                    # Alternates each tick who can use mixed mode (allowing departure to use it too)
                    if self.even_turn == True and self.is_departure == False and runway.mixed_mode == True:
                        checked += 1
                        continue

                    # Directs the plane to the runway
                    runway.max_planes += 1
                    removed = self.plane_queue.pop(0)
                    removed.go_to_runway(runway.runway_number)
                    currentFrameActions.current_frame_actions.append([removed.callsign, runway.runway_number])
                    # Assigns the holding queue exit time to the plane object
                    removed.left_hold = self.sim.get_tick_time() * MINUTES_PER_TICK 
                    delay = round(removed.left_hold - removed.tick_actual_time) 
                    hold_time = round(removed.left_hold - removed.entered_hold)
                
                    # Adds the delay time and wait time to the report and decrements current queue size
                    if removed.is_departure:
                        RD.reportData.take_off_delays.append(delay)
                    else:
                        RD.reportData.arrival_delay_times.append(delay)

                    RD.reportData.wait_times.append(delay)
                    RD.reportData.hold_times.append(hold_time)
                    RD.reportData.tot_wait_time += hold_time
                    RD.reportData.dec_queue_current()
                else:
                    checked += 1

    def enqueue(self, p: Plane) -> None:
        """
        Adds a plane to the queue.

        If the plane has an emergency status it will be inserted into the queue
        according to its emergency priority. Otherwise the plane is appended
        to the end of the queue.

        The time at which the plane enters the holding queue is recorded and
        the queue size statistics are updated.

        Args:
            p: The Plane object to add to the queue.
        """
        if(p.emergency_status != EmergencyStatus.NONE): 
            self.plane_emergency(p)
        else:
            self.plane_queue.append(p)

        # Assigns holding queue entry time to plane object and increments current queue size
        p.entered_hold = self.sim.get_tick_time() * MINUTES_PER_TICK 
        RD.reportData.inc_queue_current()

    def check_cancel_time(self) -> None:
        """
        Checks whether planes should be removed from the queue due to
        emergencies or cancellation limits.

        For landing queues:
        - If a plane has an emergency and its emergency_time_left reaches zero,
          the plane is diverted and removed from the queue.

        For departure queues:
        - If a plane exceeds its cancellation_time it is cancelled and removed
          from the queue.

        All relevant diversion and cancellation statistics are updated in
        reportData.
        """
        if len(self.plane_queue) == 0:
            return

        # If the emergency time exceeds the limit, diverts the plane
        for plane in self.plane_queue[:]:
            if (not self.is_departure) and plane.emergency_status != EmergencyStatus.NONE and plane.emergency_time_left <= 0:
                plane.divert()
                self.plane_queue.remove(plane)
                RD.reportData.diversions += 1

        # If the plane exceeds the cancellation time
        i = 0
        while i < len(self.plane_queue):
            plane = self.plane_queue[i]
            if plane.cancellation_time <= 0 and self.is_departure:
                plane.cancel()
                self.plane_queue.pop(i)
                RD.reportData.cancellations += 1
            else:
                i += 1

    def plane_emergency(self, p: Plane) -> None:
        """
        Handles the insertion of a plane with an emergency into the queue.

        The plane's emergency_time_left is set depending on the type of
        emergency (fuel, health, or mechanical). The plane is then placed
        in the queue according to its emergency priority so that planes
        with more urgent emergencies are positioned closer to the front.

        The emergency event is also recorded in the current frame actions.

        Args:
            p: The Plane object experiencing an emergency.
        """
        currentFrameActions.current_frame_actions.append([p.callsign, "emergency"])
        if p in self.plane_queue:
            self.plane_queue.remove(p)

        # Assings time based on emergency status
        match (p.emergency_status):
            case EmergencyStatus.FUEL:
                p.emergency_time_left = 10
            case EmergencyStatus.HEALTH:
                p.emergency_time_left = 20
            case EmergencyStatus.MECHANICAL:
                p.emergency_time_left = 30
        
        # Uses emergency time left to modify its queue position
        inserted = False
        for i, plane in enumerate(self.plane_queue):
            if plane.emergency_time_left == 0 or plane.emergency_time_left >= p.emergency_time_left:
                self.plane_queue.insert(i, p)
                inserted = True
                break
        if not inserted:
            self.plane_queue.append(p)