import statistics
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from report import PerformanceReport
from logic.presets import PresetController







## Plots for: 
    # x:Runways, y:diversions
    # x:Runways, y:cancellations
    # x:Plane number, y:diversions
    # x:plane number, y:cancellations

## QUESTIONS: 
    # do we want to plot cancellations too?
    # would it be good to somehow include the runway splits too?
    # should i make a summary text document for all the reports or not? would this be useful? graph easier to visualise

def summariseAll(reports: list[PerformanceReport]):
    runways = []
    landings_per_hour = []
    diversions = []
    cancellations = []
    diversions_per_runway = []
    avg_diversions_per_runway = []

    

    for report in reports:
        runways.append(report.runway_amount)
        landings_per_hour.append(report.landings_per_hour)
        diversions.append(report.diversions)
        cancellations.append(report.cancellations)
    
    
    for i in range(0, len(runways)):
        if i == 0:
            diversions_per_runway.append([runways[i],[diversions[i]]])
        else:
            for j in range(0, len(diversions_per_runway)):
                if diversions_per_runway[j][0] == runways[i]:
                    diversions_per_runway[j][1].append(diversions[i])
    
    diversions_per_runway.sort(key = lambda entry: entry[0])

    for i in range(0,len(diversions_per_runway)):
        avg_diversions_per_runway[i][0] = diversions_per_runway[i][0]
        avg_diversions_per_runway[i][1] = statistics.mean(diversions_per_runway[i][1])


    
    location = Path("./")
    filename = location / "runways_diversions.pdf"

    x = np.array(runways)
    y = np.array(avg_diversions_per_runway)

    plt.plot(x, y, marker='o')
    plt.title('Amount of runways and the average number of diversions')
    plt.xlabel('Amount of runways')
    plt.ylabel('Number of diversions')
    plt.show()
    plt.savefig(filename)

    


    
    
    
    """runways = []
    landings_per_hour = []
    diversions = []
    cancellations = []
    for report in reports:
        runways.append(report.runway_amount)
        landings_per_hour.append(report.landings_per_hour)
        diversions.append(report.diversions)
        cancellations.append(report.cancellations)

    location = Path("./")
    filename = location / "runways_diversions.pdf"

    x = np.array(runways)
    y = np.array(diversions)

    plt.xlabel("Plane actual arrival time (s)")
    plt.ylabel("Time spent in holding queue (s)")

    plt.scatter(x,y)
    plt.savefig(filename) """
    
    



"""
Format for function below:

"Percentage (%) changes in metrics in Report 2 relative to Report 1"
f"Number of diversions: {diversions}\n"
f"Number of cancellations: {cancellations}\n"
f"Total amount of fuel used: {tot_fuel_used}\n"
f"Average amount of fuel used: {fuel_avg}\n"
f"Total number of planes generated: {total_planes}\n\n"

f"Maximum number of planes in holding queue: {holding_max}\n"
f"Maximum number of planes in runway queue: {queue_max}\n\n"

f"Maximum wait time: {max_wait}\n"
f"Average wait time: {mean_wait}\n\n"

f"Maximum hold time: {max_hold}\n"
f"Average hold time: {mean_hold}\n\n"

f"Maximum take-off time: {max_take_off}\n"
f"Average take-off time: {mean_take_off}\n\n"

f"Maximum arrival time: {max_arrival}\n"
f"Average arrival time: {mean_arrival}\n\n"

"""

