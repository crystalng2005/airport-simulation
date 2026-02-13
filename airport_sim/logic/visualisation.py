# VisualisationController Class
from models import Plane, Runway

class VisualisationController:
    def __init__(self, tickspeed: int = 5): # Tickspeed is 5 minutes by default
        self.tickspeed = tickspeed

    def getAircraftData(self, simulation) -> dict:
        """Stub method to return aircraft data for visualization."""
        # TODO: Implement data retrieval from simulation (backend)
        return {
            'planes': [],
            'runways': [],
            'queues': []
        }

    def getPlaneInfo(self) -> tuple:
        pass

    def getQueue(self) -> list[Plane]:
        pass

    def getRunways(self) -> list[Runway]:
        pass