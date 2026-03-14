from logic.plane import Plane, EmergencyStatus
import json
import os
import tempfile
from datetime import datetime, timezone
from logic.report import PerformanceReport
import logic.globals.reportData as RD

class PresetController:

    def __init__(self):
        self.plane_list = []

        self.departure_runways = 0
        self.landing_runways = 0
        self.mixed_runways = 0
        self.runway_closure_prob = []
        self.plane_emergency_prob = []
        self.runway_opening_prob = 1

        self.report = None  # Initialised before saving, goto line 75

        self.data_dir = os.path.join(
            os.path.dirname(__file__), '..', 'data'
        )

        self.meta_file = os.path.join(self.data_dir, 'presets_meta.json')
        self.preset_files = [
            os.path.join(self.data_dir, f'preset{i}.json') for i in range(3)
        ]

        self._init_meta()

    # --- Meta file functions ---  (Meta file keeps track of preset ID's and when they were saved)
    def _init_meta(self):
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

    def _load_meta(self):
        try:
            with open(self.meta_file, 'r') as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError):
            return {"presets": []}

    def _save_meta(self, meta):
        with open(self.meta_file, 'w') as f:
            json.dump(meta, f, indent=4)

    def get_preset_save_times(self) -> list[tuple[int, str]]:
        meta = self._load_meta().get("presets", [])

        return [
            (p["id"], p["last_saved"])
            for p in meta
            if p.get("last_saved") is not None
        ]

    # --- Preset functions ---

    def save_preset(self):
        try:
            print('savePreset called')
            
            meta_data = self._load_meta()
            presets = meta_data.get("presets", [])

            unused = [p for p in presets if p.get("last_saved") is None]
            if unused:
                preset_id = unused[0]["id"]
            else:
                presets_with_time = [p for p in presets if p.get("last_saved") is not None]
                presets_with_time.sort(key=lambda p: p["last_saved"])
                preset_id = presets_with_time[0]["id"]

            now = datetime.now(timezone.utc).isoformat()

            if RD.reportData is None:
                return False

            self.report = RD.reportData
            
            report_dict = self.report.__dict__.copy()
            
            # Convert any datetime objects to ISO strings for JSON serialization
            for key, val in report_dict.items():
                if hasattr(val, 'isoformat'):
                    report_dict[key] = val.isoformat()
                elif hasattr(val, 'total_seconds'):
                    report_dict[key] = val.total_seconds()
                elif isinstance(val, list):
                    report_dict[key] = [
                        v.total_seconds() if hasattr(v, 'total_seconds') else v
                        for v in val
                    ]

            preset = {
                "saved_at": now,
                "vars": {
                    "departure_runways": self.departure_runways,
                    "landing_runways": self.landing_runways,
                    "mixed_runways": self.mixed_runways,
                    "plane_emergency_prob" : self.plane_emergency_prob,
                    "runway_closure_prob" : self.runway_closure_prob,
                    "runway_opening_prob" : self.runway_opening_prob,
                },
                "planes": [self._serialize_plane(plane) for plane in self.plane_list],
                "report": report_dict
            }

            # Atomic write: write to temp file first, then rename
            dest = self.preset_files[preset_id]
            fd, tmp_path = tempfile.mkstemp(dir=self.data_dir, suffix='.tmp')
            try:
                with os.fdopen(fd, 'w') as f:
                    json.dump(preset, f, indent=4)
                os.replace(tmp_path, dest)
            except:
                os.unlink(tmp_path)
                raise

            for p in meta_data["presets"]:
                if p["id"] == preset_id:
                    p["last_saved"] = now

            self._save_meta(meta_data)
            print('Preset saved successfully!')
            return True

        except (IOError, IndexError, KeyError, TypeError) as e:
            print(f'Error in savePreset: {e}')
            import traceback
            traceback.print_exc()
            return False

    def load_preset(self, preset_id: int) -> bool:
        if not (0 <= preset_id < len(self.preset_files)):
            return False

        try:
            with open(self.preset_files[preset_id], 'r') as f:
                data = json.load(f)

            vars_data = data["vars"]
            self.departure_runways = vars_data["departure_runways"]
            self.landing_runways = vars_data["landing_runways"]
            self.mixed_runways = vars_data["mixed_runways"]
            self.plane_emergency_prob = vars_data["plane_emergency_prob"]
            self.runway_closure_prob = vars_data["runway_closure_prob"]
            self.runway_opening_prob = vars_data["runway_opening_prob"]

            # Loads planes by initiating new objects and importing their data from the preset
            self.plane_list = []
            for plane_data in data["planes"]:
                plane = Plane.__new__(Plane)
                plane.__dict__.update(plane_data)
                # Restore enum from int
                if isinstance(plane.emergency_status, int):
                    plane.emergency_status = EmergencyStatus(plane.emergency_status)
                self.plane_list.append(plane)

            report = PerformanceReport.__new__(PerformanceReport)
            report.__dict__.update(data["report"])
            self.report = report
            RD.reportData = report

            return True
        except (IOError, KeyError, IndexError, TypeError):
            return False
    # Resets file to save new preset info
    # To be called when new simulation runs
    def reset(self) -> bool:
        self.departure_runways = 0
        self.landing_runways = 0
        self.mixed_runways = 0
        self.plane_emergency_prob = []
        self.runway_closure_prob = []
        self.runway_opening_prob = 1
        self.plane_list.clear()
        self.report = None
        return True

    @staticmethod
    def _serialize_plane(plane):
        """Convert a Plane object to a JSON-serializable dict."""
        skip = {'queue_controller'}
        d = {}
        for k, v in plane.__dict__.items():
            if k in skip:
                continue
            if hasattr(v, 'isoformat'):       # datetime / datetime.time
                d[k] = v.isoformat()
            elif hasattr(v, 'value'):          # Enum
                d[k] = v.value
            else:
                d[k] = v
        return d