def dualCompareReports(rep1 : PerformanceReport, rep2 : PerformanceReport):
    ans = "Percentage (%) changes in metrics in Report 2 relative to Report 1\n"
    ans += "Note: if the Report 1 value is 0, a numerical change (+ prefix) will be displayed.\n\n"
    symbol = ""
    if rep1.diversions != 0:
        diversions = (rep1.diversions - rep2.diversions)/rep1.diversions * 100
        symbol = ""
    else:
        diversions = rep2.diversions - rep1.diversions
        symbol = "+"
    ans += f"Number of diversions: {symbol} {diversions}\n"

    if rep1.cancellations != 0:
        cancellations = (rep1.cancellations - rep2.cancellations)/rep1.cancellations * 100
        symbol = ""
    else:
        cancellations = rep2.cancellations - rep1.cancellations
        symbol = "+"
    ans += f"Number of cancellations: {symbol}{cancellations}\n"

    # Fuel used
    if rep1.tot_fuel_used != 0:
        tot_fuel_used = (rep1.tot_fuel_used - rep2.tot_fuel_used)/rep1.tot_fuel_used * 100
        symbol = ""
    else:
        tot_fuel_used = rep2.tot_fuel_used - rep1.tot_fuel_used
        symbol = "+"
    ans += f"Total amount of fuel used: {symbol} {tot_fuel_used}\n"
    
    if rep1.fuel_avg != 0:
        fuel_avg = (rep1.fuel_avg - rep2.fuel_avg)/rep1.fuel_avg * 100
        symbol = ""
    else:
        fuel_avg = rep2.fuel_avg - rep2.fuel_avg
        symbol = "+"
    
    ans += f"Average amount of fuel used: {symbol} {fuel_avg}\n"
    
    # Total number of planes generated
    if rep1.total_planes != 0:
        total_planes = (rep1.total_planes - rep2.total_planes)/rep1.total_planes * 100
        symbol = ""
    else:
        total_planes = rep2.total_planes - rep1.total_planes
        symbol = "+"
    f"Total number of planes generated: {symbol} {total_planes}\n\n"

    # Maximum number of planes in holding queue
    if rep1.max_hold != 0:
        holding_max = (rep1.max_hold - rep2.max_hold)/rep1.max_hold * 100
        symbol = ""
    else:
        holding_max = rep2.max_hold - rep1.max_hold
        symbol = "+"
    ans += f"Maximum number of planes in holding queue: {symbol} {holding_max}\n"
        
    # Maximum number of planes in runway queue
    if rep1.queue_max != 0:
        queue_max = (rep1.queue_max - rep2.queue_max)/rep1.queue_max * 100
        symbol = ""
    else:
        queue_max = rep2.queue_max - rep1.queue_max
        symbol = "+"
    f"Maximum number of planes in runway queue: {symbol} {queue_max}\n\n"

    # Wait times
    if rep1.max_wait != 0:
        max_wait = (rep1.max_wait - rep2.max_wait)/rep1.max_wait * 100
        symbol = ""
    else:
        max_wait = rep2.max_wait - rep1.max_wait
        symbol = "+"
    ans += f"Maximum wait time: {symbol} {max_wait}\n"
        

    if rep1.mean_wait != 0:
        mean_wait = (rep1.mean_wait - rep2.mean_wait)/rep1.mean_wait * 100
        symbol = ""
    else: 
        mean_wait = rep2.mean_wait - rep1.mean_wait
        symbol = "+"
    ans += f"Average wait time: {symbol} {mean_wait}\n\n"

    # Hold times
    if max_hold != 0:
        max_hold = (rep1.max_hold - rep2.max_hold)/rep1.max_hold * 100
        symbol = ""
    else:
        max_hold = rep2.max_hold - rep1.max_hold
        symbol = "+"
    ans += f"Maximum hold time: {symbol} {max_hold}\n"
    
    if mean_hold != 0:
        mean_hold = (rep1.mean_hold - rep2.mean_hold)/rep1.mean_hold * 100
        symbol = ""
    else:
        mean_hold = rep2.mean_hold - rep1.mean_hold
        symbol = "+"
    ans += f"Average hold time: {symbol} {mean_hold}\n\n"

    # Take-off times
    if max_take_off != 0:
        max_take_off = (rep1.max_take_off - rep2.max_take_off)/rep1.max_take_off * 100
        symbol = ""
    else:
        max_take_off = rep2.max_take_off - rep1.max_take_off
        symbol = "+"
    ans+= f"Maximum take-off time: {symbol} {max_take_off}\n"

    if mean_take_off != 0:
        mean_take_off = (rep1.mean_take_off - rep2.mean_take_off)/rep1.mean_take_off * 100
        symbol = ""
    else:
        mean_take_off = rep2.mean_take_off - rep1.mean_take_off
        symbol = "+"
    ans += f"Average take-off time: {symbol} {mean_take_off}\n\n"

    # Arrival times
    if max_arrival != 0:
        max_arrival = (rep1.max_arrival - rep2.max_arrival)/rep1.max_arrival * 100
        symbol = ""
    else:
        max_arrival = rep2.max_arrival - rep1.max_arrival
        symbol = "+"
    ans+= f"Maximum arrival time: {symbol} {max_arrival}\n"

    if mean_arrival != 0:
        mean_arrival = (rep1.mean_arrival - rep2.mean_arrival)/rep1.mean_arrival * 100
        symbol = ""
    else:
        mean_arrival = rep2.mean_arrival - rep1.mean_arrival
        symbol = "+"
    ans += f"Average arrival time: {symbol} {mean_arrival}\n\n"

    return ans


