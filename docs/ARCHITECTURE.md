# Airport Simulation - Architecture Design Document

## 1. System Overview

The Airport Simulation system is a discrete event simulation application designed to model aircraft arrivals and departures at a single airport. It provides airport operators with the analytical tools to evaluate runway configuration types and hence obtain the optimal configuration.

### Purpose
- Model aircraft arrivals, departures, and holding patterns
- Analyse runway utilisation and aircraft throughput
- Project impact of runway closures and configuration changes
- Provide statistical metrics for operational decision-making

### Key Stakeholders
- Airport Managers and Operators
- Client (Dorset Software)

---

## 2. Architectural Overview

The system follows a **Layered Architecture** pattern with separation of concerns:

```
┌─────────────────────────────────────────────┐
│         Presentation Layer (Flask)          │
│   Web Interface + Visualisation + Reports   │
└────────────────────┬────────────────────────┘
                     │
┌────────────────────▼────────────────────────┐
│      Application Layer (Controllers)        │
│   Preset | Visualisation | Report | Sim     │
└────────────────────┬────────────────────────┘
                     │
┌────────────────────▼────────────────────────┐
│           Business Logic Layer              │
│    Simulation | Queue Manager | Current     │
│       Frame Actions | Plane Models          │
└────────────────────┬────────────────────────┘
                     │
┌────────────────────▼────────────────────────┐
│                 Data Layer                  │
│   Models | Global State | Results Storage   │
└─────────────────────────────────────────────┘
```

### Rationale
- **Separation of Concerns**: Each layer has distinct responsibilities
- **Testability**: Functional requirements logic can be tested independently
- **Maintainability**: Changes to UI don't affect simulation logic
- **Extensibility**: Ability to modify or extend individual layers

---

## 3. Core Components

### 3.1 Presentation Layer (`app.py`, `templates/`, `static/`)

**Responsibilities:**
- HTTP request/response handling
- Session management
- Template rendering
- Static asset serving

**Key Classes:**
- `MainController`: Central request dispatcher
  - Manages preset and visualisation controllers
  - Handles simulation lifecycle (start, tick, stop)
  - Error handling and response formatting

**Design Patterns Used:**
- **MVC Pattern**: Applied at presentation layer
  - View: HTML templates
  - Controller: Flask route handling (app.py)
  - Model: Business logic layer
  
- **Application Controllers Pattern**: Coordinate cross-layer interactions
  - PresetController: Bridges UI ↔ simulation engine
  - VisualisationController: Manages simulation state/presentation
  - PerformanceReport: Transforms business data for user consumption
  - Note: These are NOT traditional MVC controllers; they're adapter
    patterns that isolate the presentation layer from business logic
    
- **Singleton**: Flask app instance (single application instance)

---

### 3.2 Application Layer (`logic/presets.py`, `logic/visualisation.py`, etc.)

#### PresetController
**Purpose**: Manage simulation configurations
- Load/save preset configurations
- Validate input parameters
- Provide configuration templates

#### VisualisationController
**Purpose**: Manage active simulation and data presentation
- Initialise and step through simulations
- Collect simulation state snapshots
- Format data for visualization

#### PerformanceReport
**Purpose**: Generate analytical reports
- Calculate statistics from simulation results
- Compare multiple simulation runs
- Export reports to various formats

**Design Pattern**: **Strategy Pattern** - Different report types can be implemented (extensibility)

---

### 3.3 Business Logic Layer (`logic/simulation.py`, `logic/queue_manager.py`, etc.)

#### Simulation Engine
**Core Responsibilities:**
1. **Discrete Event Processing**
   - Process arrival/departure events sequentially
   - Maintain global time counter
   - Update aircraft state each frame

2. **Runway Management**
   - Track runway availability and operating modes
   - Enforce single-aircraft-per-runway constraint
   - Handle mode transitions (landing/takeoff/mixed)

3. **Queue Management**
   - Maintain holding pattern queue (FIFO + priority for emergencies)
   - Maintain takeoff queue (FIFO)
   - Enforce vertical separation in holding pattern (1000ft minimum)

#### Queue Manager
**Responsibilities:**
- Queue data structure operations (enqueue, dequeue, peek)
- Aircraft priority sorting (emergency status)
- Queue visualization data

#### Aircraft Models (`logic/plane.py`, `logic/models.py`)
**Data Attributes:**
- Identification: `callsign`, `operator`, `origin`, `destination`
- Timing: `scheduled_time`, `actual_time`, `flight_duration`
- Flight Status: `altitude`, `ground_speed`, `fuel_level`
- Emergency Status: `NONE`, `FUEL`, `MECHANICAL`, `HEALTH`

**Behavior:**
- Fuel consumption rate (constant): ~1 unit per time step
- Descent in holding pattern: instantaneous
- Altitude constraints: 1000ft separation minimum

#### Current Frame Actions
**Purpose**: Execute simulation logic for each time step
- Process new arrivals/departures entering system
- Move aircraft through queues
- Update fuel levels
- Detect emergency conditions
- Execute takeoffs/landings

