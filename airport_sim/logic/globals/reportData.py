import logic.report as R
from datetime import datetime

def init(runway_total: int, runways_mixed: int, runways_departure: int, runways_landing: int, landings_per_hour: int, start_time: datetime):
    """
    Called to initialise the global variable storing the report object from PerformanceReport.
    Initialise at the beginning of the simulation.
    Can then be called to update the values stored in the report between different files.
    """
    global reportData
    reportData = R.PerformanceReport(runway_total, runways_mixed, runways_departure, runways_landing, landings_per_hour, start_time)


