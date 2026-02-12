# Plane and Runway Classes

from enum import Enum
from datetime import datetime


# hello


class EmergencyStatus(Enum):
    NONE = 0
    FUEL = 1
    HEALTH = 2
    MECHANICAL = 3


class Plane:
    def __init__(
        self,
        callsign: str,
        origin: str,
        destination: str,
        is_departure: bool,
        fuel_level: float,
        emergency_status: EmergencyStatus = EmergencyStatus.NONE,
    ):
        self.callsign = callsign
        self.origin = origin
        self.destination = destination
        self.is_departure = is_departure
        self.fuel_level = fuel_level
        self.emergency_status = emergency_status
        self.target_time = None
        self.actual_time = None
        self.current_location = origin

    def decreaseFuel(self) -> bool:
        pass

    def goToRunway(self, runway: int) -> bool:
        pass

    def cancel(self) -> bool:
        pass

    def hasEmergency(self) -> bool:
        pass

class Runway:
    def __init__(self, is_departure: bool, mixed_mode: bool, runway_number: int, is_available: bool, is_operational: bool):
        pass