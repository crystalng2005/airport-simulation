import datetime
from enum import Enum 
from numpy import random
import linecache
import os
import math

import logic.globals.reportData as RD
from logic.currentFrameActions import currentFrameActions


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




class Plane:
    # Stores the total number of plane objects generated
    plane_num = 0
    
    def __init__(self, is_departure: bool):
        # Basic information relating to the plane
        self.callsign = self.genCallsign()
        self.origin = self.genOrigin()
        self.destination = self.genDestination()
        self.current_location = self.origin
        self.is_departure = is_departure
        self.fuel_level = self.genFuel()
        self.emergency_status = self.genEmergencyOnSpawn()
        self.target_time = self.genTargetTime()
        self.actual_time = self.genActualTime()

        # User settings for emergency probabilities (must be set before genEmergencyOnSpawn())
        self.user_setting = False
        self.user_mechanical = 0
        self.user_medical = 0
        self.user_fuel = 0

        # Management variables
        self.emergency_time_left = 0 # Initially 0, will be decreased in decrease fuel when emergency arises
        self.current_runway = -1

        # Control booleans
        self.cancelled = False
        self.diverted = False
        self.entered_hold = None 
        self.left_hold = None
        self.generated_at = None
        self.left_simulation = False
        self.needsToBeRemoved = False

        # Increments total number of planes
        Plane.plane_num += 1
        

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


    # ------- PLANE GENERATION FUNCTIONS ------- #

    # Generates the call sign (PLN followed by its plane number)
    def genCallsign(self):
        return "PLN" + str(self.plane_num)

    # Generates the IATA code for the destination from the list of IATA airport codes
    def genOrigin(self):
        # Gets the absolute path of iata.txt
        iata_path = os.path.join(os.path.dirname(__file__), '..', 'iata.txt')
        # Gets a random line from the file
        line = linecache.getline(iata_path, random.randint(3, 535))
        wordCount = 0
        # Gets the code, airport and country from the entry
        code = ""
        airport = ""
        country = ""
        # Checks which part of the entry is currently being read based on '|' location
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
        
        # Remove whitespace
        code = code.strip()
        aiport = airport.strip()
        country = country.strip()

        # Returns the IATA code, but can change to airport/country
        return code


    # Generates the destination airport IATA code
    def genDestination(self):
        first = True
        # Gets the absolute path of iata.txt
        iata_path = os.path.join(os.path.dirname(__file__), '..', 'iata.txt')
        code = ""
        airport = ""
        country = ""
        # Lets it run once (first), then loops until the code generated is different from the origin code
        while first or (code == self.origin):
            line = linecache.getline(iata_path, random.randint(3,535))
            wordCount = 0
            code = ""
            airport = ""
            country = ""
            # Checks which part of the entry is currently being read based on '|' location
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

        # Removes whitespace
        code = code.strip()
        aiport = airport.strip()
        country = country.strip()

        # Returns the IATA code
        return code 


    # Generates fuel based on the uniform distribution between 20 and 60 minutes
    def genFuel(self):
        fuel = random.uniform(20,60)
        return fuel



    # Generates the target arrival/departure time for the aircraft
    # Depending on whether is_departure is true this could bethe target departure/arrival time
    def genTargetTime(self):
        # Generates the seconds randomly, then divides into hours/minutes etc.
        randSeconds = random.randint(0,82800)
        randHours = randSeconds // 3600
        remaining = randSeconds % 3600
        randMinutes = remaining // 60
        secs = remaining % 60

        # Gets the target time in ticks
        self.tickTargetTime = math.ceil(randMinutes/5)

        # Returns in datetime format, converted to int
        return datetime.time(int(randHours), int(randMinutes), int(secs))

    # Uses the target time to generate the actual time using the normal distribution
    def genActualTime(self):
        # Breaks down the target time back into seconds
        actualSeconds = self.target_time.hour * 3600 + self.target_time.minute * 60 + self.target_time.second 

        # Applies normal distribution (with standard deviation of 5 minutes (300s))
        time = random.normal(actualSeconds, 5*60) 
        # Applies the normal distribution on the tick time
        self.tickActualTime = random.normal(self.tickTargetTime, 5/MINUTES_PER_TICK)

        # Converts the new time back into datetime and returns
        timeSeconds = int(time)
        timeSeconds = max(0, min(timeSeconds, 86399))
        timeHours = timeSeconds // 3600
        remaining = timeSeconds % 3600
        timeMinutes = remaining // 60
        secs = remaining % 60
        return datetime.time(int(timeHours),int(timeMinutes), int(secs))
    

    """

    Calculations and sources for emergency generation:

    Medical emergencies: https://pmc.ncbi.nlm.nih.gov/articles/PMC7125952/ 
        Diversion rate: 0.073, 1 emergency per 604 flights, rate per flight: 0.00012
    Fuel emergencies: (not a lot of data, but can use american):
        https://www.ishn.com/articles/107086-planes-run-out-of-fuel-more-often-than-you-think
        https://www.faa.gov/air_traffic/by_the_numbers
        56 fuel accidents per year, 16191379 flights = 3.458*10^-6 = 0.000003458, but actual value may be higher
        This will just be for spawning in with the emergency
    Mechanical: https://www.aopa.org/training-and-safety/air-safety-institute/accident-analysis/richard-g-mcspadden-report/mcspadden-report-figure-view/?category=all&year=2023&condition=all&report=true
        0.00004
    
    """

  
    def genEmergencyOnSpawn(self):
        # Placeholders
        mechanical_val = 2
        fuel_val = 2
        medical_val = 2
        # If user hasn't set anything
        if not self.user_setting:
            # Chances per flight (based on flight per year data)
            medical_p = 0.00012
            fuel_p = 0.000003458
            mechanical_p = 0.00004
            
            # Only one emergency is tracked, so the highest one is picked
            # Ordered in terms of priorities
            mechanical_val = random.randint(1,int(1/mechanical_p))
            fuel_val = random.randint(1,int(1/fuel_p))
            medical_val = random.randint(1,int(1/medical_p))

        # If the user has set values for probabilities
        else:
            mechanical_val = random.randint(1,int(1/self.user_mechanical))
            fuel_val = random.randint(1,int(1/self.user_fuel))
            medical_val = random.randint(1,int(1/self.user_medical))

        # Goes through and checks if any emergencies have been generated
        if mechanical_val == 1:
            return EmergencyStatus.MECHANICAL
        elif fuel_val == 1:
            return EmergencyStatus.FUEL
        elif medical_val == 1:
            return EmergencyStatus.HEALTH
        else:
            return EmergencyStatus.NONE
        
    # Lets user set emergencies and defines that user settings have been set
    def set_user_emergencies(self, mechanical, medical, fuel):
        self.user_setting = True
        self.user_mechanical = mechanical
        self.user_medical = medical
        self.user_fuel = fuel



    # ------- PLANE CONTROL FUNCTIONS ------- #


    # Decreases the fuel by the amount stored in FUEL_USAGE_PER_TICK constant with each cal
    def decrease_fuel(self):
        if self.needsToBeRemoved:
            self.needsToBeRemoved = False
            self.exit_simulation()
        # Checks if the plane is cancelled (don't need to decrease if it is)
        if not self.cancelled:
            self.fuel_level -= FUEL_USAGE_PER_TICK
            RD.reportData.tot_fuel_used += FUEL_USAGE_PER_TICK
            return True 
        return False


    # Directs a plane to the given runway
    def goToRunway(self, runway: int) -> bool:
        if self.current_runway != runway:
            self.current_runway = runway 
            # Its now on a runway and will need to depart
            self.needsToBeRemoved = True
            return True 
        else:
            return False


    # Cancels the plane and makes it leave the simulation
    def cancel(self):
        self.cancelled = True
        self.exit_simulation()


    # Diverts the plane and makes it leave the simulation
    def divert(self):
        self.diverted = True
        self.exit_simulation()


    # Changes left simulation variable and appends plane kill to the action list
    def exit_simulation(self):
        self.left_simulation = True
        currentFrameActions.current_frame_actions.append([self.callsign, "kill"])


    # Returns the current emergency status
    def has_emergency(self):
        return self.emergency_status


    """
    Below are the values for the emergency chances for every 60 minutes: (uses sources from above)

    28.4 million flight hours a year =  28400000
    Mechanical: per 100,000 flight hours is 0.85 --> 0.0000085 per 60 minutes
    https://atag.org/facts-figures : 35.3 million flights per year
    Medical: 88000000 flight hours per year, 2.49 hours per flight, 0.00004819 per 60 mins
    Fuel : 0.000003458 per flight --> 0.000001388 per 60 mins
    
    """



    # Called every tick to give every plane a chance of generating an emergency
    # Fuel emergencies are excluded, as these are based on current fuel level, not random generation
    def update_emergency(self):
        # If no user values have been given
        if not self.user_setting:
            # Gets the probability per tick
            mechanical_per_tick = 0.0000085/MINUTES_PER_TICK
            medical_per_tick = 0.00004819/MINUTES_PER_TICK

            # Ordered in terms of priorities
            mechanical_val = random.randint(1,int(1/mechanical_per_tick))
            medical_val = random.randint(1,int(1/medical_per_tick))
        
        # If user values given, use these
        else:
            mechanical_per_tick = self.user_mechanical/MINUTES_PER_TICK
            medical_per_tick = self.user_medical/MINUTES_PER_TICK

            mechanical_val = random.randint(1,int(1/mechanical_per_tick))
            medical_val = random.randint(1,int(1/medical_per_tick))

        # Sets the emergency status based on generated values
        if self.emergency_status == EmergencyStatus.NONE:
            if mechanical_val == 1:
                self.emergency_status= EmergencyStatus.MECHANICAL
            elif medical_val == 1:
                self.emergency_status= EmergencyStatus.HEALTH
            
            # Checks the fuel level and flags emergency if needed
            else:
                if self.fuel_level < 20:
                    self.emergency_status = EmergencyStatus.FUEL
            
        return self.emergency_status


    


