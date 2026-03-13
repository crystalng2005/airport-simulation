# Plane and Runway Classes

from enum import Enum
from datetime import datetime
import random

class Runway:
    def __init__(self, is_departure: bool, mixed_mode: bool, runway_number: int, is_available: bool, is_operational: bool, probabilities, opening: float):
        # Values for defining the runway
        self.is_departure = is_departure
        self.mixed_mode = mixed_mode
        self.runway_number = runway_number

        # Values for the current state of the runway
        self.is_available = is_available
        self.is_operational = is_operational
        self.closed = False

        # User settings
        self.set_user_settings(probabilities)
        self.opening_probability = opening

        # Maximum number of planes that have passed through this runway (?)
        self.maxPlanes = 0 # (?)


    # Functions to open and close runways, can be called outside the class if necessary
    def openRunway(self):
        self.closed = False
        self.is_operational = True

    def closeRunway(self):
        #print("closed!")
        self.closed = True
        self.is_operational = False

    # Returns the status of the runway
    def checkClosed(self):
        return self.closed
    

    def set_user_settings(self, probabilities):
        self.user_weather = probabilities[0]
        self.user_safety = probabilities[1]
        self.user_maintenance = probabilities[2]
        self.user_construction = probabilities[3]

    # Checks if the runway is closed
    # If closed, offers the random chance for runway to open
    # If open, offers the chance to close it
    def updateStatus(self):
        # Chance of opening closed runway randomly
        if self.closed:
            opening = random.randint(0,int(1/self.opening_probability)) if self.opening_probability !=0 else 2
            if opening == 1:
                self.openRunway()
            return self.closed
        else:
            weather = random.randint(0,int(1/self.user_weather)) if self.user_weather != 0 else 2
            maintenance = random.randint(0,int(1/self.user_maintenance)) if self.user_maintenance != 0 else 2
            safety = random.randint(0,int(1/self.user_safety)) if self.user_safety != 0 else 2
            construction = random.randint(0,int(1/self.user_construction)) if self.user_safety != 0 else 2

            # Checks if any closures have been generated
            if weather == 1 or self.user_weather == 1:
                self.closeRunway()
            elif maintenance == 1 or self.user_maintenance == 1:
                self.closeRunway()
            elif safety == 1 or self.user_safety == 1:
                self.closeRunway()
            elif construction == 1 or self.user_construction == 1:
                self.closeRunway()
                
        return self.closed


        
"""
# Placeholder values
        weather = 0
        maintenance = 0
        safety = 0
        construction = 0
        # If no user values have been defined, use presets
        if not self.user_settings:
            if self.closed:
                val = random.randint(0,100)
                if val <= 10:
                    self.openRunway()
                return self.closed
            else:
                # Weather is the most likely, construction least likely
                weather = random.randint(0,1000)
                maintenance = random.randint(0,7000)
                safety = random.randint(0,15000)
                construction = random.randint(0,30000)


        # If user values have been set, uses these here
        else:

"""
