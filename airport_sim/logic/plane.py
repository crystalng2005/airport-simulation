import datetime
from enum import Enum 
from numpy import random
import linecache
import os
import math
# from globals import reportData as RD
import logic.globals.reportData as RD


# CONSTANTS
FUEL_USAGE_PER_TICK = 5

MINUTES_PER_TICK = 5



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



#TODO: get information function () format:dictionary

class Plane:
    plane_num = 0
    
    def __init__(self, is_departure: bool):
        self.callsign = self.genCallsign()
        self.origin = self.genOrigin()
        self.destination = self.genDestination()
        self.is_departure = is_departure
        self.fuel_level = self.genFuel()
        self.emergency_status = self.genEmergencyOnSpawn()
        self.target_time = self.genTargetTime()
        self.actual_time = self.genActualTime()
        self.current_location = self.origin
        self.emergency_time_left = 0 # Initially 0, will be decreased in decrease fuel when emergency arises
        self.current_runway = -1
        self.cancelled = False
        self.entered_hold = None 
        self.left_hold = None
        Plane.plane_num += 1

    # ------- CONSTRUCTOR ------ #
    # dont need, can use the built in constructor
    """def __new__(self):
        pass"""
    
    # Returns the plane data as a dictionary
    def return_data(self):
        data = {
            "callsign": self.callsign,
            "origin": self.origin,
            "destination": self.destination,
            "is_departure": self.is_departure,
            "fuel_level": self.fuel_level,
            "emergency_status": self.emergency_status.name,
            "target_time": str(self.target_time),
            "actual_time": str(self.actual_time),
            "current_location": self.current_location
        }
        return data

        return data

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
        iata_path = os.path.join(os.path.dirname(__file__), '..', 'iata.txt') # Absolute path
        code = ""
        airport = ""
        country = ""
        while first or (code == self.origin):
            line = linecache.getline(iata_path, random.randint(3,535))
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

            first = False 

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
        randSeconds = random.randint(0,82800)
        randMinutes = (randSeconds/60) % 60
        self.tickTargetTime = math.ceil(randMinutes/5)
        randHours = (randMinutes/60) % 60
        return datetime.time(int(randHours), int(randMinutes), int(randSeconds))

    def genActualTime(self):
        actualSeconds = self.target_time.time().hour + (self.target_time.time().minute) *60 + self.target_time.time().second 
        time = random.normal(actualSeconds, 5*60) 
        self.tickActualTime = random.normal(self.tickTargetTime, 1)
        timeSeconds = time
        timeMinutes = (timeSeconds/60) % 60
        timeHours = (timeMinutes/60) % 60
        return datetime.time(int(timeHours),int(timeMinutes), int(timeSeconds))
    
    
  
    def genEmergencyOnSpawn(self):
        # offer chance to set with user input once json data available, placeholders for now
        # Medical emergencies: https://pmc.ncbi.nlm.nih.gov/articles/PMC7125952/ 
            # Diversion rate: 0.073, 1 emergency per 604 flights, rate per flight: 0.00012
        # Fuel emergencies: (not a lot of data, but can use american):
            # https://www.ishn.com/articles/107086-planes-run-out-of-fuel-more-often-than-you-think
            # https://www.faa.gov/air_traffic/by_the_numbers
            # 56 fuel accidents per year, 16191379 flights = 3.458*10^-6 = 0.000003458, but actual value may be higher
            # This will just be for spawning in with the emergency
        # Mechanical: https://www.aopa.org/training-and-safety/air-safety-institute/accident-analysis/richard-g-mcspadden-report/mcspadden-report-figure-view/?category=all&year=2023&condition=all&report=true
            # 0.00004

        # Chances per flight (based on flight per year data)
        medical_p = 0.00012
        fuel_p = 0.000003458
        mechanical_p = 0.00004
        
        # NOTE: System allows for only 1 emergency, so pick the highest priority one generated
        
        # Ordered in terms of priorities
        mechanical_val = random.randint(1,int(1/mechanical_p))
        fuel_val = random.randint(1,int(1/fuel_p))
        medical_val = random.randint(1,int(1/medical_p))

        if mechanical_val == 1:
            return EmergencyStatus.MECHANICAL
        elif fuel_val == 1:
            return EmergencyStatus.FUEL
        elif medical_val == 1:
            return EmergencyStatus.HEALTH
        else:
            return EmergencyStatus.NONE


## need to add to the plane class the emgency deciding

    # ------- PLANE CONTROL FUNCTIONS ------- #

    #NOTE: called each tick, so decreases by 5 minutes each call
    def decreaseFuel(self):
        if not self.cancelled:
            self.fuel_level -= FUEL_USAGE_PER_TICK
            RD.reportData += FUEL_USAGE_PER_TICK
            return True 
        return False


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

    # Call every tick, for every plane to both present chance of generating emergency and checking if a plane has one
    # Update this based on tick rate
    def hasEmergency(self):
        # 28.4 million flight hours a year =  28400000
        # Mechanical: per 100,000 flight hours is 0.85 --> 0.0000085 per 60 minutes
        # https://atag.org/facts-figures : 35.3 million flights per year
        # Medical: 88000000 flight hours per year, 2.49 hours per flight, 0.00004819 per 60 mins
        # Fuel : 0.000003458 per flight --> 0.000001388 per 60 mins

        mechanical_per_tick = 0.0000085/MINUTES_PER_TICK
        medical_per_tick = 0.00004819/MINUTES_PER_TICK
        #fuel_per_tick = 0.000001388/MINUTES_PER_TICK

        # Ordered in terms of priorities
        mechanical_val = random.randint(1,int(1/mechanical_per_tick))
        #fuel_val = random.randint(1,int(1/fuel_per_tick))
        medical_val = random.randint(1,int(1/medical_per_tick))
        if self.emergency_status == EmergencyStatus.NONE:
            if mechanical_val == 1:
                self.emergency_status= EmergencyStatus.MECHANICAL
            elif medical_val == 1:
                self.emergency_status= EmergencyStatus.HEALTH
            else:
                if self.fuel_level < 20:
                    self.emergency_status = EmergencyStatus.FUEL
            
        return self.emergency_status


