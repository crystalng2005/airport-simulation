# Plane and Runway Classes

from enum import Enum
from datetime import datetime
import random

class Runway:
    def __init__(self, is_departure: bool, mixed_mode: bool, runway_number: int, is_available: bool, is_operational: bool, probabilities: list[float], opening: float):
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

        # Maximum number of planes that have passed through this runway 
        self.maxPlanes = 0 


    def openRunway(self):
        """
        Opens the runway by setting closed to false and is operational to true
        """
        self.closed = False
        self.is_operational = True


    def closeRunway(self):
        """
        Closes the runway by setting closed to true and is operational to false
        """
        self.closed = True
        self.is_operational = False

    def checkClosed(self) -> bool:
        """
        Returns true if a runway is closed, false otherwise
        """
        return self.closed
    

    def set_user_settings(self, probabilities):
        """
        Uses the probabilities input by the user to set the probabilities of runway closure from the list.
        Called on object generation.
        """
        self.user_weather = probabilities[0]
        self.user_safety = probabilities[1]
        self.user_maintenance = probabilities[2]
        self.user_construction = probabilities[3]

    
    def updateStatus(self) -> bool:
        """
        Checks if the runway is closed.
        If closed, offers the random chance for runway to open based on user input probability.
        If open, offers the chance to close it.

        Uses the user probability to generate a value, if this is 1, then the runway closes or opens
        depending on the point in the if statement.s

        Note that the default values entered in the user input boxes are based on reasonable estimates
        for the probabilities of an event occuring (e.g. weather related events being the most common,
        planned construction the least common).

        """
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


        