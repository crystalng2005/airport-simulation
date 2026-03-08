import statistics
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from report import PerformanceReport
from logic.presets import PresetController



class ResultsSummary:
    def __init__(self, reports: list[PerformanceReport]):
        self.reports = reports 
        self.summarised = False


    def summariseAll(self):
        self.runways = []
        self.landings_per_hour = []
        self.diversions = []
        self.cancellations = []


        for report in self.reports:
            self.runways.append(report.runway_amount)
            self.landings_per_hour.append(report.landings_per_hour)
            self.diversions.append(report.diversions)
            self.cancellations.append(report.cancellations)

        self.summarised = True



    



## Plots for: 
    # x:Runways, y:diversions
    # x:Runways, y:cancellations
    # x:Plane number, y:diversions
    # x:plane number, y:cancellations

## QUESTIONS: 
    # do we want to plot cancellations too?
    # would it be good to somehow include the runway splits too?
    # should i make a summary text document for all the reports or not? would this be useful? graph easier to visualise

def plot_runways_diversions(reports: list[PerformanceReport]):
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
    #plt.show()
    plt.savefig(filename)

    
def plot_runways_cancellations(reports: list[PerformanceReport]):
    runways = []
    landings_per_hour = []
    diversions = []
    cancellations = []
    cancellations_per_runway = []
    avg_cancellations_per_runway = []


    for report in reports:
        runways.append(report.runway_amount)
        landings_per_hour.append(report.landings_per_hour)
        diversions.append(report.diversions)
        cancellations.append(report.cancellations)
    
    
    for i in range(0, len(runways)):
        if i == 0:
            cancellations_per_runway.append([runways[i],[cancellations[i]]])
        else:
            for j in range(0, len(cancellations_per_runway)):
                if cancellations_per_runway[j][0] == runways[i]:
                    cancellations_per_runway[j][1].append(cancellations[i])
    
    cancellations_per_runway.sort(key = lambda entry: entry[0])

    for i in range(0,len(cancellations_per_runway)):
        avg_cancellations_per_runway[i][0] = cancellations_per_runway[i][0]
        avg_cancellations_per_runway[i][1] = statistics.mean(cancellations_per_runway[i][1])


    
    location = Path("./")
    filename = location / "runways_diversions.pdf"

    x = np.array(runways)
    y = np.array(avg_diversions_per_runway)

    plt.plot(x, y, marker='o')
    plt.title('Amount of runways and the average number of diversions')
    plt.xlabel('Amount of runways')
    plt.ylabel('Number of diversions')
    #plt.show()
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
    
    





