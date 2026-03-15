# Airport Simulation API Specification

This document describes the HTTP endpoints exposed by the Flask application in airport_sim/app.py.

---

## Endpoint Overview

| Method | Endpoint |
|--------|----------|
| GET | / |
| POST | /start |
| GET | /simulation-screen |
| GET | /configure-simulation |
| GET | /presets |
| GET | /results |
| GET | /result-screen |
| GET | /api/number-of-runways |
| GET | /api/simulation-finished |
| GET | /api/get-preset-data/<int:preset_id> |
| GET | /api/get-presets |
| POST | /api/load-preset |
| GET | /api/get-all-results |
| GET | /api/get-full-report/<int:sim_id> |
| POST | /api/compare-simulations |
| POST | /api/comparison-plots |
| GET | /api/export-current-report |
| GET | /api/export-report/<int:sim_id> |
| GET | /api/current-frame-actions |
| GET | /api/current-time |
| POST | /api/next-frame |
| GET | /api/aircraft/<plane_call_sign> |
| GET | /api/runway-statuses |
| GET | /api/runway-modes |
| GET | /api/report |
| GET | /api/report-plots |
| GET | /api/report-plots/<int:sim_id> |

---

## Standard Response Format

Most JSON endpoints use:

Success:

```json
{ "success": true, "...": "..." }
```

Failure:

```json
{ "success": false, "error": "Description of what went wrong" }
```

Note: /api/report returns:
- HTTP 400 when there is no active simulation
- HTTP 404 when report data is not ready

---

## Simulation Lifecycle

### POST /start
Start a new simulation.

Request body fields consumed by the backend:
- runways
- inbound_flow
- outbound_flow
- departure_runways
- landing_runways
- mixed_runways
- cancellation_time
- duration
- health_emergency_prob
- fuel_emergency_prob
- weather_closure_prob
- maintenance_closure_prob
- safety_closure_prob
- construction_closure_prob
- runway_opening_prob

Notes:
- `mechanical_emergency_prob` is not currently sent as its own field from the UI payload.
- The backend currently maps `maintenance_closure_prob` into both maintenance closure probability and mechanical emergency probability.

Success response:

```json
{ "success": true, "message": "Simulation started" }
```

### POST /api/next-frame
Advance simulation by one frame.

Success response:

```json
{ "success": true, "message": "Frame advanced" }
```

### GET /api/simulation-finished
Check completion flag.

Success response:

```json
{ "success": true, "finished": false }
```

### GET /api/current-time
Return the current simulation timestamp.

Success response:

```json
{ "success": true, "time": "Sat, 01 Jan 2000 00:05:00 GMT" }
```

### GET /api/current-frame-actions
Return the latest frame action list.

Success response:

```json
{ "success": true, "actions": [["PLN0", "spawnDeparture"]] }
```

---

## Aircraft and Runways

### GET /api/aircraft/<plane_call_sign>
Return a single aircraft object from Plane.return_data().

Example success response:

```json
{
  "success": true,
  "aircraft": {
    "callsign": "PLN12",
    "origin": "LHR",
    "destination": "JFK",
    "is_departure": false,
    "fuel_level": 45,
    "emergency_status": "NONE",
    "target_time": "2000-01-01 00:40:00",
    "actual_time": "None",
    "current_location": "LHR"
  }
}
```

### GET /api/number-of-runways

```json
{ "success": true, "number": 4 }
```

### GET /api/runway-statuses
Returns an array of booleans (true means runway operational/open).

```json
{ "success": true, "status": [true, false, true] }
```

### GET /api/runway-modes
Returns an array of mode codes in runway order:
- 0 = mixed
- -1 = departure-only
- 1 = landing-only

```json
{ "success": true, "mode": [1, -1, 0] }
```

---

## Presets

### GET /api/get-presets
Returns all available preset slots with runway vars, sample planes, and report data.

### GET /api/get-preset-data/<int:preset_id>
Returns one preset in this shape:

```json
{
  "success": true,
  "vars": {
    "departure_runways": 2,
    "landing_runways": 2,
    "mixed_runways": 1
  },
  "planes": [],
  "report": {}
}
```

### POST /api/load-preset
Request:

```json
{ "preset_id": 1 }
```

Success:

```json
{ "success": true, "message": "Preset loaded successfully" }
```

---

## Reports and Results

### GET /api/report
Returns the current simulation report dictionary after simulation completion.

### GET /api/get-all-results
Returns result summaries in this shape:

```json
{
  "success": true,
  "results": [
    {
      "id": 0,
      "completed_at": "2026-03-14T16:00:00+00:00",
      "duration": 6000.0,
      "config": {
        "total_runways": 4,
        "departure_runways": 2,
        "landing_runways": 1,
        "mixed_runways": 1
      },
      "report": {}
    }
  ]
}
```

### GET /api/get-full-report/<int:sim_id>
Success:

```json
{ "success": true, "report": { "total_planes": 120 } }
```

### POST /api/compare-simulations
Request:

```json
{ "sim_id_1": 1, "sim_id_2": 2 }
```

Success shape:

```json
{
  "success": true,
  "comparison": {
    "simulation_1": {},
    "simulation_2": {},
    "metrics": {}
  }
}
```

### POST /api/comparison-plots
Request:

```json
{ "sim_id_1": 1, "sim_id_2": 2 }
```

Success response contains base64-encoded PNGs under keys such as:
- key_counts
- queues
- times
- fuel_efficiency

### GET /api/report-plots
Returns base64 plot images for current report.

### GET /api/report-plots/<int:sim_id>
Returns base64 plot images for one saved report.

### GET /api/export-current-report
Downloads simulation_report.txt.

### GET /api/export-report/<int:sim_id>
Downloads simulation_<sim_id>_report.txt.
