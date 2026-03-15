# Airport Simulation - System Design & Implementation Guide

## 1. Requirements Mapping

This section maps project requirements to implementation components:

### Priority 1: Dedicated Runway Operations

| Requirement | Component | Implementation Status |
|-------------|-----------|----------------------|
| Model departures + takeoff queue | `simulation.py`, `queue_manager.py` | ✓ Complete |
| Calculate max queue size | `results.py` (metrics) | ✓ Complete |
| Calculate average wait time | `results.py` (statistics) | ✓ Complete |
| Model arrival time variations | `currentFrameActions.py` | ✓ Complete (normal distribution) |
| Model aircraft holding pattern | `simulation.py` | ✓ Complete |
| Calculate max/avg delays | `results.py` | ✓ Complete |

### Priority 2: Flexible Runway Modes

| Requirement | Component | Implementation Status |
|-------------|-----------|----------------------|
| Mixed-use runway support | `models.py` (RunwayMode enum) | ✓ Complete |
| Multiple runway configurations | `simulation.py` (runway_list) | ✓ Complete |
| Mode switching | Web UI + `presets.py` | ✓ Complete |

### Priority 3: Runway Closures

| Requirement | Component | Implementation Status |
|-------------|-----------|----------------------|
| Runway closure specification | `models.py` (OperationalStatus) | ✓ Complete |
| Cancellation time limit | `presets.py` (configurable) | ✓ Complete |
| Diversion modeling | `currentFrameActions.py` | ✓ Complete |

### Priority 4: Fuel Management

| Requirement | Component | Implementation Status |
|-------------|-----------|----------------------|
| Fuel tracking | `plane.py` (fuel_level attribute) | ✓ Complete |
| Uniform distribution (20-60 min) | `simulation.py` (aircraft generation) | ✓ Complete |
| 10-minute threshold enforcement | `currentFrameActions.py` | ✓ Complete |
| Diversion on low fuel | `currentFrameActions.py` | ✓ Complete |

---

## 2. Aircraft State Machine

Aircraft progress through distinct states in the system:

```
┌─────────────────────────────────────────────────────────────┐
│                    AIRCRAFT LIFECYCLE                        │
└─────────────────────────────────────────────────────────────┘

ARRIVAL AIRCRAFT:
Generated → In Airspace → Holding Pattern → Runway Approach 
→ Landing → Departed
                            ↓
                    (Low fuel) → DIVERTED

DEPARTURE AIRCRAFT:
Generated → Queued for Takeoff → On Runway → Takeoff → Gone
                            ↓
                    (Timeout) → CANCELLED
```

### State Definitions

| State | Location | Time Tracked | Fuel Consumed |
|-------|----------|--------------|---------------|
| Generated | Entering system | Initial time | - |
| In Queue | Ground/Holding pattern | Enqueue → Dequeue | Yes |
| On Runway | Runway zone | Use start → Use end | Yes |
| Completed | Departed/Landed | Use end | No (left system) |
| Diverted | Removed from system | Diversion time | No |
| Cancelled | Removed from system | Cancellation time | No |

---

## 3. Timing & Scheduling Model

### Time Unit
- **Base Unit**: 1 time step (tick) = 5 minutes of airport operations
- **Simulation Speed**: User can accelerate via visualisation controller

### Arrival Generation (Normal Distribution)
```
Actual Arrival Time = Scheduled Arrival Time + Normal(μ=0, σ=5 min)

Example:
- Scheduled: 14:30:00
- Generated variance: +2.5 min
- Actual arrival: 14:32:30
```

### Departure Generation (Normal Distribution)
```
Actual Departure Queue Entry = Scheduled Departure Time + Normal(μ=0, σ=5 min)

Example:
- Scheduled: 14:30:00
- Generated variance: -1.2 min
- Queue entry: 14:28:48
```

### Processing Times
| Operation | Duration | Notes |
|-----------|----------|-------|
| Landing approach to touchdown | 1 tick (5 minutes) | Single tick runway occupation |
| Takeoff acceleration to airborne | 1 tick (5 minutes) | Runway becomes available after the tick |
| Descent in holding pattern | Instant | Per spec, ignored in timeline |
| Fuel consumption | 5 units per tick | Equivalent to 1 unit/min |

---

## 4. Queue Management Strategy

### Holding Pattern (FIFO with Priority)

**Ordering Logic:**
1. Emergency aircraft first (mechanical failure, low fuel, health issues)
2. Non-emergency aircraft in FIFO order (by arrival time)

**Vertical Separation Enforcement:**
- Minimum 1000 feet between successive aircraft
- Altitude assignment: Based on position in queue
  - Position 1: Lowest altitude (ready to land)
  - Position 2: +1000 ft
  - Position N: +(N-1)*1000 ft

**Capacity Management:**
- No hard queue limit
- Fuel level determines actual capacity
- Aircraft diverted if fuel < 10 minutes remaining

### Takeoff Queue (FIFO)

**Ordering Logic:**
- First-in, first-out until runway available
- No emergency prioritization (per spec)
- Cancellation after max wait time

**Capacity Management:**
- Aircraft cancelled if wait time > max configured (default: 30 min)
- No fuel constraints for departures

---

## 5. Runway Scheduling Algorithm

### Runway Allocation Strategy

#### Dedicated Landing Runway
```
Each time step:
  IF runway available AND holding_pattern not empty:
    aircraft = holding_pattern.dequeue()
    aircraft.land()
    runway.occupy(aircraft, duration=1 tick)
```

