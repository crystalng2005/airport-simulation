# VisualisationController Class
from logic.models import Runway
from logic.plane import Plane
from logic.results import ResultsController
from logic.presets import PresetController
import os

class VisualisationController:
    def __init__(self, tickspeed: int = 5): # Tickspeed is 5 minutes by default
        self.tickspeed = tickspeed

    def getAllSimulationResults(self):
        return ResultsController.getAllResults()

    def getSimulationReport(self, sim_id):
        report = ResultsController.loadResults(sim_id)
        if report != None:
            return {
                "report": report.outputReport_dict()
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
                "report": PresetController.report.outputReport_dict()
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
            "report": PresetController.report.outputReport_dict()
        }
