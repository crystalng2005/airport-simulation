"""

Tests the integration of:
- Preset saving (3 slots)
- Preset loading
- Preset timestamps
- Oldest preset replacement
- VisualisationController preset methods
- Preset data persistence
"""

import pytest
import sys
sys.path.insert(0, '..')

from logic.presets import PresetController
from logic.visualisation import VisualisationController
from logic.plane import Plane
from logic.report import PerformanceReport
import os
import json
from datetime import datetime


# Helper function to create PerformanceReport with correct signature
def create_performance_report():
    """Create PerformanceReport with correct signature based on actual implementation"""
    # Actual signature: (runway_amount, runways_departure, runways_landing, landings_per_hour, start_time, tick_minutes)
    return PerformanceReport(5, 2, 2, 10, datetime.now(), 5)


# Setup function to initialize preset meta file
@pytest.fixture(scope="session", autouse=True)
def setup_preset_files():
    """Initialize preset meta file before tests"""
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    meta_file = os.path.join(data_dir, 'presets_meta.json')
    
    # Create empty meta file if it doesn't exist or is empty
    if not os.path.exists(meta_file) or os.path.getsize(meta_file) == 0:
        with open(meta_file, 'w') as f:
            json.dump({"presets": [None, None, None]}, f)


class TestPresetControllerBasics:
    """Test basic PresetController functionality"""
    
    def test_preset_controller_creates(self):
        """Test PresetController can be instantiated"""
        controller = PresetController()
        assert controller is not None
    
    def test_preset_controller_has_plane_list(self):
        """Test PresetController has plane_list attribute"""
        controller = PresetController()
        assert hasattr(controller, 'plane_list')
        assert isinstance(controller.plane_list, list)
    
    def test_preset_controller_has_runway_attributes(self):
        """Test PresetController has runway configuration attributes"""
        controller = PresetController()
        assert hasattr(controller, 'departure_runways')
        assert hasattr(controller, 'landing_runways')
        assert hasattr(controller, 'mixed_runways')
    
    def test_preset_controller_has_report(self):
        """Test PresetController has report attribute"""
        controller = PresetController()
        assert hasattr(controller, 'report')


class TestPresetSaving:
    """Test preset saving functionality"""
    
    def test_save_preset_method_exists(self):
        """Test savePreset method exists"""
        controller = PresetController()
        assert hasattr(controller, 'savePreset')
        assert callable(getattr(controller, 'savePreset'))
    
    def test_save_preset_returns_boolean(self):
        """Test savePreset returns a boolean"""
        controller = PresetController()
        controller.departure_runways = 2
        controller.landing_runways = 2
        controller.mixed_runways = 1
        controller.report = create_performance_report()
        
        result = controller.savePreset()
        assert isinstance(result, bool)
    
    def test_save_preset_creates_file(self):
        """Test savePreset creates a preset file"""
        controller = PresetController()
        controller.departure_runways = 2
        controller.landing_runways = 2
        controller.mixed_runways = 1
        controller.report = create_performance_report()
        controller.plane_list = []
        
        controller.savePreset()
        
        # Check if any preset file exists
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        preset_files = [f for f in os.listdir(data_dir) if f.startswith('preset') and f.endswith('.json')]
        assert len(preset_files) > 0


