# Airport Simulation - Development & Deployment Guide

## 1. Development Environment Setup

### 1.1 Prerequisites

```
Python: 3.7 or higher
pip: Latest version
Git: For version control
```

### 1.2 Initial Setup

```bash
# Clone the repository
git clone https://github.com/yourname/cs261.git
cd cs261/airport_sim

# Create Python virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import flask; print(flask.__version__)"
```

### 1.3 Project Structure

```
airport_sim/
├── app.py                    # Flask entry point
├── requirements.txt          # Dependencies
├── pytest.ini                # Test configuration
├── README.md
│
├── logic/                   # Business logic layer
│   ├── simulation.py        # Core simulation engine
│   ├── queue_manager.py     # Queue operations
│   ├── plane.py             # Aircraft model
│   ├── models.py            # Data models
│   ├── currentFrameActions.py  # Frame processing
│   ├── presets.py          # Configuration management
│   ├── report.py           # Report generation
│   ├── results.py          # Results handling
│   └── globals/
│       └── reportData.py   # Global state
│
├── static/                 # Frontend assets
│   ├── css/                # Stylesheets
│   └── js/                 # JavaScript
│
├── templates/              # HTML templates
│   ├── menu.html
│   ├── configure_simulation.html
│   ├── simulation_screen.html
│   ├── result_screen.html
│   └── results.html
│
├── tests/                  # Test suite
│   ├── test_functional_requirements.py
│   └── __init__.py
│
└─── data/                   # Data files
    ├── presets.json         # Saved configurations
    ├── presets_meta.json
    └── records/

```

---

## 2. Development Workflow

### 2.1 Git Workflow

**Branch Strategy**: Feature branching with main protection

```bash
# Create feature branch
git checkout -b feature/aircraft-model-improvements

# Make changes
git add logic/plane.py
git commit -m "Improve fuel consumption model accuracy"

# Push feature branch
git push origin feature/aircraft-model-improvements

# Create Pull Request (on GitHub)
# - Request code review
# - Ensure tests pass
# - Discuss changes

# After approval, merge to develop
git checkout develop
git merge feature/aircraft-model-improvements
git push origin develop

# Periodic release to main
git checkout main
git merge develop
git tag v1.0.1
git push origin main --tags
```

### 2.2 Development Best Practices

**Code Style**:
```python
# Follow PEP 8 guidelines
# Use meaningful variable names
# Prefer explicit over implicit

# Good:
def process_holding_pattern(pattern: HoldingPattern) -> List[Aircraft]:
    """Process aircraft in holding pattern this frame."""
    if not pattern.has_aircraft():
        return []
    
    landing_aircraft = pattern.dequeue_next()
    return [landing_aircraft] if landing_aircraft else []

# Avoid:
def processHoldingPattern(p):
    if len(p) > 0:
        return p[0]
```

**Documentation**:
- Use docstrings for all public methods
- Comment complex logic
- Keep README current
- Update architecture docs when making design changes

**Testing**:
- Write tests before implementation (TDD)
- Maintain >80% code coverage
- Run tests before committing
- Use descriptive test names

### 2.3 Common Development Tasks

#### Adding a New Feature

```
1. Create feature branch
   git checkout -b feature/runway-closure-feature

2. Write tests first
   tests/test_runway_closure.py
   
3. Implement feature
   logic/simulation.py (modify close_runway method)
   
4. Run tests
   pytest tests/test_runway_closure.py -v
   
5. Update documentation
   docs/SYSTEM_DESIGN.md
   
6. Commit and push
   git add .
   git commit -m "Add runway closure feature"
   git push origin feature/runway-closure-feature
   
7. Create pull request and get review
```

#### Fixing a Bug

```
1. Create issue describing bug
2. Create fix branch
   git checkout -b fix/fuel-consumption-bug
3. Write test reproducing bug
4. Fix the bug
5. Verify test passes
6. Commit with issue reference
   git commit -m "Fix fuel consumption calculation (fixes #42)"
7. Push and create PR
```

#### Running Tests Locally

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest --cov=logic tests/ --cov-report=html

# Run specific test file
pytest tests/test_aircraft_states.py -v

# Run specific test
pytest tests/test_aircraft_states.py::test_landing_lifecycle -v

# Run tests matching pattern
pytest tests/test_fuel* -v

# Watch mode (rerun on file change)
pip install pytest-watch
ptw tests/
```

---

## 3. Configuration Management

### 3.1 Configuration Files

**requirements.txt**:
```
Flask==2.3.0
pytest==7.3.0
pytest-cov==4.1.0
scipy==1.10.0
```

### 3.2 Environment Variables

```bash
# Create .env file (not committed to git)
DEBUG=False
FLASK_ENV=production
PORT=5000
LOG_LEVEL=INFO
```

---

## 4. Building & Deployment

### 4.1 Local Development

```bash
# Start development server
python app.py

# Server runs on http://localhost:5000
# Automatically reloads on code changes (debug mode)
```
---

## 5. Performance Profiling

### 5.1 Python Profiler

```python
import cProfile
import pstats

# Profile a function
profiler = cProfile.Profile()
profiler.enable()

# Run code to profile
simulation.run()

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)  # Top 20 functions
```

### 5.2 Memory Profiling

```bash
pip install memory-profiler

python -m memory_profiler app.py
```

### 5.3 Simulation Benchmarking

```python
import time

start = time.time()
results = simulation.run()
duration = time.time() - start

print(f"Simulation took {duration:.2f} seconds")
print(f"Processed {len(results.aircraft)} aircraft")
print(f"Throughput: {len(results.aircraft) / duration:.1f} aircraft/sec")
```
---

### 5.4 .gitignore

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
*.egg
*.egg-info/
dist/
build/

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Logs
*.log

# Environment variables
.env

# Generated files
exports/
*.json~
```
---

## 6. Documentation Maintenance

### 6.1 Updating Documentation

When making code changes:

1. Update relevant docs
2. Update code comments
3. Update docstrings
4. Update architecture docs if structure changes
5. Include doc updates in commit

```bash
# Example
git commit -m "Add fuel burn rate configuration (docs: update SYSTEM_DESIGN.md)"
```
---