# Airport Simulation API Specification

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
- `callsign` (string): Unique aircraft identifier
- `origin` (string): Departure airport code
- `destination` (string): Arrival airport code
- `is_departure` (boolean): `true` for departures, `false` for arrivals
- `fuel_level` (float): Remaining fuel percentage (0-100)
- `emergency_status` (string): One of `"NONE"`, `"FUEL"`, `"HEALTH"`, `"MECHANICAL"`
- `target_time` (string|null): ISO 8601 scheduled time
- `actual_time` (string|null): ISO 8601 actual operation time
- `current_location` (string): Current location code


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
- `runway_number` (integer): Runway identifier (1-10)
- `is_departure` (boolean): Designated for departures
- `mixed_mode` (boolean): Can handle both arrivals and departures
- `is_available` (boolean): Currently free to use
- `is_operational` (boolean): Not under maintenance
- `current_plane` (string|null): Callsign of plane using runway


### Queue Object
```json
{
  "queue_type": "departure",
  "planes": ["BA123", "AA456", "DL789"],
  "length": 3
}
```

## API Endpoints

### POST /start
**Request:**
```json
{
  "runways": 5,
  "inbound_flow": 5,
  "outbound_flow": 20,
  "departure_runways": 2,
  "landing_runways": 2,
  "mixed_runways": 1,
  "cancellation_time": 300
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Simulation started"
}
```

**Response (Error):**
```json
{
  "success": false,
  "errors": ["Runways must be between 1 and 10"]
}
```

### GET /visualization/data
**Response:**
```json
{
  "success": true,
  "data": {
    "planes": [
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
    ],
    "runways": [
      {
        "runway_number": 1,
        "is_departure": true,
        "mixed_mode": false,
        "is_available": true,
        "is_operational": true,
        "current_plane": null
      }
    ],
    "queues": [
      {
        "queue_type": "departure",
        "planes": ["BA123", "AA456"],
        "length": 2
      },
      {
        "queue_type": "arrival",
        "planes": ["DL789"],
        "length": 1
      }
    ],
    "stats": {
      "diversions": 0,
      "cancellations": 0,
      "total_planes": 3,
      "average_wait_time": 12.5,
      "total_fuel_used": 150.75
    }
  }
}
```

### GET /report
**Response:**
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

## Emergency Status Codes
- `NONE` (0): No emergency
- `FUEL` (1): Low fuel emergency
- `HEALTH` (2): Medical emergency
- `MECHANICAL` (3): Aircraft mechanical issue