def compareReports(rep1 : PerformanceReport, rep2 : PerformanceReport):
    comparison = {}

    ## Diversions
    diversions = {
        "absolute_change" : rep2.diversions - rep1.diversions
    }

    if rep1.diversions != 0:
        diversions.update({"percent_change" : (rep1.diversions - rep2.diversions)/rep1.diversions * 100})
    else:
        diversions.update({"percent_change" : 0})

    text = ""
    improvement = False
    if diversions["percent_change"] >= 0:
        text = f"{abs(diversions["percent_change"])}% increase"
    else:
        text = f"{abs(diversions["percent_change"])}% reduction"
        improvement = True
    diversions.update({"text" : text})
    diversions.update({"is_improvement" : improvement})

    comparison.update(diversions)

    ## Cancellations
    cancellations = {
        "absolute_change" : rep2.cancellations - rep1.cancellations
    }

    if rep1.cancellations != 0:
        cancellations.update({"percent_change" : (rep1.cancellations - rep2.cancellations)/rep1.cancellations * 100})
    else:
        cancellations.update({"percent_change" : 0})

    text = ""
    improvement = False
    if cancellations["percent_change"] >= 0:
        text = f"{abs(cancellations["percent_change"])}% increase"
    else:
        text = f"{abs(cancellations["percent_change"])}% reduction"
        improvement = True
    cancellations.update({"text" : text})
    cancellations.update({"is_improvement" : improvement})

    comparison.update(cancellations)

    ## Fuel used 
    # Total
    total_fuel = {
        "absolute_change" : rep2.tot_fuel_used - rep1.tot_fuel_used
    }

    if rep1.tot_fuel_used != 0:
        total_fuel.update({"percent_change" : (rep1.tot_fuel_used - rep2.tot_fuel_used)/rep1.tot_fuel_used * 100})
    else:
        total_fuel.update({"percent_change" : 0})

    text = ""
    improvement = False
    if total_fuel["percent_change"] >= 0:
        text = f"{abs(total_fuel["percent_change"])}% increase"
    else:
        text = f"{abs(total_fuel["percent_change"])}% reduction"
        improvement =  True
    total_fuel.update({"text" : text})
    total_fuel.update({"is_improvement" : improvement})

    comparison.update(total_fuel)

    # Average
    avg_fuel = {
        "absolute_change" : rep2.fuel_avg - rep1.fuel_avg
    }

    if rep1.fuel_avg != 0:
        avg_fuel.update({"percent_change" : (rep1.fuel_avg - rep2.fuel_avg)/rep1.fuel_avg * 100})
    else:
        avg_fuel.update({"percent_change" : 0})

    text = ""
    improvement = False
    if avg_fuel["percent_change"] >= 0:
        text = f"{abs(avg_fuel["percent_change"])}% increase"
    else:
        text = f"{abs(avg_fuel["percent_change"])}% reduction"
        improvement = True
    avg_fuel.update({"text" : text})
    avg_fuel.update({"is_improvement" : improvement})

    comparison.update(avg_fuel)


    # Total planes
    total_planes = {
        "absolute_change" : rep2.total_planes - rep1.total_planes
    }

    if rep1.total_planes != 0:
        total_planes.update({"percent_change" : (rep1.total_planes - rep2.total_planes)/rep1.total_planes * 100})
    else:
        total_planes.update({"percent_change" : 0})

    text = ""
    improvement = False
    if total_planes["percent_change"] >= 0:
        text = f"{abs(total_planes["percent_change"])}% increase"
    else:
        text = f"{abs(total_planes["percent_change"])}% reduction"
        improvement = True
    total_planes.update({"text" : text})
    total_planes.update({"is_improvement" : improvement})

    comparison.update(total_planes)


    # Max hold
    holding_max = {
        "absolute_change" : rep2.holding_max - rep1.holding_max
    }

    if rep1.holding_max != 0:
        holding_max.update({"percent_change" : (rep1.holding_max - rep2.holding_max)/rep1.holding_max * 100})
    else:
        holding_max.update({"percent_change" : 0})

    text = ""
    improvement = False
    if holding_max["percent_change"] >= 0:
        text = f"{abs(holding_max["percent_change"])}% increase"
    else:
        text = f"{abs(holding_max["percent_change"])}% reduction"
        improvement = True
    holding_max.update({"text" : text})
    holding_max.update({"is_improvement" : improvement})

    comparison.update(holding_max)



    # Queue max
    queue_max = {
        "absolute_change" : rep2.queue_max - rep1.queue_max
    }

    if rep1.queue_max != 0:
        queue_max.update({"percent_change" : (rep1.queue_max - rep2.queue_max)/rep1.queue_max * 100})
    else:
        queue_max.update({"percent_change" : 0})

    text = ""
    improvement = False
    if queue_max["percent_change"] >= 0:
        text = f"{abs(queue_max["percent_change"])}% increase"
    else:
        text = f"{abs(queue_max["percent_change"])}% reduction"
        improvement = True
    queue_max.update({"text" : text})
    queue_max.update({"is_improvement" : improvement})

    comparison.update(queue_max)


    ## Wait time
    # Maximum wait time
    max_wait = {
        "absolute_change" : rep2.max_wait - rep1.max_wait
    }

    if rep1.max_wait != 0:
        max_wait.update({"percent_change" : (rep1.max_wait - rep2.max_wait)/rep1.max_wait * 100})
    else:
        max_wait.update({"percent_change" : 0})

    text = ""
    improvement = False
    if max_wait["percent_change"] >= 0:
        text = f"{abs(max_wait["percent_change"])}% increase"
    else:
        text = f"{abs(max_wait["percent_change"])}% reduction"
        improvement = True
    max_wait.update({"text" : text})
    max_wait.update({"is_improvement" : improvement})

    comparison.update(max_wait)

    # Average wait time
    mean_wait = {
        "absolute_change" : rep2.mean_wait - rep1.mean_wait
    }

    if rep1.mean_wait != 0:
        mean_wait.update({"percent_change" : (rep1.mean_wait - rep2.mean_wait)/rep1.mean_wait * 100})
    else:
        mean_wait.update({"percent_change" : 0})

    text = ""
    improvement = False
    if mean_wait["percent_change"] >= 0:
        text = f"{abs(mean_wait["percent_change"])}% increase"
    else:
        text = f"{abs(mean_wait["percent_change"])}% reduction"
        improvement = True
    mean_wait.update({"text" : text})
    mean_wait.update({"is_improvement" : improvement})

    comparison.update(mean_wait)



    ## Hold time
    # Maximum
    max_hold = {
        "absolute_change" : rep2.max_hold - rep1.max_hold
    }

    if rep1.max_hold != 0:
        max_hold.update({"percent_change" : (rep1.max_hold - rep2.max_hold)/rep1.max_hold * 100})
    else:
        max_hold.update({"percent_change" : 0})

    text = ""
    improvement = False
    if max_hold["percent_change"] >= 0:
        text = f"{abs(max_hold["percent_change"])}% increase"
    else:
        text = f"{abs(max_hold["percent_change"])}% reduction"
        improvement = True
    max_hold.update({"text" : text})
    max_hold.update({"is_improvement" : improvement})

    comparison.update(max_hold)


    # Average
    mean_hold = {
        "absolute_change" : rep2.mean_hold - rep1.mean_hold
    }

    if rep1.mean_hold != 0:
        mean_hold.update({"percent_change" : (rep1.mean_hold - rep2.mean_hold)/rep1.mean_hold * 100})
    else:
        mean_hold.update({"percent_change" : 0})

    text = ""
    improvement = False
    if mean_hold["percent_change"] >= 0:
        text = f"{abs(mean_hold["percent_change"])}% increase"
    else:
        text = f"{abs(mean_hold["percent_change"])}% reduction"
        improvement = True
    mean_hold.update({"text" : text})
    mean_hold.update({"is_improvement" : improvement})

    comparison.update(mean_hold)


    ## Takeoff time
    # Maximum
    max_take_off = {
        "absolute_change" : rep2.max_take_off - rep1.max_take_off
    }

    if rep1.max_take_off != 0:
        max_take_off.update({"percent_change" : (rep1.max_take_off - rep2.max_take_off)/rep1.max_take_off * 100})
    else:
        max_take_off.update({"percent_change" : 0})

    text = ""
    improvement = False
    if max_take_off["percent_change"] >= 0:
        text = f"{abs(max_take_off["percent_change"])}% increase"
    else:
        text = f"{abs(max_take_off["percent_change"])}% reduction"
        improvement = True
    max_take_off.update({"text" : text})
    max_take_off.update({"is_improvement" : improvement})

    comparison.update(max_take_off)


    # Average
    mean_take_off = {
        "absolute_change" : rep2.mean_take_off - rep1.mean_take_off
    }

    if rep1.mean_take_off != 0:
        mean_take_off.update({"percent_change" : (rep1.mean_take_off - rep2.mean_take_off)/rep1.mean_take_off * 100})
    else:
        mean_take_off.update({"percent_change" : 0})

    text = ""
    improvement = False
    if mean_take_off["percent_change"] >= 0:
        text = f"{abs(mean_take_off["percent_change"])}% increase"
    else:
        text = f"{abs(mean_take_off["percent_change"])}% reduction"
        improvement = True
    mean_take_off.update({"text" : text})
    mean_take_off.update({"is_improvement" : improvement})

    comparison.update(mean_take_off)



    ## Arrival time
    # Maximum
    max_arrival = {
        "absolute_change" : rep2.max_arrival - rep1.max_arrival
    }

    if rep1.max_arrival != 0:
        max_arrival.update({"percent_change" : (rep1.max_arrival - rep2.max_arrival)/rep1.max_arrival * 100})
    else:
        max_arrival.update({"percent_change" : 0})

    text = ""
    improvement = False
    if max_arrival["percent_change"] >= 0:
        text = f"{abs(max_arrival["percent_change"])}% increase"
    else:
        text = f"{abs(max_arrival["percent_change"])}% reduction"
        improvement = True
    max_arrival.update({"text" : text})
    max_arrival.update({"is_improvement" : improvement})

    comparison.update(max_arrival)


    # Average
    mean_arrival = {
        "absolute_change" : rep2.mean_arrival - rep1.mean_arrival
    }

    if rep1.mean_arrival != 0:
        mean_arrival.update({"percent_change" : (rep1.mean_arrival - rep2.mean_arrival)/rep1.mean_arrival * 100})
    else:
        mean_arrival.update({"percent_change" : 0})

    text = ""
    improvement = False
    if mean_arrival["percent_change"] >= 0:
        text = f"{abs(mean_arrival["percent_change"])}% increase"
    else:
        text = f"{abs(mean_arrival["percent_change"])}% reduction"
        improvement = True
    mean_arrival.update({"text" : text})
    mean_arrival.update({"is_improvement" : improvement})

    comparison.update(mean_arrival)


    # efficiency
    efficiency = {
        "sim1_val" : rep1.efficiency,
        "sim2_val" : rep2.efficiency,
        "absolute_change" : rep2.efficiency - rep1.efficiency,
    }

    if rep1.efficiency != 0:
        efficiency.update({"percentage_change" : (rep1.efficiency - rep2.efficiency)/rep1.efficiency * 100})
    else:
        efficiency.update({"percentage_change" : 0}) 

    text = ""
    improvement = False
    if efficiency["percent_change"] >= 0:
        text = f"{abs(efficiency["percent_change"])}% increase"
    else:
        text = f"{abs(efficiency["percent_change"])}% reduction"
        improvement = True
    efficiency.update({"text" : text})
    efficiency.update({"is_improvement" : improvement})
    
    comparison.update(efficiency)

    return comparison

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
def compareReports_string(rep1 : PerformanceReport, rep2 : PerformanceReport):
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









