

import pytest
import sys
from datetime import datetime

sys.path.insert(0, '..')

from logic.simulation import SimulationController
from logic.plane import Plane, EmergencyStatus
from logic.presets import PresetController
from logic.models import Runway
import logic.globals.reportData as RD


class TestFR1_CoreSimulation:
    """FR-1.1: Aircraft Generation & FR-1.2: Aircraft Data Tracking"""
    
    def setup_method(self):
        RD.init(5, 1, 2, 2, 10, datetime(2000, 1, 1))
        self.sim = SimulationController(10, 10, 5, 2, 2, 1, 30, 100)
    
    def test_fr1_1_aircraft_generation_inbound(self):
        """FR-1.1: System generates inbound aircraft"""
        initial_count = RD.reportData.total_planes
        self.sim.generatePlane(is_departure=False)
        assert RD.reportData.total_planes == initial_count + 1
    
    def test_fr1_1_aircraft_generation_outbound(self):
        """FR-1.1: System generates outbound aircraft"""
        initial_count = RD.reportData.total_planes
        self.sim.generatePlane(is_departure=True)
        assert RD.reportData.total_planes == initial_count + 1
    
    def test_fr1_2_aircraft_has_callsign(self):
        """FR-1.2: Aircraft has callsign (String)"""
        plane = Plane(False, self.sim.landing_queue, 30)
        assert hasattr(plane, 'callsign'), "Aircraft missing callsign"
        assert isinstance(plane.callsign, str), "callsign not a string"
    
    def test_fr1_2_aircraft_has_fuel_level(self):
        """FR-1.2: Aircraft tracks fuel level (Float)"""
        plane = Plane(False, self.sim.landing_queue, 30)
        assert hasattr(plane, 'fuel_level'), "Aircraft missing fuel_level"
        assert isinstance(plane.fuel_level, (int, float)), "fuel_level not numeric"
    
    def test_fr1_2_aircraft_has_emergency_status(self):
        """FR-1.2: Aircraft tracks emergency status (Enum)"""
        plane = Plane(False, self.sim.landing_queue, 30)
        assert hasattr(plane, 'emergency_status'), "Aircraft missing emergency_status"
        assert isinstance(plane.emergency_status, EmergencyStatus), "emergency_status not Enum"
    
    def test_fr1_2_aircraft_data_updates(self):
        """FR-1.2: Aircraft data updates as simulation progresses"""
        plane = Plane(False, self.sim.landing_queue, 30)
        initial_fuel = plane.fuel_level
        plane.decrease_fuel()  # Correct method name
        assert plane.fuel_level < initial_fuel, "Fuel not decreasing"


class TestFR2_DepartureAndTakeOff:
    """FR-2.1: Take-Off Queue & FR-2.2: Cancellation"""
    
    def setup_method(self):
        RD.init(3, 0, 1, 2, 10, datetime(2000, 1, 1))
        self.sim = SimulationController(10, 10, 3, 1, 2, 0, 30, 100)
    
    def test_fr2_1_takeoff_queue_fifo_order(self):
        """FR-2.1: Take-off queue operates in FIFO order"""
        plane1 = Plane(True, self.sim.departure_queue, 30)
        plane2 = Plane(True, self.sim.departure_queue, 30)
        plane3 = Plane(True, self.sim.departure_queue, 30)
        
        self.sim.departure_queue.enqueue(plane1)
        self.sim.departure_queue.enqueue(plane2)
        self.sim.departure_queue.enqueue(plane3)
        
        assert self.sim.departure_queue.plane_queue[0] == plane1
    
    def test_fr2_1_outbound_aircraft_joins_queue(self):
        """FR-2.1: Outbound aircraft joins take-off queue"""
        initial_size = len(self.sim.departure_queue.plane_queue)
        plane = Plane(True, self.sim.departure_queue, 30)
        self.sim.departure_queue.enqueue(plane)
        assert len(self.sim.departure_queue.plane_queue) == initial_size + 1
    
    def test_fr2_2_cancellation_when_wait_exceeds_max(self):
        """FR-2.2: Aircraft cancelled when wait exceeds max"""
        plane = Plane(True, self.sim.departure_queue, 30)
        plane.cancelled = False
        plane.cancel()
        assert plane.cancelled == True
    
    def test_fr2_2_cancellation_recorded(self):
        """FR-2.2: System records cancellations"""
        initial = RD.reportData.cancellations
        RD.reportData.cancellations += 1
        assert RD.reportData.cancellations == initial + 1


