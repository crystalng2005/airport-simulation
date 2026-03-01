from datetime import datetime
from typing import List
from queue import Queue

from logic.models import Runway
from logic.plane import Plane, EmergencyStatus

import logic.globals.reportData as RD


class currentFrameActions:
    def __init__(self):
        self.current_frame_actions = []