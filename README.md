# Airport Simulation

A discrete event simulation system for modeling aircraft arrivals, departures, and runway operations at a single airport. Designed to analyse operational scenarios and optimise runway configurations.

## Functions of Simulation

The Airport Simulation is a **prototype software solution** that models airport operations under various configurations. It allows airport operators to:

- Model aircraft arrivals and departures
- Analyse runway utilisation and capacity
- Project impact of runway closures
- Evaluate mixed-mode vs dedicated runway strategies
- Understand fuel constraints and diversions
- Generate analytical reports with statistical metrics

**Real-World Application**: Used by airport planners to evaluate operational changes (e.g., converting a runway from landing-only to mixed-mode during peak hours) and identify the optimal configuration before building the runways.

---

## Quick Start

### Installation

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Start the application
python app.py

# 3. Open browser
# Visit http://localhost:8080
```
---

## Documentation

This project includes comprehensive professional documentation:

| Document | Audience | Purpose |
|----------|----------|---------|
| **[ARCHITECTURE.md](doumentations/ARCHITECTURE.md)** | Developers | System structure and component responsibilities |
| **[SYSTEM_DESIGN.md](doumentations/SYSTEM_DESIGN.md)** | Developers | Requirement mapping, timing model, and algorithms |
| **[DEVELOPMENT.md](doumentations/DEVELOPMENT.md)** | Developers | Setup, dependencies, and testing workflow |
| **[API_SPECIFICATION.md](doumentations/API_SPECIFICATION.md)** | Developers | Flask route and payload reference |

---

## System Architecture

```
┌─────────────────────────────────────────────┐
│    Web UI (HTML/CSS/JavaScript)             │
│    - Simulation controls                    │
│    - Real-time visualization                │
│    - Results & reports                      │
└────────────┬────────────────────────────────┘
             │
┌────────────▼────────────────────────────────┐
│    Flask Application (Python)               │
│    - Request handling                       │
│    - Session management                     │
│    - Response formatting                    │
└────────────┬────────────────────────────────┘
             │
┌────────────▼────────────────────────────────┐
│    Business Logic Layer                     │
│    - Simulation engine                      │
│    - Queue management                       │
│    - Metrics calculation                    │
└────────────┬────────────────────────────────┘
             │
┌────────────▼────────────────────────────────┐
│    Data Models & Configuration              │
│    - Aircraft, Runways, Queues              │
│    - Presets, Results                       │
│    - Global simulation state                │
└─────────────────────────────────────────────┘
```
---

## Key Features

### Core Functionality ✓
- [x] Aircraft arrival & departure modeling
- [x] Holding pattern with vertical separation
- [x] Takeoff queue management
- [x] Multiple runway configurations
- [x] Runway operational modes (Landing, Takeoff, Mixed)
- [x] Fuel consumption & emergency diversions
- [x] Statistical metrics & reporting

### Advanced Features ✓
- [x] Runway closure simulation
- [x] Preset configurations (save/load)
- [x] Real-time visualisation
- [x] Comparison reports
- [x] Export to JSON/text
- [x] Scenario analysis tools

---

## Project Structure

```
airport_sim/
├── app.py                  # Flask entry point
├── logic/                  # Business logic
│   ├── simulation.py      # Core simulation engine
│   ├── queue_manager.py   # Queue operations
│   ├── plane.py           # Aircraft model
│   ├── currentFrameActions.py
│   ├── presets.py         # Configuration
│   ├── report.py          # Reports
│   └── results.py         # Metrics
├── static/                 # Frontend assets (CSS/JS)
├── templates/              # HTML templates
├── tests/                  # Test suite (47 tests)
├── data/                   # Data files & presets
├── exports/                # Generated results
└── doumentations/          # Documentation (4 files)
```

---

## Technology Stack

- **Backend**: Python 3.7+, Flask 2.3+
- **Frontend**: HTML5, CSS3, JavaScript
- **Data**: JSON for configuration and results
- **Testing**: pytest

---

## Understanding the Simulation

### Aircraft Lifecycle

```
ARRIVALS:                          DEPARTURES:
Generated → Holding Pattern        Generated → Takeoff Queue
    ↓                                  ↓
Lands when runway free             Takes off when runway free
    ↓                                  ↓
Departs from system                Departs from system
    ↓                                  ↓
(Or diverted if fuel low)      (Or cancelled if wait too long)
```

### Key Rules (From Spec)

1. **Emergency Priority**: Aircraft with emergencies land first
2. **Vertical Separation**: 1000ft minimum between aircraft in holding pattern
3. **Single Aircraft Per Runway**: Only one aircraft occupies runway at a time
4. **Fuel Constraints**: Aircraft diverted if fuel < 10 minutes remaining
5. **Timeouts**: Departures cancelled if wait > 30 minutes (configurable)

---


## Common Questions

**Q: Why do results vary between runs?**  
A: Aircraft arrival/departure times use normal distribution (random). Use same random seed to reproduce results.

**Q: What do the metrics mean?**  
A: See [SYSTEM_DESIGN.md](doumentations/SYSTEM_DESIGN.md) for how metrics are produced and interpreted in the simulation flow.

**Q: Can I export results?**  
A: Yes. Export to JSON (machine-readable) or text (human-readable). The export handlers are documented in [API_SPECIFICATION.md](doumentations/API_SPECIFICATION.md).

---

## Contributors

This project was developed by:

- Crystal Ng Shu Lu
- Saroop Jagdev
- Federico Parisella
- Julia Chrom
- Turki Aldossary
- Jainam Kamdar


