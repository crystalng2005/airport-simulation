import datetime
from enum import Enum 
from numpy import random
import linecache

# Emergency status enum, used with the plane class
class EmergencyStatus(Enum):
    NONE = 0
    FUEL = 1
    HEALTH = 2
    MECHANICAL = 3

"""
keep here as reference for data types
self,
callsign: str,
origin: str,
destination: str,
is_departure: bool,
fuel_level: float,
target_time: datetime,
actual_time: datetime
"""

class Plane:
    plane_num = 0

    # NOTE: if storing the origin/destination as an airport or airport code, a 'rough' dataset may have to suffice since full updated information isn't readily available
    def __init__(self, is_departure: bool):
        self.callsign = self.genCallsigns()
        self.origin = self.genOrigin()
        self.destination = self.genDestination()
        self.is_departure = is_departure
        self.fuel_level = self.genFuel()
        self.emergency_status = EmergencyStatus.NONE
        # NOTE: NEED DEPARTURE AND ARRIVAL TIMES SEPARATELY
        self.target_time = self.genTargetTime()
        self.actual_time = self.genActualTime
        self.current_location = self.origin
        self.emergency_time_left = 0 # Initially 0, will be decreased in decrease fuel when emergency arises
        plane_num += 1

    # ------- CONSTRUCTOR ------ #
    def __new__(self):
        pass

    # ------- PLANE GENERATION FUNCTIONS ------- #
    def genCallsign(self):
        # For this, number the planes, can just keep a global count of current value
        # If want to, could preface with company name or something
        return "PLN" + str(self.plane_num)

# for the following two will create a txt file of airport AITA codes, names and countries
    def genOrigin(self):
        line = linecache.getline('iata.txt', random.randint(3,535))
        wordCount = 0
        code = ""
        airport = ""
        country = ""
        for l in line:
            if l != "|":
                if wordCount == 0:
                    code += l
                elif wordCount == 1:
                    airport += l
                elif wordCount == 2:
                    country += l
            else:
                wordCount += 1
        
        code = code.strip()
        aiport = airport.strip()
        country = country.strip()

        return code



    def genDestination(self):
        first = True
        while first or (code == self.origin):
            line = linecache.getline('iata.txt', random.randint(3,535))
            wordCount = 0
            code = ""
            airport = ""
            country = ""
            for l in line:
                if l != "|":
                    if wordCount == 0:
                        code += l
                    elif wordCount == 1:
                        airport += l
                    elif wordCount == 2:
                        country += l
                else:
                    wordCount += 1


        code = code.strip()
        aiport = airport.strip()
        country = country.strip()

        return code 

# use the normal dist for this 
    def genFuel(self):
        fuel = random.uniform(20,60)
        return fuel

# NTOE: is_departure will determine whether or not the taget or actual time is about the departure or arrival
# again, use the normal distribution
    def genTargetTime(self):
        # find way to get target (generate or input ??)
        pass 

    def genActualTime(self):
        pass

    # ------- PLANE CONTROL FUNCTIONS ------- #
    def decreaseFuel(self) -> bool:
        pass

    def goToRunway(self, runway: int) -> bool:
        pass

    def cancel(self) -> bool:
        pass

    def hasEmergency(self) -> bool:
        pass
