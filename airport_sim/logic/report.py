from __future__ import annotations
import statistics
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import datetime


# PerformanceReport Class

class PerformanceReport:
    def __init__(self, runway_total, runways_mixed, runways_departure, runways_landing, landings_per_hour, start_time):
        # Simulation preset data
        self.runway_total = runway_total
        self.runways_mixed = runways_mixed
        self.runways_departure = runways_departure
        self.runways_landing = runways_landing
        self.landings_per_hour = landings_per_hour
        self.start_time = start_time

        # Data from running the simulation
        self.diversions = 0
        self.cancellations = 0
        self.total_planes = 0
        self.tot_wait_time = 0
        self.tot_fuel_used = 0

        # Time monitored per plane, each counted in seconds
        self.wait_times = []
        self.hold_times = []
        self.take_off_delays = []
        self.arrival_delay_times = []

        # Queue size data
        self.queue_max = 0
        self.queue_current = 0

        self.holding_max = 0
        self.holding_current = 0




    # Records the time the simulation has finished
    # Call when ending the simulation
    def setFinishTime(self, finishTime : datetime):
        self.finish_time = finishTime
        self.duration = self.finish_time - self.start_time
        

    # Generates the report based on collected data
    def generateReport(self):
        self.efficiency = self.getEfficiency()
        
        # Maximum of each value stored in the lists
        self.max_wait = max(self.wait_times) if self.wait_times else 0
        self.max_hold = max(self.hold_times) if self.hold_times else 0
        self.max_take_off = max(self.take_off_delays) if self.take_off_delays else 0
        self.max_arrival = max(self.arrival_delay_times) if self.arrival_delay_times else 0

        # Mean of the values stored in the lists
        self.mean_wait = round(statistics.mean(self.wait_times)) if self.wait_times else 0
        self.mean_hold = round(statistics.mean(self.hold_times)) if self.hold_times else 0
        self.mean_take_off = round(statistics.mean(self.take_off_delays)) if self.take_off_delays else 0
        self.mean_arrival = round(statistics.mean(self.arrival_delay_times)) if self.arrival_delay_times else 0

        # Standard deviation of the values stored in the lists
        self.std_wait = round(statistics.stdev(self.wait_times)) if len(self.wait_times) >= 2 else 0
        self.std_hold = round(statistics.stdev(self.hold_times)) if len(self.hold_times) >= 2 else 0
        self.std_take_off = round(statistics.stdev(self.take_off_delays)) if len(self.take_off_delays) >= 2 else 0
        self.std_arrival = round(statistics.stdev(self.arrival_delay_times)) if len(self.arrival_delay_times) >= 2 else 0

        # Calculated the average fuel used per plane, checks if total planes are 0
        self.fuel_avg = 0
        if self.total_planes > 0:
            self.fuel_avg = round(self.tot_fuel_used / self.total_planes)


    # Returns the duration in seconds as a formatted string
    def string_duration(self):
        if hasattr(self.duration, 'total_seconds'):
            inSeconds = int(self.duration.total_seconds())
        else:
            inSeconds = int(self.duration)
        hours, remainder = divmod(inSeconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours} hours, {minutes} minutes, {seconds} seconds"
    

    # Outputs the values for the reports as a dictionary
    def outputReport_dict(self):
        return {
            "start_time" : self.start_time,
            "completed_at" : self.finish_time,
            "duration" : self.string_duration(),

            "total_planes": self.total_planes,
            "diversions": self.diversions,
            "cancellations": self.cancellations,

            "tot_fuel_used": self.tot_fuel_used,
            "avg_fuel_per_plane" : self.fuel_avg,

            "holding_max": self.holding_max,
            "queue_max": self.queue_max,
            
            "tot_wait_time": self.tot_wait_time,
            "avg_wait_time": self.mean_wait, 
            "std_wait_time" : self.std_wait,

            "max_hold_time" : self.max_hold,
            "avg_hold_time" : self.mean_hold,
            "std_hold_time" : self.std_hold,

            "max_takeoff_time" : self.max_take_off,
            "avg_takeoff_time" : self.mean_take_off,
            "std_take_off_time" : self.std_take_off,

            "max_arrival_time" : self.max_arrival,
            "avg_arrival_time" : self.mean_arrival,
            "std_arrival_time" : self.std_arrival,

            "efficiency": self.efficiency           
        }


    # Generates the report and returns as a formatted string
    def outputReport_string(self) -> str:
        self.generateReport()

        return (f"Number of diversions: {self.diversions}\n"
                f"Number of cancellations: {self.cancellations}\n"
                f"Total amount of fuel used: {self.tot_fuel_used}\n"
                f"Average amount of fuel used: {self.fuel_avg}\n"
                f"Total number of planes generated: {self.total_planes}\n\n"

                f"Maximum number of planes in holding queue: {self.holding_max}\n"
                f"Maximum number of planes in runway queue: {self.queue_max}\n\n"

                f"Maximum wait time: {self.max_wait}\n"
                f"Average wait time: {self.mean_wait}\n"
                f"Standard deviation of wait times: {self.std_wait}\n\n"

                f"Maximum hold time: {self.max_hold}\n"
                f"Average hold time: {self.mean_hold}\n"
                f"Standard deviation of hold times: {self.std_hold}\n\n"

                f"Maximum take-off time: {self.max_take_off}\n"
                f"Average take-off time: {self.mean_take_off}\n"
                f"Standard deviation of take-off times: {self.std_take_off}\n\n"

                f"Maximum arrival time: {self.max_arrival}\n"
                f"Average arrival time: {self.mean_arrival}\n"
                f"Standard deviation of arrival times: {self.std_arrival}\n\n")


    # Resets the values stored in the report
    def reset(self) -> bool:
        self.diversions = 0
        self.cancellations = 0
        self.total_planes = 0
        self.tot_wait_time = 0
        self.tot_fuel_used = 0

        self.hold_times = []
        self.wait_times = []
        self.take_off_delays = []
        self.arrival_delay_times = []
        
        self.queue_max = 0
        self.queue_current = 0

        self.holding_max = 0
        self.holding_current = 0


    # Calculates the efficiency
    def getEfficiency(self):
        if self.total_planes > 0:
            return (round((self.total_planes - self.diversions - self.cancellations)/self.total_planes * 100))
        return 0


    # Increments the number of planes currently in the runway queue
    # Checks if the maximum number needs to be updated
    def incQueueCurrent(self):
        self.queue_current +=1 
        if self.queue_current > self.queue_max:
            self.queue_max = self.queue_current 

    # Decrements the number of planes currently in the runway queue
    def decQueueCurrent(self):
        if self.queue_current > 0:
            self.queue_current -= 1

    # Increments the number of planes currently in the holding queue
    # Checks if the maximum number needs to be updated
    def incHoldingCurrent(self):
        self.holding_current += 1
        if self.holding_current > self.holding_max:
            self.holding_max = self.holding_current

    # Decrements the number of planes currently in the holding queue
    def decHoldingCurrent(self):
        if self.holding_current > 0:
            self.holding_current -= 1

    def generate_plots_base64(self):
        """Generate distribution plots for the report and return them as base64-encoded PNGs."""
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import io
        import base64

        plots = {}

        def make_histogram(data, title, xlabel, ylabel="Number of planes"):
            if not data:
                return None
            fig, ax = plt.subplots(figsize=(4, 2.8))
            ax.hist(data, bins=min(20, max(5, len(set(data)))), color='#3b82f6', edgecolor='#1e3a8a', alpha=0.85)
            ax.set_title(title, fontsize=10, fontweight='bold')
            ax.set_xlabel(xlabel, fontsize=8)
            ax.set_ylabel(ylabel, fontsize=8)
            ax.tick_params(labelsize=7)
            ax.grid(axis='y', alpha=0.3)
            fig.tight_layout()
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=100)
            plt.close(fig)
            buf.seek(0)
            return base64.b64encode(buf.read()).decode('utf-8')

        def make_bar_chart(categories, values, title, ylabel):
            fig, ax = plt.subplots(figsize=(4, 2.8))
            bars = ax.bar(categories, values, color=['#3b82f6', '#ef4444', '#f59e0b'])
            ax.set_title(title, fontsize=10, fontweight='bold')
            ax.set_ylabel(ylabel, fontsize=8)
            ax.tick_params(axis='x', labelsize=7)
            ax.tick_params(axis='y', labelsize=7)
            ax.grid(axis='y', alpha=0.3)
            for bar in bars:
                h = bar.get_height()
                ax.text(bar.get_x() + bar.get_width() / 2, h, f'{h:.1f}', ha='center', va='bottom', fontsize=6)
            fig.tight_layout()
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=100)
            plt.close(fig)
            buf.seek(0)
            return base64.b64encode(buf.read()).decode('utf-8')

        plots['wait_times'] = make_histogram(
            self.wait_times,
            'Distribution of Wait Times',
            'Wait time (seconds)'
        )

        plots['hold_times'] = make_histogram(
            self.hold_times,
            'Distribution of Hold Times',
            'Hold time (seconds)'
        )

        plots['takeoff_delays'] = make_histogram(
            self.take_off_delays,
            'Distribution of Take-off Delays',
            'Take-off delay (seconds)'
        )

        plots['arrival_delays'] = make_histogram(
            self.arrival_delay_times,
            'Distribution of Arrival Delays',
            'Arrival delay (seconds)'
        )

        plots['outcome_summary'] = make_bar_chart(
            ['Total Planes', 'Diversions', 'Cancellations'],
            [self.total_planes, self.diversions, self.cancellations],
            'Outcome Summary',
            'Plane count'
        )

        plots['operations_snapshot'] = make_bar_chart(
            ['Efficiency %', 'Avg Wait', 'Avg Hold'],
            [self.efficiency, self.mean_wait, self.mean_hold],
            'Operations Snapshot',
            'Value'
        )

        # Filter out None values (empty data)
        return {k: v for k, v in plots.items() if v is not None}

    @staticmethod
    def generate_comparison_plots_base64(rep1, rep2, label1="Sim 1", label2="Sim 2"):
        """Generate side-by-side bar chart comparisons of two reports as base64 PNGs."""
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import io
        import base64

        plots = {}

        def make_bar_chart(categories, vals1, vals2, title):
            fig, ax = plt.subplots(figsize=(5, 3))
            x = range(len(categories))
            width = 0.35
            bars1 = ax.bar([i - width/2 for i in x], vals1, width, label=label1, color='#3b82f6', alpha=0.85)
            bars2 = ax.bar([i + width/2 for i in x], vals2, width, label=label2, color='#f59e0b', alpha=0.85)
            ax.set_xticks(list(x))
            ax.set_xticklabels(categories, fontsize=7)
            ax.set_title(title, fontsize=10, fontweight='bold')
            ax.legend(fontsize=7)
            ax.tick_params(labelsize=7)
            ax.grid(axis='y', alpha=0.3)
            # Add value labels on bars
            for bar in bars1:
                h = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2, h, f'{h:.0f}', ha='center', va='bottom', fontsize=6)
            for bar in bars2:
                h = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2, h, f'{h:.0f}', ha='center', va='bottom', fontsize=6)
            fig.tight_layout()
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=100)
            plt.close(fig)
            buf.seek(0)
            return base64.b64encode(buf.read()).decode('utf-8')

        def get(report_dict, key, default=0):
            return report_dict.get(key, default)

        r1 = rep1 if isinstance(rep1, dict) else rep1.outputReport_dict()
        r2 = rep2 if isinstance(rep2, dict) else rep2.outputReport_dict()

        # Key counts comparison
        plots['key_counts'] = make_bar_chart(
            ['Total Planes', 'Diversions', 'Cancellations'],
            [get(r1, 'total_planes'), get(r1, 'diversions'), get(r1, 'cancellations')],
            [get(r2, 'total_planes'), get(r2, 'diversions'), get(r2, 'cancellations')],
            'Planes, Diversions & Cancellations'
        )

        # Queue & holding comparison
        plots['queues'] = make_bar_chart(
            ['Max Queue', 'Max Holding'],
            [get(r1, 'queue_max'), get(r1, 'holding_max')],
            [get(r2, 'queue_max'), get(r2, 'holding_max')],
            'Queue & Holding Comparison'
        )

        # Wait & hold times comparison
        plots['times'] = make_bar_chart(
            ['Avg Wait', 'Avg Hold', 'Avg Take-off', 'Avg Arrival'],
            [get(r1, 'avg_wait_time'), get(r1, 'avg_hold_time'), get(r1, 'avg_takeoff_time'), get(r1, 'avg_arrival_time')],
            [get(r2, 'avg_wait_time'), get(r2, 'avg_hold_time'), get(r2, 'avg_takeoff_time'), get(r2, 'avg_arrival_time')],
            'Average Times Comparison'
        )

        # Fuel & efficiency comparison
        plots['fuel_efficiency'] = make_bar_chart(
            ['Total Fuel', 'Avg Fuel/Plane', 'Efficiency (%)'],
            [get(r1, 'tot_fuel_used'), get(r1, 'avg_fuel_per_plane'), get(r1, 'efficiency')],
            [get(r2, 'tot_fuel_used'), get(r2, 'avg_fuel_per_plane'), get(r2, 'efficiency')],
            'Fuel Usage & Efficiency'
        )

        return plots