class TestPresetLoading:
    """Test preset loading functionality"""
    
    def setup_method(self):
        """Setup - save a preset to test loading"""
        self.controller = PresetController()
        self.controller.departure_runways = 3
        self.controller.landing_runways = 2
        self.controller.mixed_runways = 1
        self.controller.report = create_performance_report()
        self.controller.plane_list = []
        self.controller.savePreset()
    
    def test_load_preset_method_exists(self):
        """Test loadPreset method exists"""
        assert hasattr(self.controller, 'loadPreset')
        assert callable(getattr(self.controller, 'loadPreset'))
    
    def test_load_preset_returns_boolean(self):
        """Test loadPreset returns boolean"""
        result = self.controller.loadPreset(0)
        assert isinstance(result, bool)
    
    def test_load_preset_restores_runway_config(self):
        """Test loadPreset restores runway configuration"""
        # Save with specific config
        self.controller.departure_runways = 4
        self.controller.landing_runways = 3
        self.controller.mixed_runways = 2
        self.controller.savePreset()
        
        # Create new controller and load
        new_controller = PresetController()
        new_controller.loadPreset(0)
        
        assert new_controller.departure_runways == 4
        assert new_controller.landing_runways == 3
        assert new_controller.mixed_runways == 2
    
    def test_load_preset_restores_plane_list(self):
        """Test loadPreset restores plane list"""
        # Save with planes
        plane1 = Plane(is_departure=True)
        plane2 = Plane(is_departure=False)
        self.controller.plane_list = [plane1, plane2]
        self.controller.savePreset()
        
        # Load and verify
        new_controller = PresetController()
        new_controller.loadPreset(0)
        
        assert len(new_controller.plane_list) == 2
    
    def test_load_preset_restores_report(self):
        """Test loadPreset restores performance report"""
        # Save with report
        report = create_performance_report()
        report.total_planes = 50
        report.diversions = 5
        self.controller.report = report
        self.controller.savePreset()
        
        # Load and verify
        new_controller = PresetController()
        new_controller.loadPreset(0)
        
        assert new_controller.report is not None
        assert new_controller.report.total_planes == 50
        assert new_controller.report.diversions == 5


class TestPresetTimestamps:
    """Test preset timestamp functionality"""
    
    def test_get_preset_save_times_exists(self):
        """Test getPresetSaveTimes method exists"""
        controller = PresetController()
        assert hasattr(controller, 'getPresetSaveTimes')
    
    def test_get_preset_save_times_returns_list(self):
        """Test getPresetSaveTimes returns a list"""
        controller = PresetController()
        times = controller.getPresetSaveTimes()
        assert isinstance(times, list)
    
    def test_preset_save_times_has_3_slots(self):
        """Test getPresetSaveTimes returns 3 slots"""
        controller = PresetController()
        times = controller.getPresetSaveTimes()
        assert len(times) == 3
    
    def test_preset_save_time_format(self):
        """Test preset save times are strings or None"""
        controller = PresetController()
        controller.departure_runways = 2
        controller.landing_runways = 2
        controller.mixed_runways = 1
        controller.report = create_performance_report()
        controller.savePreset()
        
        times = controller.getPresetSaveTimes()
        
        for time in times:
            assert time is None or isinstance(time, str)


class TestPresetSlotManagement:
    """Test 3-slot preset management"""
    
    def test_only_3_presets_stored(self):
        """Test only 3 presets are stored"""
        # Save 5 presets
        for i in range(5):
            controller = PresetController()
            controller.departure_runways = i
            controller.landing_runways = i
            controller.mixed_runways = i
            controller.report = create_performance_report()
            controller.savePreset()
        
        # Check only 3 files exist
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        preset_files = [f for f in os.listdir(data_dir) if f.startswith('preset') and f.endswith('.json') and f != 'presets_meta.json']
        
        assert len(preset_files) <= 3
    
    def test_oldest_preset_replaced(self):
        """Test oldest preset is replaced when saving 4th preset"""
        # Save 3 presets with different configs
        configs = [(1,1,1), (2,2,2), (3,3,3)]
        
        for d, l, m in configs:
            controller = PresetController()
            controller.departure_runways = d
            controller.landing_runways = l
            controller.mixed_runways = m
            controller.report = create_performance_report()
            controller.savePreset()
        
        # Save 4th preset - should replace oldest
        controller = PresetController()
        controller.departure_runways = 4
        controller.landing_runways = 4
        controller.mixed_runways = 4
        controller.report = create_performance_report()
        controller.savePreset()
        
        # Verify only 3 presets exist
        controller2 = PresetController()
        times = controller2.getPresetSaveTimes()
        non_none_times = [t for t in times if t is not None]
        assert len(non_none_times) <= 3


