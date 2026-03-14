# Airport Simulation - Comprehensive Documentation Index

## Complete Documentation Suite

This project includes professional-grade technical documentation following commercial software development standards. Below is a guide to all available documentation.

---

## Getting Started

**Read in the following order:**

1. **[README.md](../README.md)**
   - Quick overview
   - Installation steps
   - Basic usage

2. **[USER_GUIDE.md](USER_GUIDE.md)**
   - How to use the application
   - Configuration guide
   - Running simulations
   - Interpreting results

3. **[ARCHITECTURE.md](ARCHITECTURE.md)**
   - System design overview
   - Component structure
   - Technology choices
   - Why things are the way they are

---

## 📖 Documentation by Role

### 👤 **End Users** (Airport Operators)

**Exclusively for application usage**

→ **[USER_GUIDE.md](USER_GUIDE.md)**
- How to start simulations
- Understanding results
- Common scenarios
- Troubleshooting

**Quick Reference**:
- Quick Start: §1.1
- Configuration: §2
- Interpreting Results: §5
- Troubleshooting: §7

---

### 👨‍💻 **Developers** (Working on the Code)

**For modification or extensibility**

**Read in the following order**:

1. **[ARCHITECTURE.md](ARCHITECTURE.md)** - System overview
   - Component structure
   - Data flow diagrams
   - Design decisions

2. **[SYSTEM_DESIGN.md](SYSTEM_DESIGN.md)** - Implementation details
   - State machines
   - Algorithms used
   - How features work
   - Error handling

3. **[DEVELOPMENT.md](DEVELOPMENT.md)** - How to work on the code
   - Setting up development environment
   - Git workflow
   - Running tests locally
   - Debugging guide

4. **[API_SPECIFICATION.md](API_SPECIFICATION.md)** - REST APIs
   - Endpoint definitions
   - Request/response formats
   - Data models

**When implementing features**:
- [SYSTEM_DESIGN.md](SYSTEM_DESIGN.md) explains the algorithms used
- `tests/` includes all the functions' tests
- [TESTING.md](TESTING.md) outlines the testing strategy

---

### 🧪 **QA/Testers** (Ensuring Quality)

**Outline of testing procedure**

→ **[TESTING.md](TESTING.md)**
- How to run tests
- Test coverage
- Test cases
- Known limitations

→ **[QA_REPORT.md](QA_REPORT.md)**
- Quality metrics
- Test results
- Performance validation
- Known issues

**Quick Reference**:
- Run tests: `pytest tests/ -v`
- View coverage: `pytest --cov=logic tests/ --cov-report=html`
- Test status: 47 tests, 100% passing

---

### **Stakeholders** (Evaluating the Project)

**Overview of project**

1. **[QA_REPORT.md](QA_REPORT.md)** - Quality metrics
   - Code quality scores
   - Test coverage
   - Requirements verification
   - Risk assessment

2. **[SYSTEM_DESIGN.md](SYSTEM_DESIGN.md)** (§11) - Testing strategy
   - Validation approach
   - Performance benchmarks

3. **[ARCHITECTURE.md](ARCHITECTURE.md)** (§5-6) - Design decisions
   - Justifications
   - Technology choices

---

## Documentation Map

### Core Functionality Documentation

| Document | Purpose | Audience |
|----------|---------|----------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | System design & components | Developers, architects |
| [SYSTEM_DESIGN.md](SYSTEM_DESIGN.md) | Implementation details | Developers, QA |
| [API_SPECIFICATION.md](API_SPECIFICATION.md) | REST API reference | Developers, UI |

### Quality & Testing

| Document | Purpose | Audience |
|----------|---------|----------|
| [TESTING.md](TESTING.md) | Test strategy & results | QA, developers |
| [QA_REPORT.md](QA_REPORT.md) | Quality metrics & assessment | Stakeholders, graders |

### Usage Documentation

| Document | Purpose | Audience |
|----------|---------|----------|
| [USER_GUIDE.md](USER_GUIDE.md) | How to use application | End users |
| [DEVELOPMENT.md](DEVELOPMENT.md) | Development setup & workflow | Developers |

---