# Airport Simulation - Development Guide

## 1. Development Environment Setup

### 1.1 Prerequisites

- Python 3.10 or higher (project currently tested on Python 3.11)
- pip
- Git

### 1.2 Install and Run

```bash
cd airport_sim
..\.venv\Scripts\python.exe -m pip install -r requirements.txt
..\.venv\Scripts\python.exe app.py
```

## 2. Project Structure

```text
airport_sim/
|-- app.py
|-- iata.txt
|-- pytest.ini
|-- requirements.txt
|-- data/
|   |-- preset0.json
|   |-- preset1.json
|   |-- preset2.json
|   |-- presets_meta.json
|   |-- results.json
|   `-- records/
|-- exports/
|-- logic/
|   |-- currentFrameActions.py
|   |-- models.py
|   |-- plane.py
|   |-- presets.py
|   |-- queue_manager.py
|   |-- report.py
|   |-- reportComparison.py
|   |-- results.py
|   |-- simulation.py
|   |-- visualisation.py
|   `-- globals/
|       `-- reportData.py
|-- static/
|   |-- css/
|   `-- js/
|-- templates/
|   |-- configure_simulation.html
|   |-- menu.html
|   |-- presets.html
|   |-- result_screen.html
|   |-- results.html
|   `-- simulation_screen.html
`-- tests/
    |-- __init__.py
    `-- test_functional_requirements.py
```

## 3. Dependencies

Current requirements.txt:

```text
Flask==3.1.2
matplotlib==3.10.8
numpy==2.4.2
pytest==9.0.2
Jinja2==3.1.6
Flask-Bootstrap==5.3.8
python-dotenv
```

## 4. Running Tests

From the `airport_sim/` directory, using the project virtual environment:

```bash
# Navigate to the simulation folder first
cd airport_sim

# Run all tests
..\.venv\Scripts\python.exe -m pytest tests/ -v

# Run a specific test class
..\.venv\Scripts\python.exe -m pytest tests/ -v -k "TestFR1"

```

## 5. Testing Principles

- Early testing during development, not after implementation.
- Comprehensive coverage of critical simulation paths.
- Reproducible and deterministic test execution.
- Maintainable tests that are easy to read and modify.
- Automated test execution with pytest.