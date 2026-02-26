import json
import os
from datetime import datetime
from logic.report import PerformanceReport
import globals.reportData as RD


class PresetController:

    def __init__(self):
        self.result = None
        self.max_results = 50

        self.data_dir = os.path.join(
            os.path.dirname(__file__), '..', '..', 'data'
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
    def loadResults(self, index: int) -> PerformanceReport:
        try:
            with open(self.results_file, 'r') as f:
                results = json.load(f)

            result_data = results[index]["result"]

            result = PerformanceReport.__new__(PerformanceReport)
            result.__dict__.update(result_data)
            self.result = result

            return self.result
        except (IOError, IndexError, KeyError):
            return False

    # Return a list of all indexes + saving timestamps of each result in list
    def getResultSaveTimes(self) -> list[tuple[int, str]]:
        with open(self.results_file, 'r') as f:
            results = json.load(f)

        return [(i, r["saved_at"]) for i, r in enumerate(results)]

    def reset(self) -> bool:
        self.result = None
        return True