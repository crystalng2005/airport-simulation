# Airport Simulation API Specification

This document describes all HTTP endpoints exposed by the Flask application (`app.py`), the data models used in requests and responses, and the standard error format.

---

## Endpoint Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Render main menu page |
| `POST` | `/start` | Start a new simulation |
| `GET` | `/simulation-screen` | Render simulation screen page |
| `GET` | `/configure-simulation` | Render configuration page |
| `GET` | `/presets` | Render presets page |
| `GET` | `/results` | Render results page |
| `GET` | `/result-screen` | Render result screen page |
| `GET` | `/api/number-of-runways` | Get number of runways |
| `GET` | `/api/simulation-finished` | Check if simulation has finished |
| `GET` | `/api/get-preset-data/<preset_id>` | Get full data for a preset |
| `GET` | `/api/get-presets` | Get all available presets |
| `POST` | `/api/load-preset` | Load a preset into session |
| `GET` | `/api/get-all-results` | Get all saved simulation results |
| `GET` | `/api/get-full-report/<sim_id>` | Get full report for a simulation |
| `POST` | `/api/compare-simulations` | Compare two simulations |
| `POST` | `/api/comparison-plots` | Get comparison bar charts (base64) |
| `GET` | `/api/export-current-report` | Download current report as .txt |
| `GET` | `/api/export-report/<sim_id>` | Download a saved report as .txt |
| `GET` | `/api/current-frame-actions` | Get actions from current frame |
| `GET` | `/api/current-time` | Get current simulation time |
| `POST` | `/api/next-frame` | Advance simulation by one frame |
| `GET` | `/api/aircraft/<callsign>` | Get data for a specific aircraft |
| `GET` | `/api/runway-statuses` | Get operational statuses of all runways |
| `GET` | `/api/runway-modes` | Get operating modes of all runways |
| `GET` | `/api/report` | Get current simulation report |
| `GET` | `/api/report-plots` | Get report plots for current simulation (base64) |
| `GET` | `/api/report-plots/<sim_id>` | Get report plots for a saved simulation (base64) |

---

## Standard Response Format

All API endpoints return JSON. Successful responses include `"success": true`; error responses include `"success": false` with an error message.

**Success:**
```json
{ "success": true, ... }
```

**Error:**
```json
{ "success": false, "error": "Description of what went wrong" }
```

---

## Data Models

### Plane Object
```json
{
  "callsign": "BA123",
  "origin": "LHR",
  "destination": "JFK",
  "is_departure": false,
  "fuel_level": 45.5,
  "emergency_status": "NONE",
  "target_time": "2026-02-13T14:30:00Z",
  "actual_time": null,
  "current_location": "LHR"
}
```

**Fields:**
- `callsign` (string): Unique aircraft identifier (e.g. `"BA123"`)
- `origin` (string): IATA departure airport code
- `destination` (string): IATA arrival airport code
- `is_departure` (boolean): `true` for departures, `false` for arrivals
- `fuel_level` (float): Remaining fuel in minutes (0–60)
- `emergency_status` (string): One of `"NONE"`, `"FUEL"`, `"HEALTH"`, `"MECHANICAL"`
- `target_time` (string|null): ISO 8601 scheduled time
- `actual_time` (string|null): ISO 8601 actual operation time; `null` if not yet completed
- `current_location` (string): Where the aircraft currently is

---

### Runway Object
```json
{
  "runway_number": 1,
  "is_departure": true,
  "mixed_mode": false,
  "is_available": true,
  "is_operational": true,
  "current_plane": null
}
```

**Fields:**
- `runway_number` (integer): Runway identifier (1–10)
- `is_departure` (boolean): `true` if designated for departures
- `mixed_mode` (boolean): `true` if handling both arrivals and departures
- `is_available` (boolean): `true` if no aircraft is currently using it
- `is_operational` (boolean): `false` during inspection, snow clearance, or equipment failure
- `current_plane` (string|null): Callsign of the aircraft currently on the runway, or `null`

---

### Queue Object
```json
{
  "queue_type": "departure",
  "planes": ["BA123", "AA456", "DL789"],
  "length": 3
}
```

**Fields:**
- `queue_type` (string): Either `"departure"` (takeoff queue) or `"arrival"` (holding pattern)
- `planes` (array of strings): Callsigns in queue order, front to back
- `length` (integer): Number of aircraft currently in the queue

---

### Report Object
```json
{
  "diversions": 2,
  "cancellations": 1,
  "total_planes": 50,
  "total_wait_time": 625.5,
  "total_fuel_used": 1250.75,
  "average_wait_time": 12.51,
  "efficiency_score": 85.5
}
```

