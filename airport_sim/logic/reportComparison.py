import statistics
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from report import PerformanceReport
from logic.presets import PresetController

    
def compare_reports(rep1 : PerformanceReport, rep2 : PerformanceReport) -> dict:
    """
    Generates a dictionary storing the results of the comparison of two PerformanceReport
    objects.

    Calculates the percentage change, absolute change, and whether there is an improvement for 
    each of the following metrics:
    - Diversions
    - Cancellations
    - Fuel used (total and average)
    - Total number of planes
    - Holding queue maximum size
    - Runway queue maximum size
    - Wait time (max and average)
    - Holding time (max and average)
    - Take-off time (max and average)
    - Arrival time (max and average)
    - Efficiency (= total planes - diversions - cancellations)
    """
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

