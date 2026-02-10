# PresetController Class

from models import Plane

class PresetController:

    def __init__(self, plane_list: list[Plane]):
        self.plane_list = plane_list

    def save_preset(self) -> bool:
        pass

    def reset(self) -> bool:
        pass

    def load_preset(self, preset_id: int) -> bool:
        pass
