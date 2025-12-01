# 🧪 SIFU Test Suite

This directory contains the test suite for SIFU, organized by test type following pytest conventions.

## 📁 Structure

```
tests/
├── __init__.py
├── conftest.py          # Shared pytest configuration & fixtures
├── unit/                # Unit tests (fast, isolated)
│   ├── test_*.py
│   └── __init__.py
├── integration/         # Integration tests (slower, multiple components)
│   ├── test_*.py
│   └── __init__.py
└── demo/                # Demo/standalone examples (educational)
    ├── *_test.py
    └── __init__.py
```

## 🏃 Running Tests

```bash
# Run all tests
pytest

# Run specific test type
pytest tests/unit/          # Only unit tests (fast)
pytest tests/integration/   # Only integration tests
pytest tests/demo/          # Only demos

# Run with coverage
pytest --cov=src --cov-report=html

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_api.py
```

## 🎯 Test Categories

### 🧪 Unit Tests (`tests/unit/`)
Fast, isolated tests for individual components.
- Execution time: < 1 second per test
- External dependencies: Mocked
- Good for: Quick feedback during development

**Examples:**
- `test_api.py` - API endpoint tests
- `test_services.py` - Business logic tests
- `test_models.py` - Data model tests

### 🔗 Integration Tests (`tests/integration/`)
Tests that verify multiple components working together.
- Execution time: 1-30 seconds per test
- External dependencies: May use test database
- Good for: Verifying system workflows

**Examples:**
- `test_integration_api.py` - Full API flows
- `test_brou_monitoring.py` - Monitoring system
- `test_health_checks.py` - Health check endpoints

### 🎬 Demo Tests (`tests/demo/`)
Standalone exploratory tests and examples.
- Purpose: Educational, demonstrating SIFU features
- Execution: Can run independently
- Good for: Understanding how to use SIFU

**Examples:**
- `async_test.py` - Async operation examples
- `main_test.py` - Main server tests
- `simple_test.py` - Simple standalone examples

## 📝 Writing New Tests

1. **Identify the test type:**
   - Unit? → `tests/unit/`
   - Integration? → `tests/integration/`
   - Demo? → `tests/demo/`

2. **Use proper naming:**
   - Unit/Integration: `test_component.py`
   - Demo: `demo_feature.py` or `component_test.py`

3. **Follow pytest conventions:**
   ```python
   import pytest
   
   class TestMyComponent:
       def test_happy_path(self):
           # Arrange
           # Act
           # Assert
           pass
       
       def test_error_case(self):
           # Test error handling
           pass
   ```

4. **Use shared fixtures from conftest.py:**
   ```python
   def test_with_fixture(test_client, test_db):
       # test_client and test_db are shared fixtures
       pass
   ```

## 🛠️ Pytest Configuration

See `pytest.ini` in project root for configuration:
- Test discovery paths
- Markers for categorizing tests
- Coverage options

## 📚 Resources

- [pytest documentation](https://docs.pytest.org/)
- [Testing best practices](https://docs.python-guide.org/writing/tests/)
- SIFU Architecture documentation