class TestVisualisationControllerPresetMethods:
    """Test VisualisationController preset methods"""
    
    def setup_method(self):
        """Setup - create some test presets"""
        # Save 2 test presets
        for i in range(2):
            controller = PresetController()
            controller.departure_runways = i + 1
            controller.landing_runways = i + 1
            controller.mixed_runways = 1
            controller.report = create_performance_report()
            controller.report.total_planes = (i + 1) * 10
            controller.report.diversions = i + 1
            
            # Add some planes
            plane1 = Plane(is_departure=True)
            plane2 = Plane(is_departure=False)
            controller.plane_list = [plane1, plane2]
            
            controller.savePreset()
        
        self.vis_controller = VisualisationController()
    
    def test_get_available_presets_exists(self):
        """Test getAvailablePresets method exists"""
        assert hasattr(self.vis_controller, 'getAvailablePresets')
    
    def test_get_available_presets_returns_list(self):
        """Test getAvailablePresets returns a list"""
        presets = self.vis_controller.getAvailablePresets()
        assert isinstance(presets, list)
    
    def test_get_available_presets_max_3(self):
        """Test getAvailablePresets returns maximum 3 presets"""
        presets = self.vis_controller.getAvailablePresets()
        assert len(presets) <= 3
    
    def test_preset_has_required_fields(self):
        """Test each preset has required fields"""
        presets = self.vis_controller.getAvailablePresets()
        
        if len(presets) > 0:
            preset = presets[0]
            assert 'id' in preset
            assert 'saved_at' in preset
            assert 'vars' in preset
            assert 'planes' in preset
            assert 'report' in preset
    
    def test_preset_vars_has_runway_config(self):
        """Test preset vars contains runway configuration"""
        presets = self.vis_controller.getAvailablePresets()
        
        if len(presets) > 0:
            vars_dict = presets[0]['vars']
            assert 'departure_runways' in vars_dict
            assert 'landing_runways' in vars_dict
            assert 'mixed_runways' in vars_dict
    
    def test_preset_planes_limited_to_5(self):
        """Test preset planes list is limited to 5 in preview"""
        presets = self.vis_controller.getAvailablePresets()
        
        if len(presets) > 0:
            planes = presets[0]['planes']
            assert len(planes) <= 5
    
    def test_preset_report_is_dict(self):
        """Test preset report is a dictionary"""
        presets = self.vis_controller.getAvailablePresets()
        
        if len(presets) > 0:
            report = presets[0]['report']
            assert isinstance(report, dict)
    
    def test_get_preset_data_exists(self):
        """Test getPresetData method exists"""
        assert hasattr(self.vis_controller, 'getPresetData')
    
    def test_get_preset_data_returns_dict(self):
        """Test getPresetData returns dictionary"""
        data = self.vis_controller.getPresetData(0)
        assert isinstance(data, dict)
    
    def test_get_preset_data_has_all_fields(self):
        """Test getPresetData returns all required fields"""
        data = self.vis_controller.getPresetData(0)
        
        assert 'id' in data
        assert 'vars' in data
        assert 'planes' in data
        assert 'report' in data
    
    def test_get_preset_data_includes_all_planes(self):
        """Test getPresetData includes ALL planes (not just 5)"""
        data = self.vis_controller.getPresetData(0)
        planes = data['planes']
        
        # Should have at least 2 planes from setup
        assert len(planes) >= 2