**Key Methods:**
- `processArrivals()`: Handle new aircraft entering airspace
- `processDepartures()`: Handle new aircraft from ground
- `processHoldingPattern()`: Manage landing queue
- `processTakeoffQueue()`: Manage takeoff queue
- `updateFuelLevels()`: Decrement fuel for all aircraft

---

### 3.4 Data Layer

#### Global Report Data (`logic/globals/reportData.py`)
**Purpose**: Centralised global storage for simulation statistics
**Stores:**
- Maximum queue lengths
- Total wait times (for averaging)
- Aircraft delays
- Diversions/cancellations
- Emergency events

**Design Pattern**: **Registry Pattern** - Single source of truth for simulation statistics

#### Results & Records
**Structure:**
- `data/results.json`: Last run results with summary statistics
- `data/records/`: Historical record of individual aircraft
- `exports/`: Generated reports and comparisons

---

## 4. Data Flow Diagrams

### 4.1 Simulation Initialization Flow
```
User Input (Web Form)
    ↓
PresetController.validateAndLoad()
    ↓
Simulation.__init__()
    ├─ Initialize Runways
    ├─ Initialize Queues
    └─ Initialize Aircraft Generator
    ↓
VisualisationController.startSimulation()
    ↓
Return confirmation to UI
```

### 4.2 Simulation Step (Each Time Unit)
```
MainController.tick()
    ↓
Simulation.step()
    ├─ CurrentFrameActions.process()
    │  ├─ generateNewArrivals()
    │  ├─ generateNewDepartures()
    │  ├─ processHoldingPattern()
    │  ├─ processTakeoffQueue()
    │  ├─ processTakeoff()
    │  └─ processLanding()
    ├─ updateFuelLevels()
    ├─ checkEmergencyConditions()
    └─ collectMetrics()
    ↓
VisualisationController.getSnapshot()
    ↓
Return state to UI
```

---

## 5. Design Decisions & Justifications

### 5.1 Layered Architecture
- **Commercial Standard**: Used in industry projects for maintainability
- **Team Development**: Different team members can work on different layers
- **Testing**: Each layer can be unit tested independently
- **Scaling**: Can handle simulation complexity growth

### 5.2 Discrete Event Simulation
- **Efficiency**: Only processes meaningful time points (events)
- **Accuracy**: Deterministic timing for reproducible results
- **Scalability**: Ability to handle thousands of aircraft

### 5.3 Queue Management Design
- **Priority Queue for Arrivals**: Emergency aircraft goes to runway first
- **FIFO for Departures**: Fair, predictable behavior
- **Vertical Separation Model**: Abstracted from real ATC

### 5.4 Fuel Consumption Model
- **Constant Rate**: Abstracted per spec assumptions
- **Uniform Distribution (20-60 min)**: Realistic aircraft variation
- **10-minute threshold**: Safety margin before diversion

---

## 6. Technology Stack Justification

| Component | Technology | Why |
|-----------|-----------|-----|
| Backend | Python 3.x | Data science libraries, rapid development |
| Web Framework | Flask | Lightweight, suitable for PoC, Pythonic |
| Frontend | HTML5/CSS3/JavaScript | Standard web technologies, good UX control |
| Data Format | JSON | Human-readable, language-agnostic |
| Testing | pytest/unittest | Industry standard, good coverage |
| Reporting | Plain text/JSON | Easy to parse, no external dependencies |

---

## 7. Extensibility & Maintenance

### 7.1 Future Enhancement Points
1. **Multiple Airport Support**: Extend to airport networks
2. **Advanced Visualisation**: Real-time 3D aircraft display
3. **Weather Integration**: Dynamic weather event modeling
4. **Machine Learning**: Predictive delay estimation
5. **Database Integration**: Persistent storage of historical runs

### 7.2 Code Organisation Principles
- **Single Responsibility**: Each class has one reason to change
- **DRY**: Shared logic in base classes
- **Open/Closed Principle**: Open for extension, closed for modification
- **Dependency Injection**: Controllers receive dependencies

---

## 8. Security Considerations

- **Input Validation**: All user inputs validated before processing
- **Error Handling**: Generic error messages to users, detailed logs internally
- **Session Management**: Flask sessions used appropriately
- **File Permissions**: Results directory access controlled

---

## 9. Performance Characteristics

### Expected Behavior
- **Simulation Speed**: ~1000 total aircraft per 10-second simulation
- **Memory Usage**: Scales with queue size, typically <100MB
- **Response Time**: <500ms per tick for normal operations
- **Scalability Limit**: ~50 concurrent users with current architecture

### Optimisation Strategies
- **Lazy Load Presets**: Load only when needed
- **Result Caching**: Cache computed statistics
- **Incremental Metrics**: Update metrics per-frame rather than recalculating

---

## 10. Version Control Strategy

- **Main Branch**: Stable, tested code
- **Development Branch**: Active feature development
- **Feature Branches**: Individual features/components
- **Git Workflow**: Feature → Dev → Main (with PR reviews)

---

## Appendix: Component Interaction Map

```
User
  ↓
app.py (MainController)
  ├→ PresetController → Simulation
  ├→ VisualisationController → Simulation
  └→ PerformanceReport ← ReportData
  
Simulation
  ├→ Queue Manager
  ├→ RunwayManager
  ├→ CurrentFrameActions
  └→ Plane + Models
```

---
