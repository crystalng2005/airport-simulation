# Plane and Runway Classes

from enum import Enum
from datetime import datetime

class Runway:
    def __init__(self, is_departure: bool, mixed_mode: bool, runway_number: int, is_available: bool, is_operational: bool):
        self.is_departure = is_departure
        self.mixed_mode = mixed_mode
        self.runway_number = runway_number
        self.is_available = is_available
        self.is_operational = is_operational