#### Dedicated Takeoff Runway
```
Each time step:
  IF runway available AND takeoff_queue not empty:
    aircraft = takeoff_queue.dequeue()
    aircraft.takeoff()
    runway.occupy(aircraft, duration=1 tick)
```

#### Mixed Mode Runway
```
Decision logic (prioritize based on queue pressure):
  landing_pressure = len(holding_pattern) / capacity
  takeoff_pressure = len(takeoff_queue) / capacity
  
  IF runway available:
    IF landing_pressure > takeoff_pressure:
      allocate to landing
    ELSE:
      allocate to takeoff
      
Alternative: Strict alternation (every other slot to each)
```

### Runway Closure Handling

```
When runway marked as unavailable:
  FOR each aircraft on runway:
    Move to appropriate queue
  FOR runways in mixed mode:
    Mode switches to remaining runways if available
  QueueManager: Recalculate wait times
  
Closure simulation:
  Option 1: Fixed duration (e.g., 2 hours)
  Option 2: Manual re-opening via UI
```

---

## 6. Fuel Consumption Model

### Fuel Constants (Per Spec)

| Parameter | Value | Notes |
|-----------|-------|-------|
| Initial fuel | Uniform(20, 60) min | Stored as minutes of endurance |
| Consumption rate | 5 units per tick | Equivalent to 1 unit/min |
| Minimum safe level | 10 min remaining | Must land/divert before this |
| No landing slot time | 30 min (configurable) | Diversion trigger |

### Fuel State Tracking

```python
# For each aircraft
current_fuel = initial_fuel  # minutes remaining
fuel_consumed = 0

# Each time step
if in_system:
    current_fuel -= 5  # consume one 5-minute tick of fuel
    fuel_consumed += 5
    
    if current_fuel <= 10 and in_holding_pattern:
        divert()  # Emergency drop-down landing elsewhere
```

### Diversion Decision Logic

```
At each time step:
  IF aircraft in holding_pattern:
    IF fuel_remaining <= 10 minutes:
      divert_aircraft(aircraft)
      increment_diversion_count()
    ELSE IF wait_time > max_hold_time (30 min):
      divert_aircraft(aircraft)  # Can't wait longer
```

---

## 7. Metrics Calculation Strategy

### Per-Flight Metrics
| Metric | Formula | Notes |
|--------|---------|-------|
| Delay | actual_time - scheduled_time | Signed value |
| Queue wait | dequeue_time - enqueue_time | Only while in queue |
| Fuel consumed | initial_fuel - final_fuel | Total burn |
| On-runway time | runway_exit - runway_entry | Always = 1 unit |

### Aggregate Metrics
| Metric | Calculation | Purpose |
|--------|-------------|---------|
| Max queue size | MAX(queue_length) over time | Infrastructure planning |
| Avg queue wait | SUM(wait_times) / count | Performance indicator |
| Max delay | MAX(delays) | Worst-case analysis |
| Avg delay | SUM(delays) / count | Overall efficiency |
| Fuel margin | AVG(final_fuel) at landing | Safety buffer |
| Diversion rate | diverted_count / arrival_count | System adequacy |
| Cancellation rate | cancelled_count / departure_count | Runway capacity |

### Statistical Distributions

Beyond averages, calculate:
- **Variance**: Spread of delays around mean
- **Percentiles**: 25th, 50th (median), 75th, 95th
- **Histogram Bins**: Distribution visualisation

---

## 8. Error Handling & Validation

### Input Validation Layer

```
validateParameters(runways, inbound_flow, outbound_flow):
  Assert 1 ≤ runways ≤ 10
  Assert 0 ≤ inbound_flow ≤ 200
  Assert 0 ≤ outbound_flow ≤ 200
  Assert inbound_flow + outbound_flow > 0
  Assert runway_mode valid in [LANDING, TAKEOFF, MIXED]
  Assert operational_status valid
```

### Runtime Error Handling

| Error Condition | Detection | Recovery |
|-----------------|-----------|----------|
| Queue overflow | len(queue) > MAX_QUEUE | Log warning, continue |
| Negative fuel | fuel < 0 | Force diversion immediately |
| Invalid state transition | Unexpected state | Rollback, log error |
| Runway conflict | 2+ aircraft on runway | Prevent (enforce queue) |

### User-Friendly Error Messages

```
Technical (Backend Log):
  "RuntimeError: Aircraft BA123 queue_state=HOLDING
   without matching runway_zone entry"

User Message:
  "Simulation encountered an error. 
   Your settings have been saved. Please refresh and try again."
```

---

## 9. Testing Strategy

### Unit Testing Layer
- Test queue operations independently
- Test fuel consumption calculations
- Test runway mode transitions
- Test metrics calculations

### Integration Testing Layer
- Aircraft lifecycle end-to-end
- Multi-runway interactions
- Queue priority ordering
- State transitions with multiple aircraft

### Simulation Testing Layer
- Steady-state behavior (24-hour run)
- Extreme cases (all emergencies, max aircraft)
- Closure scenarios (verify operational changes)
- Results accuracy validation

---

## 10. Configuration Management

### User Configuration Override Points
- Probability of Runway operational status (active/inspection/snow/failed)
- Runway operating mode (landing/takeoff/mixed)
- Maximum wait times before cancellation
- Simulation run duration

---

## 11. Performance Optimisation

### Current Optimisation Strategies

1. **Event-Based Processing**: Only process events when they occur
2. **Incremental Metric Updates**: Update per aircraft, not whole system
3. **Queue Indexing**: O(1) access for queue operations
4. **Lazy Calculations**: Compute stats only when requested

---