**Fields:**
- `diversions` (integer): Aircraft diverted due to insufficient fuel
- `cancellations` (integer): Departures cancelled due to exceeding max wait time
- `total_planes` (integer): Total aircraft processed in simulation
- `total_wait_time` (float): Cumulative queue wait time across all aircraft (minutes)
- `total_fuel_used` (float): Cumulative fuel consumed (minutes-equivalent)
- `average_wait_time` (float): Mean queue wait time per aircraft (minutes)
- `efficiency_score` (float): Derived score (0–100) reflecting overall system performance

---

## API Endpoints

### Simulation Lifecycle

#### `POST /start`
Start a new simulation with the given configuration.

**Request:**
```json
{
  "runways": 4,
  "inbound_flow": 20,
  "outbound_flow": 20,
  "departure_runways": 2,
  "landing_runways": 2,
  "mixed_runways": 0,
  "cancellation_time": 30
}
```

**Request Fields:**
- `runways` (integer, required): Total runways, 1–10
- `inbound_flow` (integer, required): Arrivals per hour
- `outbound_flow` (integer, required): Departures per hour
- `departure_runways` (integer): Number of takeoff-only runways
- `landing_runways` (integer): Number of landing-only runways
- `mixed_runways` (integer): Number of mixed-mode runways
- `cancellation_time` (integer): Max departure wait before cancellation (minutes, default 30)

**Response (Success) — 200:**
```json
{ "success": true, "message": "Simulation started" }
```

**Response (Error) — 500:**
```json
{ "success": false, "error": "Description of error" }
```

---

#### `POST /api/next-frame`
Advance the simulation by one frame.

**Response (Success) — 200:**
```json
{ "success": true, "message": "Frame advanced" }
```

**Response (Error) — 400:**
```json
{ "success": false, "error": "No active simulation" }
```

---

#### `GET /api/simulation-finished`
Check whether the simulation has completed.

**Response (Success) — 200:**
```json
{ "success": true, "finished": false }
```

---

#### `GET /api/current-time`
Get the current simulation time (in minutes from start).

**Response (Success) — 200:**
```json
{ "success": true, "time": 47 }
```

---

#### `GET /api/current-frame-actions`
Get a list of events that occurred in the most recent simulation frame (arrivals, departures, diversions, etc.).

**Response (Success) — 200:**
```json
{
  "success": true,
  "actions": [
    "BA123 entered holding pattern",
    "AA456 landed on runway 2",
    "DL789 took off from runway 1"
  ]
}
```

---

### Aircraft

#### `GET /api/aircraft/<callsign>`
Get current data for a specific aircraft by its callsign.

**URL Parameters:**
- `callsign` (string): Aircraft callsign, e.g. `BA123`

**Response (Success) — 200:**
```json
{
  "success": true,
  "aircraft": {
    "callsign": "BA123",
    "origin": "JFK",
    "destination": "LHR",
    "is_departure": false,
    "fuel_level": 38.0,
    "emergency_status": "NONE",
    "target_time": "2026-03-12T14:30:00Z",
    "actual_time": null,
    "current_location": "holding"
  }
}
```

**Response (Not Found) — 404:**
```json
{ "success": false, "error": "Aircraft not found" }
```

---

### Runways

#### `GET /api/number-of-runways`
Get the total number of runways in the current simulation.

**Response (Success) — 200:**
```json
{ "success": true, "number": 4 }
```

---

#### `GET /api/runway-statuses`
Get the operational status of all runways.

**Response (Success) — 200:**
```json
{
  "success": true,
  "status": [
    { "runway_number": 1, "is_operational": true },
    { "runway_number": 2, "is_operational": false }
  ]
}
```

---

#### `GET /api/runway-modes`
Get the operating mode of all runways.

**Response (Success) — 200:**
```json
{
  "success": true,
  "mode": [
    { "runway_number": 1, "mode": "LANDING" },
    { "runway_number": 2, "mode": "TAKEOFF" },
    { "runway_number": 3, "mode": "MIXED" }
  ]
}
```

**Mode values:** `"LANDING"`, `"TAKEOFF"`, `"MIXED"`

---

### Reports & Results

#### `GET /api/report`
Get the report for the currently active simulation.

**Response (Success) — 200:**
```json
{
  "success": true,
  "report": {
    "diversions": 2,
    "cancellations": 1,
    "total_planes": 50,
    "total_wait_time": 625.5,
    "total_fuel_used": 1250.75,
    "average_wait_time": 12.51,
    "efficiency_score": 85.5
  }
}
```

**Response (Not Ready):**
```json
{ "success": false, "error": "Report not ready" }
```

---

#### `GET /api/get-all-results`
Get a summary list of all previously saved simulation results.

**Response (Success) — 200:**
```json
{
  "success": true,
  "results": [
    { "sim_id": 1, "timestamp": "2026-03-10T22:02:19", "total_planes": 45 },
    { "sim_id": 2, "timestamp": "2026-03-10T22:10:40", "total_planes": 60 }
  ]
}
```

---

#### `GET /api/get-full-report/<sim_id>`
Get the complete report for a previously saved simulation.

