# Plane and Runway Classes

from enum import Enum
from datetime import datetime

class EmergencyStatus(Enum):
    NONE = 0
    FUEL = 1
    HEALTH = 2
    MECHANICAL = 3


class Plane:
    def __init__(self, callsign: str, origin: str, destination: str, targetTime: datetime, actualTime: datetime, isDeparture: bool, fuelLevel: float, emergencyStatus: enum, currentLocation: str) -> bool: # actually will this return smth
        pass

class Runway:
    def __init__(self, isDeparture: bool, mixedMode: bool, runwayNumber: int, isAvailable: bool, isOperational: bool):
        pass