# VisualisationController Class
from logic.models import Runway
from logic.plane import Plane
from logic.results import ResultsController
from logic.presets import PresetController
import logic.globals.reportData as RD
import os

class VisualisationController:
    def __init__(self, tickspeed: int = 5): # Tickspeed is 5 minutes by default
        self.tickspeed = tickspeed
        self.preset_controller = PresetController()
        self.results_controller = ResultsController()

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


    # def getAircraftData(self, simulation):
    #     if simulation is None:
    #         return []

    #     # Simulation stores live planes here by callsign.
    #     aircraft = []
    #     for plane in simulation.planes_by_call_sign.values():
    #         if plane is not None:
    #             aircraft.append(plane.return_data())

    #     return aircraft
