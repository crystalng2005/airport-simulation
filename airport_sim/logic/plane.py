import datetime
from enum import Enum 
from numpy import random
import linecache
import os




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
    
    def __init__(self, is_departure: bool):
        self.callsign = self.genCallsign()
        self.origin = self.genOrigin()
        self.destination = self.genDestination()
        self.is_departure = is_departure
        self.fuel_level = self.genFuel()
        self.emergency_status = EmergencyStatus.NONE
        self.target_time = self.genTargetTime()
        self.actual_time = self.genActualTime()
        self.current_location = self.origin
        self.emergency_time_left = 0 # Initially 0, will be decreased in decrease fuel when emergency arises
        self.current_runway = -1
        self.cancelled = False
        Plane.plane_num += 1

    # ------- CONSTRUCTOR ------ #
    # dont need, can use the built in constructor
    """def __new__(self):
        pass"""

    # ------- PLANE GENERATION FUNCTIONS ------- #
    def genCallsign(self):
        # For this, number the planes, can just keep a global count of current value
        # If want to, could preface with company name or something
        return "PLN" + str(self.plane_num)

# for the following two will create a txt file of airport AITA codes, names and countries
    def genOrigin(self):
        # line = linecache.getline('iata.txt', random.randint(3,535))
        iata_path = os.path.join(os.path.dirname(__file__), '..', 'iata.txt') # Absolute path
        line = linecache.getline(iata_path, random.randint(3, 535))
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

            first = False # Ended the infinite loop

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
        #doing it in seconds, but can change it to be in minutes as well
        #86400
        randSeconds = random.randint(0,86400)
        randMinutes = 86400/60
        randHours = randMinutes/60
        return datetime.time(randHours, randMinutes, randSeconds)

    def genActualTime(self):
        actualSeconds = self.target_time.time().hour + (self.target_time.time().minute) *60 + self.target_time.time().second 
        time = random.normal(actualSeconds, 5*60) 
        timeSeconds = random.randint(0,86400)
        timeMinutes = 86400/60
        timeHours = timeMinutes/60
        return datetime.time(timeHours,timeMinutes, timeSeconds)



    # ------- PLANE CONTROL FUNCTIONS ------- #

    #NOTE: called each tick, so decreases by 5 minutes each call
    def decreaseFuel(self):
        self.fuel_level -= 5

    #TODO: change name to check runway to make clearer?
    def goToRunway(self, runway: int) -> bool:
        if self.current_runway != runway:
            self.current_runway = runway 
            return True 
        else:
            return False
         

# TODO: modify if additional cancellation logic required (e.g. checking validity of cancel request?)
    def cancel(self):
        self.cancelled = True

    def hasEmergency(self):
        return self.emergency_status
