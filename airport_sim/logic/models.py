# Plane and Runway Classes

from enum import Enum
from datetime import datetime
import random

class Runway:
    def __init__(self, is_departure: bool, mixed_mode: bool, runway_number: int, is_available: bool, is_operational: bool):
        self.is_departure = is_departure
        self.mixed_mode = mixed_mode
        self.runway_number = runway_number
        self.is_available = is_available
        self.is_operational = is_operational
        self.closed = False
        self.user_settings = False 
        self.user_weather = 0
        self.user_maintenance = 0
        self.user_safety = 0
        self.user_construction = 0
        self.maxPlanes = 0


    # Function to open and close runways, can be called outside the class if necessary
    def openRunway(self):
        self.closed = False

    def closeRunway(self):
        self.closed = True

    def checkStatus(self):
        return self.closed
    

    # Checks if the runway is closed
    # If closed, offers the random chance for runway to open
    # If open, offers the chance to close it
    def updateStatus(self):
        if not self.user_settings:
            if self.closed:
                val = random.randint(0,100)
                if val <= 10:
                    self.openRunway()
                return self.closed
            else:
                weather = random.randint(0,1000)
                maintenance = random.randint(0,10000)
                safety = random.randint(0,10000)
                construction = random.randint(0,30000)

                if weather <= 10:
                    self.closeRunway()
                elif maintenance <= 10:
                    self.closeRunway()
                elif safety <= 10:
                    self.closeRunway()
                elif construction <= 10:
                    self.closeRunway()
                
                return self.closed
        else:
            # Chance of opening closed runway randomly
            if self.closed:
                val = random.randint(0,100)
                if val <= 10:
                    self.openRunway()
                return self.closed
            else:
                weather = random.randint(0,1/self.user_weather)
                maintenance = random.randint(0,self.user_maintenance)
                safety = random.randint(0,self.user_safety)
                construction = random.randint(0,self.user_construction)

                if weather <= 10:
                    self.closeRunway()
                elif maintenance <= 10:
                    self.closeRunway()
                elif safety <= 10:
                    self.closeRunway()
                elif construction <= 10:
                    self.closeRunway()
                
                return self.closed

        

