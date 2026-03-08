from __future__ import annotations
import statistics
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import datetime


# PerformanceReport Class

class PerformanceReport:
    def __init__(self, runway_total, runways_mixed, runways_departure, runways_landing, landings_per_hour, start_time):
        # Simulation preset data
        self.runway_total = runway_total
        self.runways_mixed = runways_mixed
        self.runways_departure = runways_departure
        self.runways_landing = runways_landing
        self.landings_per_hour = landings_per_hour
        self.start_time = start_time

        # Data from running the simulation
        self.diversions = 0
        self.cancellations = 0
        self.total_planes = 0
        self.tot_wait_time = 0
        self.tot_fuel_used = 0

        # Time monitored per plane, each counted in seconds
        self.wait_times = []
        self.hold_times = []
        self.take_off_delays = []
        self.arrival_delay_times = []

        # Queue size data
        self.queue_max = 0
        self.queue_current = 0

        self.holding_max = 0
        self.holding_current = 0




    # Records the time the simulation has finished
    # Call when ending the simulation
    def setFinishTime(self, finishTime : datetime):
        self.finish_time = finishTime
        self.duration = self.finish_time - self.start_time
        

    # Generates the report based on collected data
    def generateReport(self):
        self.efficiency = self.getEfficiency()
        
        # Maximum of each value stored in the lists
        self.max_wait = max(self.wait_times) if self.wait_times else 0
        self.max_hold = max(self.hold_times) if self.hold_times else 0
        self.max_take_off = max(self.take_off_delays) if self.take_off_delays else 0
        self.max_arrival = max(self.arrival_delay_times) if self.arrival_delay_times else 0

        # Mean of the values stored in the lists
        self.mean_wait = statistics.mean(self.wait_times) if self.wait_times else 0
        self.mean_hold = statistics.mean(self.hold_times) if self.hold_times else 0
        self.mean_take_off = statistics.mean(self.take_off_delays) if self.take_off_delays else 0
        self.mean_arrival = statistics.mean(self.arrival_delay_times) if self.arrival_delay_times else 0

        # Standard deviation of the values stored in the lists
        self.std_wait = statistics.stdev(self.wait_times) if len(self.wait_times) >= 2 else 0
        self.std_hold = statistics.stdev(self.hold_times) if len(self.hold_times) >= 2 else 0
        self.std_take_off = statistics.stdev(self.take_off_delays) if len(self.take_off_delays) >= 2 else 0
        self.std_arrival = statistics.stdev(self.arrival_delay_times) if len(self.arrival_delay_times) >= 2 else 0

        # Calculated the average fuel used per plane, checks if total planes are 0
        self.fuel_avg = 0
        if self.total_planes > 0:
            self.fuel_avg = self.tot_fuel_used / self.total_planes



    def string_duration(self):
        inSeconds = int(self.duration.total_seconds())
        hours, remainder = divmod(inSeconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours} hours, {minutes} minutes, {seconds} seconds"
    

    
    def outputReport_dict(self):
        return {
            "start_time" : self.start_time,
            "completed_at" : self.finish_time,
            "duration" : self.string_duration(),

            "total_planes": self.total_planes,
            "diversions": self.diversions,
            "cancellations": self.cancellations,

            "tot_fuel_used": self.tot_fuel_used,
            "avg_fuel_per_plane" : self.fuel_avg,

            "holding_max": self.holding_max,
            "queue_max": self.queue_max,
            
            "tot_wait_time": self.tot_wait_time,
            "avg_wait_time": self.mean_wait, 
            "std_wait_time" : self.std_wait,

            "max_hold_time" : self.max_hold,
            "avg_hold_time" : self.mean_hold,
            "std_hold_time" : self.std_hold,

            "max_takeoff_time" : self.max_take_off,
            "avg_takeoff_time" : self.mean_take_off,
            "std_take_off_time" : self.std_take_off,

            "max_arrival_time" : self.max_arrival,
            "avg_arrival_time" : self.mean_arrival,
            "std_arrival_time" : self.std_arrival,

            "efficiency": self.efficiency           
        }



    def outputReport_string(self) -> str:
        self.generateReport()

        return (f"Number of diversions: {self.diversions}\n"
                f"Number of cancellations: {self.cancellations}\n"
                f"Total amount of fuel used: {self.tot_fuel_used}\n"
                f"Average amount of fuel used: {self.fuel_avg}\n"
                f"Total number of planes generated: {self.total_planes}\n\n"

                f"Maximum number of planes in holding queue: {self.holding_max}\n"
                f"Maximum number of planes in runway queue: {self.queue_max}\n\n"

                f"Maximum wait time: {self.max_wait}\n"
                f"Average wait time: {self.mean_wait}\n"
                f"Standard deviation of wait times: {self.std_wait}\n\n"

                f"Maximum hold time: {self.max_hold}\n"
                f"Average hold time: {self.mean_hold}\n"
                f"Standard deviation of hold times: {self.std_hold}\n\n"

                f"Maximum take-off time: {self.max_take_off}\n"
                f"Average take-off time: {self.mean_take_off}\n"
                f"Standard deviation of take-off times: {self.std_take_off}\n\n"

                f"Maximum arrival time: {self.max_arrival}\n"
                f"Average arrival time: {self.mean_arrival}\n"
                f"Standard deviation of arrival times: {self.std_arrival}\n\n")



    def reset(self) -> bool:
        self.diversions = 0
        self.cancellations = 0
        self.total_planes = 0
        self.tot_wait_time = 0
        self.tot_fuel_used = 0

        self.hold_times = []
        self.wait_times = []
        self.take_off_delays = []
        self.arrival_delay_times = []
        
        self.queue_max = 0
        self.queue_current = 0

        self.holding_max = 0
        self.holding_current = 0



    def getEfficiency(self):
        if self.total_planes > 0:
            return ((self.total_planes - self.diversions - self.cancellations)/self.total_planes * 100)
        return 0



    def incQueueCurrent(self):
        self.queue_current +=1 
        if self.queue_current > self.queue_max:
            self.queue_max = self.queue_current 

    def decQueueCurrent(self):
        if self.queue_current > 0:
            self.queue_current -= 1

    def incHoldingCurrent(self):
        self.holding_current += 1
        if self.holding_current > self.holding_max:
            self.holding_max = self.holding_current

    def decHoldingCurrent(self):
        if self.holding_current > 0:
            self.holding_current -= 1






