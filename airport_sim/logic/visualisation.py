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
            return ""
        

    def getAvailablePresets(self):
        try:
            # Create a PresetController instance
            preset_controller = PresetController()
            
            # Get list of saved presets (using instance, not class)
            preset_times = preset_controller.getPresetSaveTimes()
            
            output = []
            for (preset_id, saved_at) in preset_times:                
                # Load each preset
                if preset_controller.loadPreset(preset_id):
                    # Get first 5 planes
                    planes = []
                    for i, p in enumerate(preset_controller.plane_list):
                        if i >= 5:
                            break
                        planes.append(p.return_data())

                    # Get report data safely
                    report_dict = {}
                    if preset_controller.report:
                        try:
                            report_dict = preset_controller.report.outputReport_dict()
                        except Exception as e:
                            print(f"Report outputReport_dict() failed: {e}")
                            report_dict = preset_controller.report.__dict__
                    
                    output.append({
                        "id": preset_id,
                        "saved_at": saved_at,
                        "vars": {
                            "departure_runways": preset_controller.departure_runways,
                            "landing_runways": preset_controller.landing_runways,
                            "mixed_runways": preset_controller.mixed_runways
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