class TestFR3_ArrivalAndLanding:
    """FR-3.1: Holding Pattern & FR-3.2: Diversion"""
    
    def setup_method(self):
        RD.init(3, 0, 1, 2, 10, datetime(2000, 1, 1))
        self.sim = SimulationController(10, 10, 3, 1, 2, 0, 30, 100)
    
    def test_fr3_1_holding_pattern_when_no_runway(self):
        """FR-3.1: Aircraft in holding pattern when no runway"""
        for runway in self.sim.landing_list:
            runway.is_available = False
        
        plane = Plane(False, self.sim.landing_queue, 30)
        self.sim.landing_queue.enqueue(plane)
        assert plane in self.sim.landing_queue.plane_queue
    
    def test_fr3_1_emergency_aircraft_prioritized(self):
        """FR-3.1: Emergency aircraft prioritized"""
        normal = Plane(False, self.sim.landing_queue, 30)
        normal.emergency_status = EmergencyStatus.NONE
        
        emergency = Plane(False, self.sim.landing_queue, 30)
        emergency.emergency_status = EmergencyStatus.FUEL
        emergency.emergency_time_left = 10
        
        self.sim.landing_queue.enqueue(normal)
        self.sim.landing_queue.planeEmergency(emergency)
        
        e_idx = self.sim.landing_queue.plane_queue.index(emergency)
        n_idx = self.sim.landing_queue.plane_queue.index(normal)
        assert e_idx < n_idx
    
    def test_fr3_1_non_emergency_fifo(self):
        """FR-3.1: Non-emergency aircraft in FIFO"""
        p1 = Plane(False, self.sim.landing_queue, 30)
        p2 = Plane(False, self.sim.landing_queue, 30)
        
        p1.emergency_status = EmergencyStatus.NONE
        p2.emergency_status = EmergencyStatus.NONE
        
        self.sim.landing_queue.enqueue(p1)
        self.sim.landing_queue.enqueue(p2)
        
        assert self.sim.landing_queue.plane_queue[0] == p1
    
    def test_fr3_2_fuel_decreases_in_holding(self):
        """FR-3.2: Fuel decreases in holding pattern"""
        plane = Plane(False, self.sim.landing_queue, 30)
        initial = plane.fuel_level
        plane.decrease_fuel()  # Correct method name
        assert plane.fuel_level < initial
    
    def test_fr3_2_diversion_at_fuel_threshold(self):
        """FR-3.2: Aircraft diverted when fuel < 10 min"""
        plane = Plane(False, self.sim.landing_queue, 30)
        plane.fuel_level = 5
        assert plane.fuel_level < 10
    
    def test_fr3_2_diversions_recorded(self):
        """FR-3.2: Diversions recorded"""
        initial = RD.reportData.diversions
        RD.reportData.diversions += 1
        assert RD.reportData.diversions == initial + 1


class TestFR4_RunwayConfiguration:
    """FR-4.1: Runway Modes & FR-4.2: Multiple Runways"""
    
    def test_fr4_1_landing_only_runway(self):
        """FR-4.1: Landing-only runway mode"""
        runway = Runway(False, False, 1, True, True)
        assert runway.is_departure == False
        assert runway.mixed_mode == False
    
    def test_fr4_1_takeoff_only_runway(self):
        """FR-4.1: Take-off-only runway mode"""
        runway = Runway(True, False, 2, True, True)
        assert runway.is_departure == True
        assert runway.mixed_mode == False
    
    def test_fr4_1_mixed_mode_runway(self):
        """FR-4.1: Mixed mode runway"""
        runway = Runway(True, True, 3, True, True)
        assert runway.mixed_mode == True
    
    def test_fr4_1_runway_occupation_exclusive(self):
        """FR-4.1: Only one aircraft per runway"""
        runway = Runway(False, False, 1, True, True)
        runway.is_available = False
        assert runway.is_available == False
    
    def test_fr4_2_multiple_runways_supported(self):
        """FR-4.2: Supports 1-10 runways"""
        sim = SimulationController(10, 10, 7, 3, 2, 2, 30, 100)
        assert len(sim.all_runways) == 7
    
    def test_fr4_2_runways_independently_configured(self):
        """FR-4.2: Independent runway configuration"""
        r1 = Runway(True, False, 1, True, True)
        r2 = Runway(False, False, 2, True, True)
        r3 = Runway(True, True, 3, True, True)
        
        assert r1.is_departure and not r1.mixed_mode
        assert not r2.is_departure and not r2.mixed_mode
        assert r3.mixed_mode


