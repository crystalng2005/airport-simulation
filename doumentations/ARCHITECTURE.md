# Airport Simulation - Architecture Design Document

## 1. System Overview

The Airport Simulation system is a discrete event simulation application designed to model aircraft arrivals and departures. It provides airport operators with the analytical tools to evaluate runway configuration types and hence obtain the optimal configuration.

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
- Provide configuration templates

#### VisualisationController
**Purpose**: Manage active simulation and data presentation
- Initialise and step through simulations
- Collect simulation state snapshots
- Format data for visualisation

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

#### Queue Manager
**Responsibilities:**
- Queue data structure operations (enqueue, dequeue, peek)
- Aircraft priority sorting (emergency status)
- Queue visualisation data

#### Aircraft Models (`logic/plane.py`, `logic/models.py`)
**Data Attributes:**
- Identification: `callsign`, `origin`, `destination`
- Timing: `target_time`, `actual_time`
- Flight Status: `fuel_level`, `current_location`, runway assignment
- Emergency Status: `NONE`, `FUEL`, `MECHANICAL`, `HEALTH`

**Behavior:**
- Fuel consumption rate (constant): 5 units per tick (tick = 5 minutes)
- Arrival/departure actual times generated from a normal distribution around target time

#### Current Frame Actions
**Purpose**: Store actions produced during the current simulation tick for UI display.
- Maintains a shared list of action entries in the form `[callsign, action]`.
- Entries are populated by simulation and queue logic during updates.

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

### 4.1 Simulation Initialisation Flow
```
User Input (Web Form)
    ↓
app.py (/start)
  ↓
VisualisationController.startSimulation(data)
  ↓
SimulationController.__init__()
    ├─ Initialise Runways
    ├─ Initialise Queues
  └─ Initialise report data (reportData)
    ↓
Return confirmation to UI
```

### 4.2 Simulation Step (Each Time Unit)
```
POST /api/next-frame
    ↓
VisualisationController.tick()
    ↓
SimulationController.update()
  ├─ Generate new arrivals/departures based on configured flow
  ├─ Enqueue and prioritise emergency aircraft
  ├─ Update runway status (open/close)
  ├─ Assign queued aircraft to available runways
  ├─ Update report metrics and current frame actions
  └─ Advance simulation clock by tick size
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
- **Mixed-Runway Fairness**: Mixed-mode runway access alternates by tick between arrival and departure processing to reduce starvation

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

- **Input Validation**: Payload parsing and type conversion are validated; invalid JSON/types return error responses
- **Error Handling**: Generic error messages to users, detailed logs internally
- **Session Management**: Flask sessions used appropriately
- **File Permissions**: Results directory access controlled

---

## 9. Performance Characteristics

### Expected Behavior
- **Simulation Tick**: 1 tick = 5 simulated minutes
- **Memory Usage**: Scales with queue size, typically <100MB
- **Response Time**: <500ms per tick for normal operations

### Optimisation Strategies
- **Lazy Load Presets**: Load only when needed
- **Result Caching**: Cache computed statistics
- **Incremental Metrics**: Update metrics per-frame rather than recalculating

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
  ├→ Runway model (`models.py`)
  ├→ CurrentFrameActions
  └→ Plane + Models
```

---
