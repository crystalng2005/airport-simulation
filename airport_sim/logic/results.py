import json
import os
from datetime import datetime, timezone
from logic.report import PerformanceReport
import logic.globals.reportData as RD

class ResultsController:
    def __init__(self) -> None:
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

    def save_result(self) -> bool:
        """
        Saves the current simulation report to the results file.
        The report stored in the global reportData object is converted
        into a JSON-serialisable format and appended to the results list.
        Only the most recent `max_results` reports are retained.

        Returns:
            True if the result was successfully saved, otherwise False.
        """
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

    def load_results(self, index: int) -> PerformanceReport | None:
        """
        Loads a specific simulation result by its index.
        The stored report data is converted back into a PerformanceReport
        object and stored in the controller.

        Args:
            index: The index of the result in the results list.

        Returns:
            The reconstructed PerformanceReport object if successful,
            otherwise None.
        """
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

    def get_result_save_times(self) -> list[tuple[int, str]]:
        """
        Retrieves the save timestamps for all stored results.

        Returns:
            A list of tuples containing:
                (result_index, saved_timestamp)
        """
        with open(self.results_file, 'r') as f:
            results = json.load(f)

        return [(i, r["saved_at"]) for i, r in enumerate(results)]


    def get_all_results(self) -> list[dict]:
        """
        Retrieves all stored results and formats them for display.

        Returns:
            A list of dictionaries representing all saved results.
        """
        with open(self.results_file, 'r') as f:
            results = json.load(f)

        output = []
        for i, r in enumerate(results):
            report = self.load_results(i)

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
                "report": report.output_report_dict()
            })

        return output

    def get_one_result(self, id: int) -> dict | None:
        """
        Retrieves a single result by its ID.
        The stored report data is reconstructed into a PerformanceReport
        object and returned as a formatted dictionary.

        Args:
            id: The ID (index) of the result.

        Returns:
            A dictionary containing result details if found,
            otherwise None.
        """
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
                "report": report.output_report_dict()
            }       
        except (IOError, IndexError, KeyError):
            return None

    def export_result_by_id(self, id: int) -> str | None:
        """
        Exports a stored result to a text report file.
        The result is first loaded using its ID and then exported
        using the export_report method.

        Args:
            id: The ID of the result to export.

        Returns:
            The file path of the exported report if successful,
            otherwise None.
        """
        report = self.load_results(id)
        if report is None:
            return None
        return self.export_report(report)

    def export_report(self, PR: PerformanceReport) -> str | None:
        """
        Exports a PerformanceReport to a formatted text file.
        The report is written to the exports directory with a
        timestamped filename.

        Args:
            PR: The PerformanceReport object to export.

        Returns:
            The file path of the exported report if successful,
            otherwise None.
        """
        export_dir = os.path.join(os.path.dirname(__file__), '..', 'exports')

        try:
            os.makedirs(export_dir, exist_ok=True)

            now = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
            export_file = os.path.join(export_dir, f'simulation-report-{now}.txt')

            report = PR.output_report_dict()

            content = (
                '===========================================================\n'
                'AIRPORT SIMULATION REPORT\n'
                '===========================================================\n\n'

                '-----------------------------------------------------------\n'
                'Summary\n'
                '-----------------------------------------------------------\n'
                f"Start time: {report.get('start_time', 'N/A')}\n"
                f"End time: {report.get('completed_at', 'N/A')}\n"
                f"Total duration: {report.get('duration', 'N/A')}\n\n"

                '-----------------------------------------------------------\n'
                'Overall outcome\n'
                '-----------------------------------------------------------\n'
                f"Total flights handled: {report.get('total_planes', 0)}\n"
                f"Flights diverted: {report.get('diversions', 0)}\n"
                f"Flights cancelled: {report.get('cancellations', 0)}\n"
                f"Operational efficiency: {report.get('efficiency', 0)}%\n\n"

                '-----------------------------------------------------------\n'
                'Queue and holding overview\n'
                '-----------------------------------------------------------\n'
                f"Longest runway queue: {report.get('queue_max', 0)} flights\n"
                f"Longest holding pattern queue: {report.get('holding_max', 0)} flights\n\n"

                '-----------------------------------------------------------\n'
                'Fuel and delays\n'
                '-----------------------------------------------------------\n'
                f"Total fuel used: {report.get('tot_fuel_used', 0):.1f} units\n"
                f"Average fuel used per flight: {report.get('avg_fuel_per_plane', 0):.1f} units\n"

                f"Average wait before runway access: {report.get('avg_wait_time', 0)} minutes\n"
                f"Average holding time: {report.get('avg_hold_time', 0)} minutes\n"
                f"Average take-off delay: {report.get('avg_takeoff_time', 0)} minutes\n"
                f"Average arrival delay: {report.get('avg_arrival_time', 0)} minutes\n\n"

                '-----------------------------------------------------------\n'
                'Additional metrics\n'
                '-----------------------------------------------------------\n'
                f"Maximum hold time: {report.get('max_hold_time', 0)} minutes\n"
                f"Maximum take-off time: {report.get('max_takeoff_time', 0)} minutes\n"
                f"Maximum arrival time: {report.get('max_arrival_time', 0)} minutes\n\n"

                f"Standard deviation of wait times: {report.get('std_wait_time', 0)} minutes\n"
                f"Standard deviation of hold times: {report.get('std_hold_time', 0)} minutes\n"
                f"Standard deviation of take-off delays: {report.get('std_take_off_time', 0)} minutes\n"
                f"Standard deviation of arrival delays: {report.get('std_arrival_time', 0)} minutes\n\n"

                '-----------------------------------------------------------\n'
                'Notes on data\n'
                '-----------------------------------------------------------\n'
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
        """
        Resets the controller state.
        Clears the currently stored result reference so the controller
        is ready for a new simulation.

        Returns:
            True once the reset operation completes.
        """
        self.result = None
        return True