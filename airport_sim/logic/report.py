
import statistics
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path


# PerformanceReport Class


#TODO: depending on what changes, could generate full plot reports e.g. showing changes based on runway num/plane amt


#NOTE: changing previous object to now just create a blank one that can be used to record data.
class PerformanceReport:
    def __init__(self):
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


#TODO: need the average wait time per plane in the take-off queue, how is this defined???


#NOTE: arrival time maximum and average is a bit weird because surely this is already given in the assumptions
    # Since its normally distributed around the target arrival/departure time (??)


    def output(self) -> str:
        max_wait = max(self.wait_times)
        max_hold = max(self.hold_times)
        max_take_off = max(self.take_off_delays)
        max_arrival = max(self.arrival_delay_times)

        mean_wait = statistics.mean(self.wait_times)
        mean_hold = statistics.mean(self.hold_times)
        mean_take_off = statistics.mean(self.take_off_delays)
        mean_arrival = statistics.mean(self.arrival_delay_times)

        std_wait = statistics.stdev(self.wait_times)
        std_hold = statistics.stdev(self.hold_times)
        std_take_off = statistics.stdev(self.take_off_delays)
        std_arrival = statistics.stdev(self.arrival_delay_times)

        fuel_avg = 0
        if self.total_planes > 0:
            fuel_avg = self.tot_fuel_used / self.total_planes

        return (f"Number of diversions: {self.diversions}\n"
                f"Number of cancellations: {self.cancellations}\n"
                f"Total amount of fuel used: {self.tot_fuel_used}\n"
                f"Average amount of fuel used: {fuel_avg}\n"
                f"Total number of planes generated: {self.total_planes}\n\n"

                f"Maximum number of planes in holding queue: {self.holding_max}\n"
                f"Maximum number of planes in runway queue: {self.queue_current}\n\n"

                f"Maximum wait time: {max_wait}\n"
                f"Average wait time: {mean_wait}\n"
                f"Standard deviation of wait times: {std_wait}\n\n"

                f"Maximum hold time: {max_hold}\n"
                f"Average hold time: {mean_hold}\n"
                f"Standard deviation of hold times: {std_hold}\n\n"

                f"Maximum take-off time: {max_take_off}\n"
                f"Average take-off time: {mean_take_off}\n"
                f"Standard deviation of take-off times: {std_take_off}\n\n"

                f"Maximum arrival time: {max_arrival}\n"
                f"Average arrival time: {mean_arrival}\n"
                f"Standard deviation of arrival times: {std_arrival}\n\n")

        # basically just do what i can now with what i have


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


    def plot_hold_times(self):
        #for now sorting like this, if there are issues, can make a copy of hte list instead (but as final call should be fine)
        
        # Sorting the values, gettings the unique times and their occurences for the plot
        self.hold_times.sort()
        uniqueTimesQuantity = []
        prevSameIndex = 0
        for i in range(0, len(self.hold_times)):
            if i == 0:
                uniqueTimesQuantity[i][0] = self.hold_times[i]
                uniqueTimesQuantity[i][1] += 1
            elif self.hold_times[i] == uniqueTimesQuantity[prevSameIndex][0]:
                uniqueTimesQuantity[prevSameIndex][1] += 1
            else:
                uniqueTimesQuantity[i][0] = self.hold_times[i]
                uniqueTimesQuantity[i][1] += 1
                prevSameIndex = i

        uniqueTimes = [entry[0] for entry in uniqueTimesQuantity]
        timeQuantity = [entry[1] for entry in uniqueTimesQuantity]

        # Plotting the points
        #NOTE:can swap the x,y values or change time to minutes instead depending on how the plot looks to make it nicer
        location = Path("./")
        filename = location / "hold_times.pdf"

        x = np.array(uniqueTimes)
        y = np.array(timeQuantity)

        plt.xlabel("Plane hold times")
        plt.ylabel("Occurrences")

        plt.scatter(x,y)
        plt.savefig(filename)
         

    def plot_wait_times(self):
        # Sorting the values, gettings the unique times and their occurences for the plot
        self.wait_times.sort()
        uniqueTimesQuantity = []
        prevSameIndex = 0
        for i in range(0, len(self.wait_times)):
            if i == 0:
                uniqueTimesQuantity[i][0] = self.wait_times[i]
                uniqueTimesQuantity[i][1] += 1
            elif self.wait_times[i] == uniqueTimesQuantity[prevSameIndex][0]:
                uniqueTimesQuantity[prevSameIndex][1] += 1
            else:
                uniqueTimesQuantity[i][0] = self.wait_times[i]
                uniqueTimesQuantity[i][1] += 1
                prevSameIndex = i

        uniqueTimes = [entry[0] for entry in uniqueTimesQuantity]
        timeQuantity = [entry[1] for entry in uniqueTimesQuantity]

        # Plotting the points
        #NOTE:can swap the x,y values or change time to minutes instead depending on how the plot looks to make it nicer
        location = Path("./")
        filename = location / "wait_times.pdf"

        x = np.array(uniqueTimes)
        y = np.array(timeQuantity)

        plt.xlabel("Plane wait times")
        plt.ylabel("Occurrences")

        plt.scatter(x,y)
        plt.savefig(filename) 


    def plot_take_off_delays(self):
        # Sorting the values, gettings the unique times and their occurences for the plot
        self.take_off_delays.sort()
        uniqueTimesQuantity = []
        prevSameIndex = 0
        for i in range(0, len(self.take_off_delays)):
            if i == 0:
                uniqueTimesQuantity[i][0] = self.take_off_delays[i]
                uniqueTimesQuantity[i][1] += 1
            elif self.take_off_delays[i] == uniqueTimesQuantity[prevSameIndex][0]:
                uniqueTimesQuantity[prevSameIndex][1] += 1
            else:
                uniqueTimesQuantity[i][0] = self.take_off_delays[i]
                uniqueTimesQuantity[i][1] += 1
                prevSameIndex = i

        uniqueTimes = [entry[0] for entry in uniqueTimesQuantity]
        timeQuantity = [entry[1] for entry in uniqueTimesQuantity]

        # Plotting the points
        #NOTE:can swap the x,y values or change time to minutes instead depending on how the plot looks to make it nicer
        location = Path("./")
        filename = location / "take_off_delays.pdf"

        x = np.array(uniqueTimes)
        y = np.array(timeQuantity)

        plt.xlabel("Plane take-off delays")
        plt.ylabel("Occurrences")

        plt.scatter(x,y)
        plt.savefig(filename) 

    def plot_arrival_delay_times(self):
        # Sorting the values, gettings the unique times and their occurences for the plot
        self.arrival_delay_times.sort()
        uniqueTimesQuantity = []
        prevSameIndex = 0
        for i in range(0, len(self.arrival_delay_times)):
            if i == 0:
                uniqueTimesQuantity[i][0] = self.arrival_delay_times[i]
                uniqueTimesQuantity[i][1] += 1
            elif self.arrival_delay_times[i] == uniqueTimesQuantity[prevSameIndex][0]:
                uniqueTimesQuantity[prevSameIndex][1] += 1
            else:
                uniqueTimesQuantity[i][0] = self.arrival_delay_times[i]
                uniqueTimesQuantity[i][1] += 1
                prevSameIndex = i

        uniqueTimes = [entry[0] for entry in uniqueTimesQuantity]
        timeQuantity = [entry[1] for entry in uniqueTimesQuantity]

        # Plotting the points
        #NOTE:can swap the x,y values or change time to minutes instead depending on how the plot looks to make it nicer
        location = Path("./")
        filename = location / "arrival_delay_times.pdf"

        x = np.array(uniqueTimes)
        y = np.array(timeQuantity)

        plt.xlabel("Plane arrival delay times")
        plt.ylabel("Occurrences")

        plt.scatter(x,y)
        plt.savefig(filename)


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


    



