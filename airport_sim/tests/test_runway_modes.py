

import pytest
import sys
sys.path.insert(0, '..')

from logic.models import Runway


class TestRunwayInitialization:
    """Test runway objects are created correctly"""
    
    def test_runway_created_with_all_attributes(self):
        """Test runway is initialised with all required attributes"""
        runway = Runway(
            is_departure=False,
            mixed_mode=False,
            runway_number=1,
            is_available=True,
            is_operational=True
        )
        
        assert runway.is_departure == False
        assert runway.mixed_mode == False
        assert runway.runway_number == 1
        assert runway.is_available == True
        assert runway.is_operational == True


class TestLandingOnlyRunway:
    
    
    def test_landing_runway_is_not_departure(self):
        """Test landing runway has is_departure=False"""
        runway = Runway(False, False, 1, True, True)
        assert runway.is_departure == False
        assert runway.mixed_mode == False


class TestDepartureOnlyRunway:
    
    
    def test_departure_runway_has_correct_flags(self):
        """Test departure runway has is_departure=True"""
        runway = Runway(True, False, 2, True, True)
        assert runway.is_departure == True
        assert runway.mixed_mode == False


class TestMixedModeRunway:
    
    
    def test_mixed_runway_has_mixed_flag(self):
        """Test mixed runway has mixed_mode=True"""
        runway = Runway(True, True, 3, True, True)
        assert runway.mixed_mode == True


class TestRunwayAvailability:
    
    
    def test_runway_starts_available(self):
        """Test runway is initially available"""
        runway = Runway(False, False, 1, is_available=True, is_operational=True)
        assert runway.is_available == True
    
    def test_runway_availability_changeable(self):
        """Test runway availability can be changed"""
        runway = Runway(False, False, 1, True, True)
        runway.is_available = False
        assert runway.is_available == False


class TestRunwayOperationalStatus:
    
    
    def test_runway_starts_operational(self):
        """Test runway is initially operational"""
        runway = Runway(False, False, 1, True, is_operational=True)
        assert runway.is_operational == True
    
    def test_runway_can_be_disabled(self):
        """Test runway operational status can be toggled"""
        runway = Runway(False, False, 1, True, True)
        runway.is_operational = False
        assert runway.is_operational == False


# Mark all tests as runway mode tests
pytestmark = [pytest.mark.unit, pytest.mark.runway]