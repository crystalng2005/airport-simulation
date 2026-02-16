# VisualisationController Class
from models import Runway
from plane import Plane

class VisualisationController:
    def __init__(self, tickspeed: int):
        self.tickspeed = tickspeed

    def getPlaneInfo(self) -> tuple:
        pass

    def getQueue(self) -> list[Plane]:
        pass

    def getRunways(self) -> list[Runway]:
        pass