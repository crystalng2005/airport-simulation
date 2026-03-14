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
    
    def __init__(self, is_departure: bool, queue_controller, cancellation_time: int, probabilities: list[float]):
        
        # User settings for emergency probabilities (must be set before genEmergencyOnSpawn())
        self.set_user_settings(probabilities)
        self.queue_controller = queue_controller
        self.cancellation_time = cancellation_time

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

        # Increments total number of planes
        Plane.plane_num += 1
        

    # Returns the plane data as a dictionary
    def return_data(self) -> dict:
        """
        Returns the plane data as a dictionary, in the following format:

        callsign: str,
        origin: str,
        destination: str,
        is_departure: bool,
        fuel_level: float,
        emergency_status: EmergencyStatus,
        target_time: datetime,
        actual_time: datetime,
        current_location: str
        """
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

    def genCallsign(self) -> str:
        """
        Generates the call sign of the plane (PLN followed by the total number of planes in the simulation).
        """
        return "PLN" + str(self.plane_num)


    @classmethod
    def reset_plane_num(cls):
        """
        Class method, resets the number of planes in the simulation between runs, call on simulation start.
        """
        cls.plane_num = 0

    
    def genOrigin(self) -> str:
        """
        Generates the IATA code for the destination from the list of IATA airport codes
        
        The IATA codes are located in the IATA.txt file, which contains most of the codes,
        airports, and locations for airports around the world that can be used for 
        generating planes. Does this by choosing a random number corresponding to the
        the line of the file, then extracting information based the position of the separating
        '|' characters.
        """
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
    def genDestination(self) -> str:
        """
        Generates the destination codes for the airplanes using the same IATA.txt
        file that is used for genOrigin() and in the same way, but keeps looping
        until a code is found that isn't the same as the origin.

        """
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


    def genFuel(self) -> float:
        """
        Generates fuel based on the uniform distribution between 20 and 60 minutes

        Generated via random.uniform and then rounded to 2d.p to make visualisation
        easier for the results.
        """
        fuel = round(random.uniform(20,60))
        return fuel



    def genTargetTime(self) -> datetime:
        """
        Generates the target arrival/departure time for the aircraft

        Takes a random time between 0 and 23 hours (converted into seconds) and then
        extracts the components of the time. Depending on whether the is_departure flag
        is set, this time could be the arrival or departure time.
        Also generates and stores the target time in ticks to make statistics calculations easier, 
        but returns the datetime format.
        """
        # Generates the seconds randomly, then divides into hours/minutes etc.
        randSeconds = random.randint(0,82800)
        randHours = randSeconds // 3600
        remaining = randSeconds % 3600
        randMinutes = remaining // 60
        secs = remaining % 60

        # Gets the target time in ticks
        self.tickTargetTime = round(math.ceil(randMinutes/5))

        # Returns in datetime format, converted to int
        return datetime.time(int(randHours), int(randMinutes), int(secs))


    def genActualTime(self) -> datetime:
        """
        Uses the target time to generate the actual time using the normal distribution

        Uses the target time generated before to get the actual time. Does this by first breaking 
        the time down into seconds again and applying the normal distribution with a standard 
        deviation of 5 minutes. Then breaks the seconds down into time components and again
        stores the tick time and returns the datetime version.
        """
        # Breaks down the target time back into seconds
        actualSeconds = self.target_time.hour * 3600 + self.target_time.minute * 60 + self.target_time.second 

        # Applies normal distribution (with standard deviation of 5 minutes (300s))
        time = random.normal(actualSeconds, 5*60) 
        # Applies the normal distribution on the tick time
        self.tickActualTime = round(random.normal(self.tickTargetTime, 5/MINUTES_PER_TICK))

        # Converts the new time back into datetime and returns
        timeSeconds = int(time)
        timeSeconds = max(0, min(timeSeconds, 86399))
        timeHours = timeSeconds // 3600
        remaining = timeSeconds % 3600
        timeMinutes = remaining // 60
        secs = remaining % 60
        return datetime.time(int(timeHours),int(timeMinutes), int(secs))
    

    def set_user_settings(self, probabilities: list[float]):
        """
        Lets user set emergencies and defines that user settings have been set

        Probabilities are input as a list, and this is where they are extracted to
        be stored in the call (called on object creation by __init__)
        """
        self.user_setting = True
        self.user_mechanical = probabilities[0]
        self.user_health = probabilities[1]
        self.user_fuel = probabilities[2]


    def genEmergencyOnSpawn(self) -> EmergencyStatus:
        """
        Called to generate the emergencies based on the probability of something occuring over the whole journey

        The following takes the probabilities that the user input and assigns the aircraft an emergency if the
        value generated is 1.

        The following are the sources and calculations used for the default values given in the input boxes:
        Calculations and sources for emergency generation default values:

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

        mechanical_val = random.randint(0,int(1/self.user_mechanical)) if self.user_mechanical != 0 else 2
        fuel_val = random.randint(0,int(1/self.user_fuel)) if self.user_fuel != 0 else 2
        medical_val = random.randint(0,int(1/self.user_health)) if self.user_health != 0 else 2


        # Goes through and checks if any emergencies have been generated
        if mechanical_val == 1 or self.user_mechanical == 1:
            return EmergencyStatus.MECHANICAL
        elif fuel_val == 1 or self.fuel_level == 1:
            return EmergencyStatus.FUEL
        elif medical_val == 1 or self.user_health == 1:
            return EmergencyStatus.HEALTH
        else:
            return EmergencyStatus.NONE
        
    



    # ------- PLANE CONTROL FUNCTIONS ------- #


    # Decreases the fuel by the amount stored in FUEL_USAGE_PER_TICK constant with each call
    def decrease_fuel(self) -> bool:
        """
        Decreases fuel by the FUEL_USAGE_PER_TICK constant if the plane is in the holding queue only - 
        if a plane is in the depature queue, waiting to take off, then this instead applies to the
        cancellation time rather than fuel consumption. If there is an emergency, then this instead decreases the
        emergency time left before the plane is diverted.
        """
        if self.needsToBeRemoved:
            self.needsToBeRemoved = False
            self.exit_simulation()
        # Checks if the plane is cancelled (don't need to decrease if it is)
        if not self.left_simulation:
            if not self.is_departure: self.fuel_level -= FUEL_USAGE_PER_TICK
            if self.emergency_status != EmergencyStatus.NONE: self.emergency_time_left -= FUEL_USAGE_PER_TICK
            if self.is_departure: self.cancellation_time -= FUEL_USAGE_PER_TICK 
            RD.reportData.tot_fuel_used += FUEL_USAGE_PER_TICK
            return True 
        return False



    # Directs a plane to the given runway
    def goToRunway(self, runway: int) -> bool:
        """
        Assigns the plane runway value based on the available runways, only if the plane 
        is still in the simulation and not on a runway already.
        """
        if not self.left_simulation:
            if self.current_runway != runway:
                self.current_runway = runway 
                # Its now on a runway and will need to depart
                self.needsToBeRemoved = True
                return True 
            else:
                return False


    
    def cancel(self):
        """
        Cancels the plane and makes it leave the simulation
        """
        self.cancelled = True
        self.exit_simulation()


    
    def divert(self):
        """
        Diverts the plane and makes it leave the simulation
        """
        self.diverted = True
        self.exit_simulation()


    
    def exit_simulation(self):
        """
        Called when a plane is supposed to leave the simulation.
        Changes left simulation variable and appends plane kill to the action list
        """
        self.left_simulation = True
        currentFrameActions.current_frame_actions.append([self.callsign, "kill"])


    def has_emergency(self) -> EmergencyStatus:
        """
        Returns the current emergency status
        """
        return self.emergency_status


    # Called every tick to give every plane a chance of generating an emergency
    def update_emergency(self) -> EmergencyStatus:
        """
        Can be called to update the emegencies every tick.
        Note that fuel emergencies are excluded, as these are based on current fuel level, not random generation.

        The values below are based on the sources and calculations for genEmergencyOnSpawn, just adjusted to instead
        have the probabilities relative the the tick time.
        Below are the values for the emergency chances for every 60 minutes:

        28.4 million flight hours a year =  28400000
        Mechanical: per 100,000 flight hours is 0.85 --> 0.0000085 per 60 minutes
        https://atag.org/facts-figures : 35.3 million flights per year
        Medical: 88000000 flight hours per year, 2.49 hours per flight, 0.00004819 per 60 mins
        Fuel : 0.000003458 per flight --> 0.000001388 per 60 mins
        """
        # Gets the probability per tick
        mechanical_per_tick = self.user_mechanical/MINUTES_PER_TICK
        medical_per_tick = self.user_health/MINUTES_PER_TICK

        # Ordered in terms of priorities
        mechanical_val = random.randint(0,int(1/mechanical_per_tick)) if self.user_mechanical != 0 else 2 
        medical_val = random.randint(0,int(1/medical_per_tick)) if self.user_health != 0 else 2

        # Sets the emergency status based on generated values
        if self.emergency_status == EmergencyStatus.NONE:
            if mechanical_val == 1 or self.user_mechanical == 1:
                self.emergency_status= EmergencyStatus.MECHANICAL
                self.queue_controller.planeEmergency(self)
            elif medical_val == 1 or self.user_health == 1:
                self.emergency_status= EmergencyStatus.HEALTH
                self.queue_controller.planeEmergency(self)
            # Checks the fuel level and flags emergency if needed
            else:
                if self.fuel_level < 20:
                    self.emergency_status = EmergencyStatus.FUEL
                    self.queue_controller.planeEmergency(self)
            
        return self.emergency_status


    