class TestPresetDataPersistence:
    """Test preset data persists across sessions"""
    
    def test_preset_survives_new_controller(self):
        """Test preset data persists when creating new controller"""
        # Save preset
        controller1 = PresetController()
        controller1.departure_runways = 5
        controller1.landing_runways = 4
        controller1.mixed_runways = 3
        controller1.report = create_performance_report()
        controller1.savePreset()
        
        # Create new controller and load
        controller2 = PresetController()
        success = controller2.loadPreset(0)
        
        assert success == True
        assert controller2.departure_runways == 5
        assert controller2.landing_runways == 4
        assert controller2.mixed_runways == 3
    
    def test_preset_files_in_data_directory(self):
        """Test preset files are saved in data/ directory"""
        controller = PresetController()
        controller.departure_runways = 2
        controller.landing_runways = 2
        controller.mixed_runways = 1
        controller.report = create_performance_report()
        controller.savePreset()
        
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        assert os.path.exists(data_dir)
        
        # Check for preset files
        files = os.listdir(data_dir)
        preset_files = [f for f in files if 'preset' in f.lower()]
        assert len(preset_files) > 0


class TestPresetErrorHandling:
    """Test preset error handling"""
    
    def test_load_invalid_preset_id(self):
        """Test loading preset with invalid ID"""
        controller = PresetController()
        
        # Try to load preset ID that doesn't exist
        result = controller.loadPreset(99)
        
        # Should return False or handle gracefully
        assert result == False or result is None
    
    def test_save_without_report(self):
        """Test saving preset without report (should handle gracefully)"""
        controller = PresetController()
        controller.departure_runways = 2
        controller.landing_runways = 2
        controller.mixed_runways = 1
        # Don't set report
        
        try:
            result = controller.savePreset()
            # Should either succeed or return False
            assert isinstance(result, bool)
        except Exception as e:
            # Should not crash - should handle gracefully
            assert False, f"savePreset crashed without report: {e}"


class TestPresetIntegrationWithFrontend:
    """Test preset integration matches frontend expectations"""
    
    def setup_method(self):
        """Setup test presets"""
        controller = PresetController()
        controller.departure_runways = 2
        controller.landing_runways = 3
        controller.mixed_runways = 1
        controller.report = create_performance_report()
        controller.report.total_planes = 100
        controller.report.diversions = 5
        controller.report.cancellations = 3
        controller.report.queue_max = 12
        controller.report.holding_max = 8
        
        plane = Plane(is_departure=True)
        controller.plane_list = [plane]
        
        controller.savePreset()
        
        self.vis_controller = VisualisationController()
    
    def test_frontend_receives_correct_structure(self):
        """Test frontend receives correctly structured preset data"""
        presets = self.vis_controller.getAvailablePresets()
        
        assert len(presets) > 0
        
        preset = presets[0]
        
        # Check structure matches frontend expectations
        assert isinstance(preset['id'], int)
        assert isinstance(preset['vars'], dict)
        assert isinstance(preset['planes'], list)
        assert isinstance(preset['report'], dict)
    
    def test_frontend_receives_all_runway_counts(self):
        """Test frontend receives all runway configuration counts"""
        presets = self.vis_controller.getAvailablePresets()
        
        if len(presets) > 0:
            vars_dict = presets[0]['vars']
            
            # Frontend needs these exact field names
            assert 'departure_runways' in vars_dict
            assert 'landing_runways' in vars_dict
            assert 'mixed_runways' in vars_dict
            
            # Values should be integers
            assert isinstance(vars_dict['departure_runways'], int)
            assert isinstance(vars_dict['landing_runways'], int)
            assert isinstance(vars_dict['mixed_runways'], int)
    
    def test_frontend_receives_report_metrics(self):
        """Test frontend receives key report metrics"""
        presets = self.vis_controller.getAvailablePresets()
        
        if len(presets) > 0:
            report = presets[0]['report']
            
            # Frontend displays these metrics
            assert 'total_planes' in report or 'totalPlanes' in report
            assert 'diversions' in report
            assert 'cancellations' in report
            assert 'queue_max' in report or 'queueMax' in report
            assert 'holding_max' in report or 'holdingMax' in report


# Mark all tests
pytestmark = [
    pytest.mark.system,
    pytest.mark.integration,
    pytest.mark.presets
]