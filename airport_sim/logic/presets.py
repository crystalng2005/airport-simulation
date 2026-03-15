from logic.plane import Plane, EmergencyStatus
import json
import os
import tempfile
from datetime import datetime, timezone
from logic.report import PerformanceReport
import logic.globals.reportData as RD

class PresetController:
    def __init__(self) -> None:
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
    def _init_meta(self) -> None:
        """
        Ensures the preset metadata file exists.
        If the metadata file does not exist, it creates one containing
        three preset slots, each with an ID and a timestamp indicating
        when the preset was last saved.
        """
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

    def _load_meta(self) -> dict:
        """
        Loads the preset metadata file.
        Returns:
            A dictionary containing metadata for all preset slots.
            If the file cannot be read or parsed, an empty metadata
            structure is returned.
        """
        try:
            with open(self.meta_file, 'r') as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError):
            return {"presets": []}

    def _save_meta(self, meta: dict) -> None:
        """
        Saves metadata about presets to the metadata file.
        Args:
            meta: A dictionary containing preset metadata including
                preset IDs and last saved timestamps.
        """
        with open(self.meta_file, 'w') as f:
            json.dump(meta, f, indent=4)

    def get_preset_save_times(self) -> list[tuple[int, str]]:
        """
        Retrieves the save timestamps of all presets.
        Returns:
            A list of tuples containing:
                (preset_id, last_saved_timestamp)

            Only presets that have been saved at least once are included.
        """
        meta = self._load_meta().get("presets", [])

        return [
            (p["id"], p["last_saved"])
            for p in meta
            if p.get("last_saved") is not None
        ]

    # --- Preset functions ---

    def save_preset(self) -> bool:
        """
        Saves the current simulation state as a preset.
        Presets are stored in one of three preset slots. If all slots are
        occupied, the oldest preset is overwritten.

        Returns:
            True if the preset was saved successfully, otherwise False.
        """
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
        """
        Loads a preset from a file.

        Args:
            preset_id: The ID of the preset slot to load.

        Returns:
            True if the preset was loaded successfully, otherwise False.
        """
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


    def reset(self) -> bool:
        """
        Resets the controller state in preparation for a new simulation.
        All parameters are cleared, and the
        report reference is removed.

        Returns:
            True once the reset operation completes.
        """
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
    def _serialize_plane(plane: Plane) -> dict:
        """
        Converts a Plane object into a JSON-serialisable dictionary.

        Args:
            plane: The Plane object to serialise.

        Returns:
            A dictionary representation of the plane suitable for JSON storage.
        """
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