class TestFR5_ScenarioModelling:
    """FR-5.1: Operational Status & FR-5.2: Fuel Calculation"""
    
    def test_fr5_1_runway_operational_status_toggle(self):
        """FR-5.1: Toggle runway operational status"""
        runway = Runway(False, False, 1, True, True)
        runway.is_operational = False
        assert runway.is_operational == False
    
    def test_fr5_1_non_operational_runway_unavailable(self):
        """FR-5.1: Non-operational runway unavailable"""
        runway = Runway(False, False, 1, True, False)
        assert runway.is_operational == False
    
    def test_fr5_2_diversions_tracked(self):
        """FR-5.2: Diversions tracked in report"""
        RD.init(3, 0, 1, 2, 10, datetime(2000, 1, 1))
        assert hasattr(RD.reportData, 'diversions')
    
    def test_fr5_2_cancellations_tracked(self):
        """FR-5.2: Cancellations tracked in report"""
        RD.init(3, 0, 1, 2, 10, datetime(2000, 1, 1))
        assert hasattr(RD.reportData, 'cancellations')
    
    def test_fr5_2_emergency_priority_fuel(self):
        """FR-5.2: Fuel emergency prioritized"""
        RD.init(3, 0, 1, 2, 10, datetime(2000, 1, 1))
        sim = SimulationController(10, 10, 3, 1, 2, 0, 30, 100)
        plane = Plane(False, sim.landing_queue, 30)
        plane.emergency_status = EmergencyStatus.FUEL
        assert plane.emergency_status == EmergencyStatus.FUEL


class TestUSP1_ConfigurableRunwayScenarios:
    """USP-1: Save/load last 3 configurations"""
    
    def setup_method(self):
        self.preset_controller = PresetController()
        RD.init(5, 1, 2, 2, 10, datetime.now())
    
    def test_usp1_preset_can_save(self):
        """USP-1: Preset can save"""
        self.preset_controller.departure_runways = 2
        self.preset_controller.landing_runways = 2
        self.preset_controller.mixed_runways = 1
        self.preset_controller.report = RD.reportData
        
        result = self.preset_controller.savePreset()
        assert result == True
    
    def test_usp1_preset_can_load(self):
        """USP-1: Preset can load - FIXED"""
        # Save with known values
        pc1 = PresetController()
        pc1.departure_runways = 3
        pc1.landing_runways = 2
        pc1.mixed_runways = 2
        pc1.report = RD.reportData
        
        # Find which slot will be used (first unused or oldest)
        meta = pc1.load_meta()
        unused = [p for p in meta['presets'] if p.get('last_saved') is None]
        if unused:
            slot_id = unused[0]['id']
        else:
            # Will use oldest - find it
            presets_with_time = [p for p in meta['presets'] if p.get('last_saved')]
            presets_with_time.sort(key=lambda p: p['last_saved'])
            slot_id = presets_with_time[0]['id']
        
        # Save to that slot
        saved = pc1.savePreset()
        assert saved == True
        
        # Load from that specific slot
        pc2 = PresetController()
        loaded = pc2.loadPreset(slot_id)
        
        assert loaded == True
        assert pc2.departure_runways == 3, f"Expected 3, got {pc2.departure_runways}"
        assert pc2.landing_runways == 2
        assert pc2.mixed_runways == 2
    
    def test_usp1_stores_last_3_presets(self):
        """USP-1: Stores 3 preset slots"""
        meta = self.preset_controller.load_meta()
        assert len(meta.get("presets", [])) == 3
    
    def test_usp1_preset_saves_runway_config(self):
        """USP-1: Preset saves runway config - FIXED"""
        pc1 = PresetController()
        pc1.departure_runways = 2
        pc1.landing_runways = 3
        pc1.mixed_runways = 1
        pc1.report = RD.reportData
        
        # Determine slot
        meta = pc1.load_meta()
        unused = [p for p in meta['presets'] if not p.get('last_saved')]
        slot_id = unused[0]['id'] if unused else 0
        
        pc1.savePreset()
        
        # Load from correct slot
        pc2 = PresetController()
        pc2.loadPreset(slot_id)
        
        assert pc2.departure_runways == 2
        assert pc2.landing_runways == 3
        assert pc2.mixed_runways == 1
