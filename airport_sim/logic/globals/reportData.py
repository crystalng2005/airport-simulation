import logic.report as R

#NOTE: will need to initialise this at the beginning of the simulation
def init(runway_total, runways_mixed, runways_departure, runways_landing, landings_per_hour, start_time):
    global reportData
    reportData = R.PerformanceReport(runway_total, runways_mixed, runways_departure, runways_landing, landings_per_hour, start_time)


