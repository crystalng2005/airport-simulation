

import pytest
import sys
sys.path.insert(0, '..')

from logic.presets import PresetController


class TestPresetControllerInitialisation:
    """Test PresetController creation"""
    
    def test_preset_controller_created_empty(self):
        """Test preset controller created without planes"""
        controller = PresetController()
        assert controller.plane_list is not None
        assert len(controller.plane_list) == 0
    
    def test_presets_file_path_configured(self):
        """Test presets file path configured"""
        controller = PresetController()
        assert controller.presets_file is not None
        assert 'presets.json' in controller.presets_file


class TestPresetMethods:
    """Test preset methods exist"""
    
    def test_save_preset_method_exists(self):
        """Test savePreset method exists"""
        controller = PresetController()
        assert hasattr(controller, 'savePreset')
    
    def test_load_preset_method_exists(self):
        """Test loadPreset method exists"""
        controller = PresetController()
        assert hasattr(controller, 'loadPreset')


# Mark all tests
pytestmark = [pytest.mark.unit, pytest.mark.presets]