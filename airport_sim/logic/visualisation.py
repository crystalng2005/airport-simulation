# VisualisationController Class
from logic.models import Runway
from logic.plane import Plane
from logic.results import ResultsController
from logic.presets import PresetController
from logic.simulation import SimulationController
import logic.globals.reportData as RD
import os

class VisualisationController:
    def __init__(self, tickspeed: int = 5): # Tickspeed is 5 minutes by default
        self.tickspeed = tickspeed
        self.preset_controller = PresetController()
        self.results_controller = ResultsController()
        self.active_simulation = None

    def getAllSimulationResults(self):
        return self.results_controller.getAllResults()

    def getSimulationReport(self, sim_id):
        report = self.results_controller.loadResults(sim_id)
        if report != None:
            return {
                "report": report.outputReport_dict()
            }

    def compareSimulations(self, sim_id_1, sim_id_2):
        sim1 = self.results_controller.getOneResult(sim_id_1)
        sim2 = self.results_controller.getOneResult(sim_id_2)

        if sim1 is None or sim2 is None:
            return None

        r1 = sim1["report"]
        r2 = sim2["report"]

        def metric(val1, val2, lower_is_better=True):
            diff = val2 - val1
            if lower_is_better:
                improved = diff < 0
            else:
                improved = diff > 0
            sign = "+" if diff > 0 else ""
            return {"is_improvement": improved, "text": f"{sign}{diff}"}

        eff1 = r1.get("efficiency", 0)
        eff2 = r2.get("efficiency", 0)
        eff_diff = eff2 - eff1
        eff_sign = "+" if eff_diff > 0 else ""

        return {
            "simulation_1": sim1,
            "simulation_2": sim2,
            "metrics": {
                "diversions": metric(r1.get("diversions", 0), r2.get("diversions", 0)),
                "cancellations": metric(r1.get("cancellations", 0), r2.get("cancellations", 0)),
                "queue_max": metric(r1.get("queue_max", 0), r2.get("queue_max", 0)),
                "holding_max": metric(r1.get("holding_max", 0), r2.get("holding_max", 0)),
                "fuel_used": metric(r1.get("tot_fuel_used", 0), r2.get("tot_fuel_used", 0)),
                "efficiency": {
                    "is_improvement": eff_diff > 0,
                    "text": f"{eff_sign}{eff_diff:.1f}%",
                    "sim1_value": eff1,
                    "sim2_value": eff2
                }
            }
        }

    def exportSimulationReport(self, sim_id):
        if self.results_controller.exportResults(sim_id):
            return os.path.dirname(__file__), '..', 'exports'
        else:
            return ""
        

    def getAvailablePresets(self):
        try:
            
            preset_times = self.preset_controller.getPresetSaveTimes()
            
            output = []
            for (preset_id, saved_at) in preset_times:                
                # Load each preset
                if self.preset_controller.loadPreset(preset_id):
                    # Get first 5 planes
                    planes = []
                    for i, p in enumerate(self.preset_controller.plane_list):
                        if i >= 5:
                            break
                        planes.append(p.return_data())

                    report_dict = {}
                    if self.preset_controller.report:
                        try:
                            report_dict = self.preset_controller.report.outputReport_dict()
                        except Exception as e:
                            print(f"Report outputReport_dict() failed: {e}")
                            report_dict = self.preset_controller.report.__dict__
                    
                    output.append({
                        "id": preset_id,
                        "saved_at": saved_at,
                        "vars": {
                            "departure_runways": self.preset_controller.departure_runways,
                            "landing_runways": self.preset_controller.landing_runways,
                            "mixed_runways": self.preset_controller.mixed_runways
                        },
                        "planes": planes,
                        "report": report_dict
                    })
                else:
                    print(f"Failed to load preset {preset_id}")
            
            return output
            
        except Exception as e:
            return []

    def getPresetData(self, id):
        self.preset_controller.loadPreset(id)
        planes = []
        temp = 0
        for p in self.preset_controller.plane_list:
            temp += 1
            planes.append(p.return_data())

        report_dict = {}
        if self.preset_controller.report:
            try:
                report_dict = self.preset_controller.report.outputReport_dict()
            except Exception:
                report_dict = self.preset_controller.report.__dict__
        elif RD.reportData:
            report_dict = RD.reportData.__dict__.copy()

        return {
            "id": id,
            "vars":{
                "departure_runways": self.preset_controller.departure_runways,
                "landing_runways": self.preset_controller.landing_runways,
                "mixed_runways": self.preset_controller.mixed_runways,
            },
            "planes": planes,
            "report": report_dict
        }


    def startSimulation(self, data: dict):
        self.active_simulation = SimulationController(
            departures_per_hour=int(data.get('outbound_flow')),
            landings_per_hour=int(data.get('inbound_flow')),
            total_runways=int(data.get('runways')),
            departure_runways=int(data.get('departure_runways')),
            landing_runways=int(data.get('landing_runways')),
            mixed_runways=int(data.get('mixed_runways')),
            cancellation_time=int(data.get('cancellation_time')),
            total_simulation_minutes=int(data.get('duration', 100)),
            tick_minutes=5
        )
        return True

    def hasSimulation(self):
        return self.active_simulation is not None

    def tick(self):
        if not self.active_simulation:
            return False
        self.active_simulation.update()
        return True

    def getCurrentFrameActions(self):
        return self.active_simulation.getCurrentFrameActions() if self.active_simulation else []

    def getCurrentTime(self):
        return self.active_simulation.getSimulationTime() if self.active_simulation else None

    def getAircraftByCallSign(self, plane_call_sign: str):
        if not self.active_simulation:
            return None
        return self.active_simulation.getAircraftByCallSign(plane_call_sign)

    def getNumberOfRunways(self):
        return self.active_simulation.get_runway_num() if self.active_simulation else 0

    def getRunwayStatuses(self):
        return self.active_simulation.get_runway_statuses() if self.active_simulation else []

    def getRunwayModes(self):
        return self.active_simulation.get_runway_modes() if self.active_simulation else []

    def isSimulationFinished(self):
        return self.active_simulation.simulation_finished if self.active_simulation else False

    def getCurrentSimulationReport(self):
        if not self.active_simulation:
            return None
        if not self.active_simulation.simulation_finished:
            return None
        if RD.reportData is None:
            return None
        RD.reportData.generateReport()
        return RD.reportData.outputReport_dict()

    def saveSimulationAsPreset(self):
        if not self.active_simulation or not self.active_simulation.simulation_finished:
            return False
        
        sim = self.active_simulation
        self.preset_controller.departure_runways = sim.departure_runways
        self.preset_controller.landing_runways = sim.landing_runways
        self.preset_controller.mixed_runways = sim.mixed_runways
        self.preset_controller.plane_list = sim.preset_controller.plane_list
        self.preset_controller.report = RD.reportData
        return self.preset_controller.savePreset()
