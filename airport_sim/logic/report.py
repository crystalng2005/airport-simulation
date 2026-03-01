from __future__ import annotations
import statistics
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path


# PerformanceReport Class

class PerformanceReport:
    def __init__(self, runway_amount, landings_per_hour, start_time):
        # Simulation preset data
        self.runway_amount = runway_amount
        self.landings_per_hour = landings_per_hour
        self.start_time = start_time

        self.diversions = 0
        self.cancellations = 0
        self.total_planes = 0
        self.tot_wait_time = 0
        self.tot_fuel_used = 0

        # Each counted in seconds (most accurate) (although for better plotting could round to minutes)
        self.wait_times = []
        self.hold_times = []
        self.take_off_delays = []
        self.arrival_delay_times = []

        self.queue_max = 0
        self.queue_current = 0

        self.holding_max = 0
        self.holding_current = 0


# NOTE: based on the specification take-off time /= departure time, as this is when the aircraft is ready instead. 



#NOTE: arrival time maximum and average is a bit weird because surely this is already given in the assumptions
    # Since its normally distributed around the target arrival/departure time (??)



    def output(self) -> str:
        self.max_wait = max(self.wait_times)
        self.max_hold = max(self.hold_times)
        self.max_take_off = max(self.take_off_delays)
        self.max_arrival = max(self.arrival_delay_times)

        self.mean_wait = statistics.mean(self.wait_times)
        self.mean_hold = statistics.mean(self.hold_times)
        self.mean_take_off = statistics.mean(self.take_off_delays)
        self.mean_arrival = statistics.mean(self.arrival_delay_times)

        self.std_wait = statistics.stdev(self.wait_times)
        self.std_hold = statistics.stdev(self.hold_times)
        self.std_take_off = statistics.stdev(self.take_off_delays)
        self.std_arrival = statistics.stdev(self.arrival_delay_times)

        self.fuel_avg = 0
        if self.total_planes > 0:
            self.fuel_avg = self.tot_fuel_used / self.total_planes

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






