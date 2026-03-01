import logic.report as R

#NOTE: will need to initialise this at the beginning of the simulation
def init(runway_amount, landings_per_hour, start_time):
    global reportData
    reportData = R.PerformanceReport(runway_amount, landings_per_hour, start_time)


