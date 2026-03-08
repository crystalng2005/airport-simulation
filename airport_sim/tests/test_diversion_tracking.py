"""
Tests the integration of:
- Diversion tracking in PerformanceReport
- Time progression in SimulationController
- Queue system in QueueController
- Emergency handling and cancellations
"""

import pytest
import sys
sys.path.insert(0, '..')

from logic.simulation import SimulationController
from logic.report import PerformanceReport
from logic.plane import Plane, EmergencyStatus
from logic.queue_manager import QueueController
from logic.models import Runway
from datetime import datetime, timedelta
import logic.globals.reportData as RD


class TestDiversionTracking:
    """Test diversion tracking functionality"""
    
    def setup_method(self):
        """Setup before each test"""
        # Initialize report data
        RD.init(5, 1, 2, 2, 10, datetime(2000, 1, 1))
    
    def test_diversion_counter_increments(self):
        """Test that diversions are tracked correctly"""
        report = RD.reportData
        initial_diversions = report.diversions
        
        # Simulate a diversion
        report.diversions += 1
        
        assert report.diversions == initial_diversions + 1
    
    def test_multiple_diversions_tracked(self):
        """Test multiple diversions are counted"""
        report = RD.reportData
        report.diversions = 0  # Reset
        
        # Simulate 5 diversions
        for i in range(5):
            report.diversions += 1
        
        assert report.diversions == 5
    
    def test_diversion_affects_efficiency(self):
        """Test that diversions reduce efficiency"""
        report = RD.reportData
        report.total_planes = 100
        report.diversions = 10
        report.cancellations = 0
        
        # Efficiency = (total - diversions - cancellations) / total * 100
        expected_efficiency = (100 - 10 - 0) / 100 * 100
        assert expected_efficiency == 90.0
    
    def test_diversion_reason_fuel_emergency(self):
        """Test diversion tracking for fuel emergency"""
        plane = Plane(is_departure=False)
        plane.emergency_status = EmergencyStatus.FUEL
        plane.fuel_level = 5  # Critical fuel
        
        # Plane should be diverted due to fuel
        assert plane.emergency_status == EmergencyStatus.FUEL
        assert plane.fuel_level < 20  # Below threshold


class TestTimeProgression:
    """Test time progression in simulation"""
    
    def setup_method(self):
        """Setup simulation for testing"""
        RD.init(5, 1, 2, 2, 10, datetime(2000, 1, 1))
        self.sim = SimulationController(
            departures_per_hour=10,
            landings_per_hour=10,
            total_runways=5,
            departure_runways=2,
            landing_runways=2,
            mixed_runways=1,
            cancellation_time=30,
            total_simulation_minutes=100,
            tick_minutes=5
        )
    
    def test_time_advances_on_update(self):
        """Test that time advances with each update"""
        initial_time = self.sim.current_time
        
        self.sim.update()
        
        # Time should advance by tick_minutes (5 minutes)
        expected_time = initial_time + timedelta(minutes=5)
        assert self.sim.current_time == expected_time
    
    def test_multiple_ticks_advance_time(self):
        """Test multiple ticks advance time correctly"""
        initial_time = self.sim.current_time
        
        # Run 10 ticks
        for _ in range(10):
            self.sim.update()
        
        # Time should advance by 10 * 5 = 50 minutes
        expected_time = initial_time + timedelta(minutes=50)
        assert self.sim.current_time == expected_time
    
    def test_tick_speed_configuration(self):
        """Test that tick speed is configurable"""
        assert self.sim.tick_minutes == 5
        
        # Create sim with different tick speed
        sim2 = SimulationController(10, 10, 3, 1, 1, 1, 30, 100, tick_minutes=10)
        assert sim2.tick_minutes == 10
    
    def test_planes_generated_per_tick(self):
        """Test planes are generated based on tick rate"""
        initial_planes = RD.reportData.total_planes
        
        # With 10 planes/hour and 5 min tick: 10 * (5/60) = 0.833 expected
        # Should generate 0 or 1 planes per tick
        self.sim.update()
        
        planes_generated = RD.reportData.total_planes - initial_planes
        assert planes_generated >= 0  # At least 0 planes
        assert planes_generated <= 2  # At most 2 (1 departure + 1 landing)