**URL Parameters:**
- `sim_id` (integer): Simulation ID

**Response (Success) — 200:**
```json
{
  "success": true,
  "report": { ...Report Object... }
}
```

**Response (Not Found) — 404:**
```json
{ "success": false, "error": "Simulation report not found" }
```

---

#### `POST /api/compare-simulations`
Compare the results of two saved simulations.

**Request:**
```json
{ "sim_id_1": 1, "sim_id_2": 2 }
```

**Response (Success) — 200:**
```json
{
  "success": true,
  "comparison": {
    "sim_1": { ...Report Object... },
    "sim_2": { ...Report Object... },
    "delta": {
      "average_wait_time": -2.1,
      "diversions": 1,
      "cancellations": 0
    }
  }
}
```

**Response (Not Found) — 404:**
```json
{ "success": false, "error": "One or both simulation IDs not found" }
```

---

#### `POST /api/comparison-plots`
Generate side-by-side bar chart images comparing two simulations, returned as base64-encoded PNG strings.

**Request:**
```json
{ "sim_id_1": 1, "sim_id_2": 2 }
```

**Response (Success) — 200:**
```json
{
  "success": true,
  "plots": {
    "wait_time": "<base64 PNG>",
    "diversions": "<base64 PNG>",
    "queue_size": "<base64 PNG>"
  }
}
```

---

#### `GET /api/report-plots`
Get base64-encoded chart images for the current active simulation report.

**Response (Success) — 200:**
```json
{
  "success": true,
  "plots": {
    "wait_time": "<base64 PNG>",
    "fuel_usage": "<base64 PNG>"
  }
}
```

---

#### `GET /api/report-plots/<sim_id>`
Get base64-encoded chart images for a specific saved simulation report.

**URL Parameters:**
- `sim_id` (integer): Simulation ID

**Response (Success) — 200:**
```json
{
  "success": true,
  "plots": { ... }
}
```

---

#### `GET /api/export-current-report`
Download the current simulation report as a `.txt` file attachment.

**Response (Success) — 200:** File download (`simulation_report.txt`)

**Response (Error) — 400:**
```json
{ "success": false, "error": "No report available" }
```

---

#### `GET /api/export-report/<sim_id>`
Download a specific saved simulation report as a `.txt` file.

**URL Parameters:**
- `sim_id` (integer): Simulation ID

**Response (Success) — 200:** File download (`simulation_<sim_id>_report.txt`)

**Response (Error) — 500:**
```json
{ "success": false, "error": "Failed to generate report" }
```

---

### Presets

#### `GET /api/get-presets`
Get a list of all available saved simulation presets.

**Response (Success) — 200:**
```json
{
  "success": true,
  "presets": [
    { "id": 0, "name": "Default", "runways": 2, "inbound_flow": 15, "outbound_flow": 15 },
    { "id": 1, "name": "Busy Airport", "runways": 4, "inbound_flow": 30, "outbound_flow": 30 }
  ]
}
```

---

#### `GET /api/get-preset-data/<preset_id>`
Get the full configuration data for a specific preset, including saved plane records and report.

**URL Parameters:**
- `preset_id` (integer): Preset ID

**Response (Success) — 200:**
```json
{
  "success": true,
  "vars": {
    "runways": 4,
    "inbound_flow": 30,
    "outbound_flow": 30
  },
  "planes": [ ...Plane Objects... ],
  "report": { ...Report Object... }
}
```

**Response (Not Found) — 404:**
```json
{ "success": false, "error": "Preset not found" }
```

---

#### `POST /api/load-preset`
Load a preset into the current session (used before navigating to configure-simulation).

**Request:**
```json
{ "preset_id": 1 }
```

**Response (Success) — 200:**
```json
{ "success": true, "message": "Preset loaded successfully" }
```

**Response (Error) — 400:**
```json
{ "success": false, "error": "No preset_id provided" }
```

---

## Reference Data

### Emergency Status Codes

| Code | Value | Meaning |
|------|-------|--------|
| `"NONE"` | 0 | No emergency |
| `"FUEL"` | 1 | Critical fuel level (<10 min remaining) |
| `"HEALTH"` | 2 | Passenger medical emergency |
| `"MECHANICAL"` | 3 | Aircraft mechanical failure |

### Runway Mode Values

| Value | Meaning |
|-------|---------|
| `"LANDING"` | Dedicated arrivals only |
| `"TAKEOFF"` | Dedicated departures only |
| `"MIXED"` | Handles both arrivals and departures |

### Runway Operational Status Values

| Value | Meaning |
|-------|---------|
| `"AVAILABLE"` | Fully operational |
| `"RUNWAY_INSPECTION"` | Closed for inspection |
| `"SNOW_CLEARANCE"` | Closed for snow clearance |
| `"EQUIPMENT_FAILURE"` | Closed due to equipment failure |

---
