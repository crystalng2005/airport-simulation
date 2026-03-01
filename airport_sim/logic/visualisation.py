# VisualisationController Class
from logic.models import Runway
from logic.plane import Plane
from logic.results import ResultsController
from logic.presets import PresetController
import os

class VisualisationController:
    def __init__(self, tickspeed: int = 5): # Tickspeed is 5 minutes by default
        self.tickspeed = tickspeed

    def getAircraftData(self, simulation) -> dict:
        """Stub method to return aircraft data for visualization."""
        # TODO: Implement data retrieval from simulation (backend)
        if simulation is None:
            return {}

        return {
            "current_time": simulation.current_time.isoformat(),
            "planes": [],
            "runways": [],
            "queues": []
        }

    def getAllSimulationResults(self):
        return ResultsController.getAllResults()

    def getSimulationReport(self, sim_id):
        report = ResultsController.loadResults(sim_id)
        if report != None:
            return {
                "success": True, #--------------???
                "report": {
                    "id": sim_id,
                    "total_planes": report.total_planes,
                    "diversions": report.diversions,
                    "cancellations": report.cancellations,
                    "tot_wait_time": report.tot_wait_time,
                    "tot_fuel_used": report.tot_fuel_used,
                    "queue_max": report.queue_max,
                    "holding_max": report.holding_max,
                    "efficiency": report.getEfficiency(),
                    "avg_wait_time": report.mean_wait,
                    "avg_fuel_per_plane": report.fuel_avg
                }
            }

    def compareSimulations(self, sim_id_1, sim_id_2):
        sim1 = ResultsController.getOneResult(sim_id_1)
        sim2 = ResultsController.getOneResult(sim_id_2)

    def exportSimulationReport(self, sim_id):
        if ResultsController.exportResults(sim_id):
            return os.path.dirname(__file__), '..', 'exports'
        else:
            return "" # Something went wrong
        

    def getAvailablePresets(self):
        L = PresetController.getPresetSaveTimes()
        output = []
        for (i,r) in enumerate(L):
            PresetController.loadPreset(i)

            planes = []
            temp = 0
            for p in PresetController.plane_list:
                temp += 1
                planes.append(p.return_data())
                if temp == 5:
                    break

            output.append({
                "id": i,
                "saved_at": r,
                "vars":{
                    "departure_runways": PresetController.departure_runways,
                    "landing_runways": PresetController.landing_runways,
                    "mixed_runways": PresetController.mixed_runways
                },
                "planes": planes,
                "report": 5 # --------------
            })
        return output

    def getPresetData(self, id):
        PresetController.loadPreset(id)
        planes = []
        temp = 0
        for p in PresetController.plane_list:
            temp += 1
            planes.append(p.return_data())

        return {
            "id": id,
            "vars":{
                "departure_runways": PresetController.departure_runways,
                "landing_runways": PresetController.landing_runways,
                "mixed_runways": PresetController.mixed_runways,
            },
            "planes": planes,
            "report": 5 # --------------
        }

    def loadPresetIntoSimulation(self, id):
        pass