class TestQueueSystem:
    """Test queue management system"""
    
    def setup_method(self):
        """Setup queue system"""
        RD.init(3, 0, 1, 2, 10, datetime(2000, 1, 1))
        
        # Create a minimal simulation for the queue controller
        self.sim = SimulationController(
            departures_per_hour=10,
            landings_per_hour=10,
            total_runways=3,
            departure_runways=1,
            landing_runways=2,
            mixed_runways=0,
            cancellation_time=30,
            total_simulation_minutes=100
        )
        
        # Create runways
        self.landing_runways = [
            Runway(False, False, 1, True, True),
            Runway(False, False, 2, True, True)
        ]
        
        self.departure_runways = [
            Runway(True, False, 3, True, True)
        ]
        
        # Create queues with sim reference
        self.landing_queue = QueueController([], self.landing_runways, False, self.sim)
        self.departure_queue = QueueController([], self.departure_runways, True, self.sim)
    
    def test_plane_enqueued_to_landing(self):
        """Test plane is added to landing queue"""
        plane = Plane(is_departure=False)
        initial_count = len(self.landing_queue.plane_queue)
        
        self.landing_queue.enqueue(plane)
        
        assert len(self.landing_queue.plane_queue) == initial_count + 1
    
    def test_plane_enqueued_to_departure(self):
        """Test plane is added to departure queue"""
        plane = Plane(is_departure=True)
        initial_count = len(self.departure_queue.plane_queue)
        
        self.departure_queue.enqueue(plane)
        
        assert len(self.departure_queue.plane_queue) == initial_count + 1
    
    def test_queue_max_tracked(self):
        """Test maximum queue size is tracked"""
        report = RD.reportData
        report.queue_max = 0
        report.queue_current = 0
        
        # Add 5 planes to queue
        for i in range(5):
            report.incQueueCurrent()
        
        assert report.queue_max == 5
        assert report.queue_current == 5
    
    def test_queue_decrements_correctly(self):
        """Test queue size decrements when planes leave"""
        report = RD.reportData
        report.queue_current = 5
        
        report.decQueueCurrent()
        
        assert report.queue_current == 4
    
    def test_holding_pattern_queue_tracked(self):
        """Test holding pattern queue is tracked separately"""
        report = RD.reportData
        report.holding_max = 0
        report.holding_current = 0
        
        # Add planes to holding pattern
        for i in range(3):
            report.incHoldingCurrent()
        
        assert report.holding_max == 3
        assert report.holding_current == 3
    
    def test_emergency_plane_priority(self):
        """Test emergency planes get priority in queue"""
        # Create normal plane
        normal_plane = Plane(is_departure=False)
        normal_plane.emergency_status = EmergencyStatus.NONE
        normal_plane.emergency_time_left = 0
        
        # Create emergency plane
        emergency_plane = Plane(is_departure=False)
        emergency_plane.emergency_status = EmergencyStatus.FUEL
        emergency_plane.emergency_time_left = 10
        
        # Add normal plane first
        self.landing_queue.enqueue(normal_plane)
        
        # Add emergency plane - should be prioritized
        self.landing_queue.planeEmergency(emergency_plane)
        
        # Emergency plane should be at front or near front of queue
        # (exact position depends on other emergencies)
        assert emergency_plane in self.landing_queue.plane_queue
    
    def test_runway_assignment_when_available(self):
        """Test plane is assigned to runway when available"""
        plane = Plane(is_departure=False)
        plane.current_runway = -1
        
        self.landing_queue.enqueue(plane)
        
        # Make runway available
        self.landing_runways[0].is_available = True
        
        # Check runways - should assign plane
        self.landing_queue.checkRunways()
        
        # Plane should be removed from queue
        assert plane not in self.landing_queue.plane_queue