#TODO; add a way to record the time of a diversion? maybe relate it to something


#NOTE: these are slightly different, using the plane list from presetcontroller instead
"""def plot_actualtime_delay(preset : PresetController):
    plane_list = preset.plane_list
    delays_seconds = []
    actualTime_seconds = []
    for plane in plane_list:
        delays_seconds.append((plane.left_hold - plane.entered_hold).total_seconds())
        actualTime_seconds.append(plane.actual_time.to_seconds())

    
    location = Path("./")
    filename = location / "actualtime_delay.pdf"

    x = np.array(actualTime_seconds)
    y = np.array(delays_seconds)

    plt.xlabel("Plane actual arrival time (s)")
    plt.ylabel("Delays from holding queue (s)")

    plt.scatter(x,y)
    plt.savefig(filename) """


# Plots the actual arrival time against the time spent in holding queue
def plot_arrival_holdtime(preset : PresetController):
    plane_list = preset.plane_list
    holdtime_seconds = []
    actualTime_seconds = []
    for plane in plane_list:
        holdtime_seconds.append((plane.left_hold - plane.entered_hold).total_seconds())
        actualTime_seconds.append(plane.actual_time.to_seconds())

    
    location = Path("./")
    filename = location / "arrival_holdtime.pdf"

    x = np.array(actualTime_seconds)
    y = np.array(holdtime_seconds)

    plt.xlabel("Plane actual arrival time (s)")
    plt.ylabel("Time spent in holding queue (s)")

    plt.scatter(x,y)
    plt.savefig(filename) 



#NOTE: the plots below arent good, used as examples. remove later
def plot_takeoff_delays(rep : PerformanceReport):
    # Sorting the values, gettings the unique times and their occurences for the plot
    rep.take_off_delays.sort()
    uniqueTimesQuantity = []
    prevSameIndex = 0
    for i in range(0, len(rep.take_off_delays)):
        if i == 0:
            uniqueTimesQuantity[i][0] = rep.take_off_delays[i]
            uniqueTimesQuantity[i][1] += 1
        elif rep.take_off_delays[i] == uniqueTimesQuantity[prevSameIndex][0]:
            uniqueTimesQuantity[prevSameIndex][1] += 1
        else:
            uniqueTimesQuantity[i][0] = rep.take_off_delays[i]
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


def plot_arrival_delays(rep : PerformanceReport):
    # Sorting the values, gettings the unique times and their occurences for the plot
    rep.arrival_delay_times.sort()
    uniqueTimesQuantity = []
    prevSameIndex = 0
    for i in range(0, len(rep.arrival_delay_times)):
        if i == 0:
            uniqueTimesQuantity[i][0] = rep.arrival_delay_times[i]
            uniqueTimesQuantity[i][1] += 1
        elif rep.arrival_delay_times[i] == uniqueTimesQuantity[prevSameIndex][0]:
            uniqueTimesQuantity[prevSameIndex][1] += 1
        else:
            uniqueTimesQuantity[i][0] = rep.arrival_delay_times[i]
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




def plot_holdtimes(rep : PerformanceReport):
    #for now sorting like this, if there are issues, can make a copy of hte list instead (but as final call should be fine)
    
    # Sorting the values, gettings the unique times and their occurences for the plot
    rep.hold_times.sort()
    uniqueTimesQuantity = []
    prevSameIndex = 0
    for i in range(0, len(rep.hold_times)):
        if i == 0:
            uniqueTimesQuantity[i][0] = rep.hold_times[i]
            uniqueTimesQuantity[i][1] += 1
        elif rep.hold_times[i] == uniqueTimesQuantity[prevSameIndex][0]:
            uniqueTimesQuantity[prevSameIndex][1] += 1
        else:
            uniqueTimesQuantity[i][0] = rep.hold_times[i]
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
        

def plot_waittimes(rep : PerformanceReport):
    # Sorting the values, gettings the unique times and their occurences for the plot
    rep.wait_times.sort()
    uniqueTimesQuantity = []
    prevSameIndex = 0
    for i in range(0, len(rep.wait_times)):
        if i == 0:
            uniqueTimesQuantity[i][0] = rep.wait_times[i]
            uniqueTimesQuantity[i][1] += 1
        elif rep.wait_times[i] == uniqueTimesQuantity[prevSameIndex][0]:
            uniqueTimesQuantity[prevSameIndex][1] += 1
        else:
            uniqueTimesQuantity[i][0] = rep.wait_times[i]
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









