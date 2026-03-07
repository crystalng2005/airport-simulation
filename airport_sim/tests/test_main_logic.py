

import pytest
import sys
sys.path.insert(0, '..')

from logic.simulation import SimulationController
import logic.globals.reportData as RD


class TestSimulationInitialization:
    """Test SimulationController initialisation"""
    
    def test_simulation_created(self):
        """Test simulation controller can be created"""
        sim = SimulationController(10, 10, 3, 1, 1, 1, 30, 60)
        assert sim.departures_per_hour == 10
        assert sim.landings_per_hour == 10


class TestRunwayGeneration:
    """Test runway generation"""
    
    def test_runways_generated_correctly(self):
        """Test correct number of runways created"""
        sim = SimulationController(10, 10, 5, 2, 2, 1, 30, 60)
        assert len(sim.all_runways) == 5
    
    def test_departure_runways_generated(self):
        """Test departure runways created"""
        sim = SimulationController(10, 10, 3, 2, 1, 0, 30, 60)
        departure_count = sum(1 for r in sim.all_runways if r.is_departure and not r.mixed_mode)
        assert departure_count == 2


class TestQueueGeneration:
    """Test queue generation"""
    
    def test_queues_generated(self):
        """Test both queues are created"""
        sim = SimulationController(10, 10, 3, 1, 1, 1, 30, 60)
        assert sim.departure_queue is not None
        assert sim.landing_queue is not None


class TestPlaneGeneration:
    """Test plane generation"""
    
    def test_generate_departure_plane(self):
        """Test departure plane can be generated"""
        sim = SimulationController(10, 10, 3, 1, 1, 1, 30, 60)
        sim.generatePlane(is_departure=True)
        assert RD.reportData.total_planes == 1


# Mark all tests
pytestmark = [pytest.mark.unit, pytest.mark.simulation]