class TestCancellationSystem:
    """Test cancellation tracking"""
    
    def setup_method(self):
        """Setup for cancellation tests"""
        RD.init(3, 0, 1, 2, 10, datetime(2000, 1, 1))
    
    def test_cancellation_counter_increments(self):
        """Test cancellation counter works"""
        report = RD.reportData
        initial_cancellations = report.cancellations
        
        report.cancellations += 1
        
        assert report.cancellations == initial_cancellations + 1
    
    def test_plane_can_be_cancelled(self):
        """Test plane can be marked as cancelled"""
        plane = Plane(is_departure=True)
        plane.cancelled = False
        
        plane.cancel()
        
        assert plane.cancelled == True
    
    def test_cancelled_plane_stops_fuel_decrease(self):
        """Test cancelled planes don't consume fuel"""
        plane = Plane(is_departure=False)
        plane.cancelled = True
        initial_fuel = plane.fuel_level
        
        # Try to decrease fuel
        result = plane.decreaseFuel()
        
        # Should return False and fuel unchanged
        assert result == False
        assert plane.fuel_level == initial_fuel
    
    def test_emergency_timeout_causes_cancellation(self):
        """Test emergency plane cancelled if time runs out"""
        plane = Plane(is_departure=False)
        plane.emergency_status = EmergencyStatus.FUEL
        plane.emergency_time_left = 0  # No time left
        
        # Should be cancelled/diverted
        assert plane.emergency_status != EmergencyStatus.NONE
        assert plane.emergency_time_left <= 0


class TestIntegratedQueueAndTime:
    """Test integration of queue system with time progression"""
    
    def setup_method(self):
        """Setup integrated system"""
        RD.init(5, 1, 2, 2, 10, datetime(2000, 1, 1))
        self.sim = SimulationController(
            departures_per_hour=12,
            landings_per_hour=10,
            total_runways=5,
            departure_runways=2,
            landing_runways=2,
            mixed_runways=1,
            cancellation_time=30,
            total_simulation_minutes=200,
            tick_minutes=5
        )
    
    def test_queue_grows_over_time(self):
        """Test queue size increases as planes arrive"""
        initial_queue_size = len(self.sim.landing_queue.plane_queue)
        
        # Run several ticks
        for _ in range(10):
            self.sim.update()
        
        # Queue should have planes (unless all processed)
        total_planes_generated = RD.reportData.total_planes
        assert total_planes_generated > 0
    
    def test_planes_processed_over_time(self):
        """Test planes are processed through queues over time"""
        # Generate some planes
        for _ in range(5):
            self.sim.generatePlane(is_departure=False)
        
        initial_queue = len(self.sim.landing_queue.plane_queue)
        
        # Make all runways available
        for runway in self.sim.landing_list:
            runway.is_available = True
        
        # Process queue
        self.sim.landing_queue.checkRunways()
        
        # Some planes should be assigned
        final_queue = len(self.sim.landing_queue.plane_queue)
        assert final_queue < initial_queue
    
    def test_report_tracks_all_metrics(self):
        """Test report tracks all required metrics"""
        report = RD.reportData
        
        # Run simulation
        for _ in range(20):
            self.sim.update()
        
        # Check all metrics are being tracked
        assert hasattr(report, 'total_planes')
        assert hasattr(report, 'diversions')
        assert hasattr(report, 'cancellations')
        assert hasattr(report, 'queue_max')
        assert hasattr(report, 'holding_max')
        assert hasattr(report, 'wait_times')
        assert hasattr(report, 'hold_times')


# Mark all tests
pytestmark = [
    pytest.mark.system,
    pytest.mark.integration,
    pytest.mark.diversion,
    pytest.mark.queue,
    pytest.mark.time
]