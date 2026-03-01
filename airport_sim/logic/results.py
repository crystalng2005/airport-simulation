import json
import os
from datetime import datetime
from logic.report import PerformanceReport
import globals.reportData as RD


class ResultsController:

    def __init__(self):
        self.result = None
        self.max_results = 50

        self.data_dir = os.path.join(
            os.path.dirname(__file__), '..', 'data'
        )

        self.results_file = os.path.join(self.data_dir, 'results.json')

        # Create file if it doesn't exist
        if not os.path.exists(self.results_file):
            with open(self.results_file, 'w') as f:
                json.dump([], f)

    # Save current report file as result in results.json
    def saveResult(self) -> bool:
        try:
            with open(self.results_file, 'r') as f:
                results = json.load(f)

            now = datetime.now(datetime.timezone.utc).isoformat()
            self.result = RD.reportData

            results.append({
                "saved_at": now,
                "result": self.result.__dict__
            })

            # Keep only the last 50 results (pops the oldest one if necessary)
            if len(results) > self.max_results:
                results.pop(0)

            with open(self.results_file, 'w') as f:
                json.dump(results, f, indent=4)

            return True
        except IOError:
            return False

    # load a specific result, using its index as the ID
    def loadResults(self, index: int):
        try:
            with open(self.results_file, 'r') as f:
                results = json.load(f)

            result_data = results[index]["result"]

            result = PerformanceReport.__new__(PerformanceReport)
            result.__dict__.update(result_data)
            self.result = result

            return self.result
        except (IOError, IndexError, KeyError):
            return None

    # Return a list of all indexes + saving timestamps of each result in list
    def getResultSaveTimes(self) -> list[tuple[int, str]]:
        with open(self.results_file, 'r') as f:
            results = json.load(f)

        return [(i, r["saved_at"]) for i, r in enumerate(results)]


    def getAllResults(self):
        with open(self.results_file, 'r') as f:
            results = json.load(f)

        output = []
        for i, r in enumerate(results):
            report = self.loadResults(i)

            output.append({
                "id": i,
                "completed_at": r["saved_at"],
                "duration": 1, # ------------------------------------
                "config": {
                    "total_runways": report.runway_amount,
                    "departure_runways": 2, #--------------------------------
                    "landing_runways": 2, # -------------------------------
                    "mixed_runways": 1 # ----------------------
                },
                "report": {
                    "total_planes": report.total_planes,
                    "diversions": report.diversions,
                    "cancellations": report.cancellations, 
                    "queue_max": report.queue_max,
                    "holding_max": report.holding_max,
                    "tot_fuel_used": report.tot_fuel_used,
                    "tot_wait_time": report.tot_wait_time,
                    "efficiency": report.getEfficiency() 
                }
            })

            return output

    def getOneResult(self,id:int):
        try:
            with open(self.results_file, 'r') as f:
                results = json.load(f)

            result_data = results[id]["result"]

            report = PerformanceReport.__new__(PerformanceReport)
            report.__dict__.update(result_data)

            return {
                "id": id,
                "completed_at": results[id]["saved_at"],
                "duration": 1, # ------------------------------------
                "config": {
                    "total_runways": report.runway_amount,
                    "departure_runways": 2, #--------------------------------
                    "landing_runways": 2, # -------------------------------
                    "mixed_runways": 1 # ----------------------
                },
                "report": {
                    "total_planes": report.total_planes,
                    "diversions": report.diversions,
                    "cancellations": report.cancellations, 
                    "queue_max": report.queue_max,
                    "holding_max": report.holding_max,
                    "tot_fuel_used": report.tot_fuel_used,
                    "tot_wait_time": report.tot_wait_time,
                    "efficiency": report.getEfficiency() 
                }
            }       
        except (IOError, IndexError, KeyError):
            return None

        


    # Given a specific report ID, exports it to the exports folder
    def exportResults(self, id: int) -> bool:
        return self.exportResults(self, self.loadResults(self, id))

    # Given a specific report, exports it to the exports folder
    def exportResults(self, PR: PerformanceReport) -> bool:
        export_dir = os.path.join(os.path.dirname(__file__), '..', 'exports')

        try:
            os.makedirs(export_dir, exist_ok=True)

            now = datetime.now(datetime.timezone.utc).isoformat()
            export_file = os.path.join(export_dir, f'results-{now}.json')

            result = PR.__dict__

            with open(export_file, 'w') as f:
                json.dump(result, f, indent=4)

            return True
        except (Exception, IOError):
            return False

    def reset(self) -> bool:
        self.result = None
        return True