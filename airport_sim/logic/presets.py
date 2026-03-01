# PresetController Class

from logic.plane import Plane
import json
import os
from datetime import datetime
from logic.report import PerformanceReport
import globals.reportData as RD

class PresetController:

    def __init__(self):
        self.plane_list = []

        self.departure_runways = 0
        self.landing_runways = 0
        self.mixed_runways = 0

        self.report = None  # Initialised before saving, goto line 75

        self.data_dir = os.path.join(
            os.path.dirname(__file__), '..', '..', 'data'
        )

        self.meta_file = os.path.join(self.data_dir, 'presets_meta.json')
        self.preset_files = [
            os.path.join(self.data_dir, f'preset{i}.json') for i in range(3)
        ]

        self.init_meta()

    # --- Meta file functions --- (Meta file keeps track of preset ID's and when they were saved)
    def init_meta(self):
        if not os.path.exists(self.meta_file):
            meta = {
                "presets": [
                    {"id": 0, "last_saved": None},
                    {"id": 1, "last_saved": None},
                    {"id": 2, "last_saved": None},
                ]
            }
            with open(self.meta_file, 'w') as f:
                json.dump(meta, f, indent=4)

    def load_meta(self):
        with open(self.meta_file, 'r') as f:
            return json.load(f)

    def save_meta(self, meta):
        with open(self.meta_file, 'w') as f:
            json.dump(meta, f, indent=4)

    def getPresetSaveTimes(self) -> list[tuple[int, str]]:
        meta = self.load_meta()["presets"]

        return [
            (p["id"], p["last_saved"])
            for p in meta
            if p["last_saved"] is not None
        ]


    # --- Preset functions ---

    def savePreset(self) -> bool:
        # TODO: Implement preset saving logic
        pass

            now = datetime.now(datetime.timezone.utc).isoformat()
            self.report = RD.reportData

            preset = {
                "saved_at": now,
                "vars": {
                    "departure_runways": self.departure_runways,
                    "landing_runways": self.landing_runways,
                    "mixed_runways": self.mixed_runways,
                },
                "planes": [plane.__dict__ for plane in self.plane_list],
                "report": self.report.__dict__
            }

            with open(self.preset_files[preset_id], 'w') as f:
                json.dump(preset, f, indent=4)

            # Updates meta file, making
            meta = self.load_meta()
            for p in meta["presets"]:
                if p["id"] == preset_id:
                    p["last_saved"] = now
            self.save_meta(meta)

            return True
        except IOError:
            return False

    def loadPreset(self, preset_id: int) -> bool:
        with open(self.presets_file, 'r') as f:
            return json.load(f)
