import json
import os
from datetime import datetime, timezone
from logic.report import PerformanceReport
import logic.globals.reportData as RD


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

            now = datetime.now(timezone.utc).isoformat()
            self.result = RD.reportData

            report_dict = self.result.__dict__.copy()
            for key, val in report_dict.items():
                if hasattr(val, 'isoformat'):
                    report_dict[key] = val.isoformat()
                elif hasattr(val, 'total_seconds'):
                    report_dict[key] = val.total_seconds()
                elif isinstance(val, list):
                    report_dict[key] = [
                        v.total_seconds() if hasattr(v, 'total_seconds') else v
                        for v in val
                    ]

            results.append({
                "saved_at": now,
                "result": report_dict
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
                "duration": report.duration,
                "config": {
                    "total_runways": report.runway_total,
                    "departure_runways": report.runways_departure, 
                    "landing_runways": report.runways_landing, 
                    "mixed_runways": report.runways_mixed 
                },
                "report": report.outputReport_dict()
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
                "duration": report.duration,
                "config": {
                    "total_runways": report.runway_total,
                    "departure_runways": report.runways_departure, 
                    "landing_runways": report.runways_landing, 
                    "mixed_runways": report.runways_mixed 
                },
                "report": report.outputReport_dict()
            }       
        except (IOError, IndexError, KeyError):
            return None

        


    # Given a specific report ID, exports it to the exports folder
    def exportResultById(self, id: int):
        report = self.loadResults(id)
        if report is None:
            return None
        return self.exportReport(report)

    # Given a specific report, exports it to the exports folder and returns the file path
    def exportReport(self, PR: PerformanceReport):
        export_dir = os.path.join(os.path.dirname(__file__), '..', 'exports')

        try:
            os.makedirs(export_dir, exist_ok=True)

            now = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
            export_file = os.path.join(export_dir, f'simulation-report-{now}.txt')

            report = PR.outputReport_dict()

            content = (
                'AIRPORT SIMULATION REPORT\n'
                '=========================\n\n'
                'Summary\n'
                '-------\n'
                f"Start time: {report.get('start_time', 'N/A')}\n"
                f"End time: {report.get('completed_at', 'N/A')}\n"
                f"Total duration: {report.get('duration', 'N/A')}\n\n"
                'Overall outcome\n'
                '---------------\n'
                f"Total flights handled: {report.get('total_planes', 0)}\n"
                f"Flights diverted: {report.get('diversions', 0)}\n"
                f"Flights cancelled: {report.get('cancellations', 0)}\n"
                f"Operational efficiency: {report.get('efficiency', 0)}%\n\n"
                'Queue and holding overview\n'
                '--------------------------\n'
                f"Longest runway queue: {report.get('queue_max', 0)} flights\n"
                f"Longest holding pattern queue: {report.get('holding_max', 0)} flights\n\n"
                'Fuel and delays\n'
                '---------------\n'
                f"Total fuel used: {report.get('tot_fuel_used', 0):.1f} units\n"
                f"Average fuel used per flight: {report.get('avg_fuel_per_plane', 0):.1f} units\n"
                f"Average wait before runway access: {report.get('avg_wait_time', 0)} minutes\n"
                f"Average holding time: {report.get('avg_hold_time', 0)} minutes\n"
                f"Average take-off delay: {report.get('avg_takeoff_time', 0)} minutes\n"
                f"Average arrival delay: {report.get('avg_arrival_time', 0)} minutes\n\n"
                'Detail notes\n'
                '------------\n'
                'Lower diversion and cancellation counts are better.\n'
                'A higher efficiency percentage means more flights were completed successfully.\n'
                'Use this report to compare runway setups and traffic flow settings.\n'
            )

            with open(export_file, 'w', encoding='utf-8') as f:
                f.write(content)

            return export_file
        except (Exception, IOError):
            return None

    def reset(self) -> bool:
        self.result = None
        return True