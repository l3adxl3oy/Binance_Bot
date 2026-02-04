# Trading Bot Tests

## 📊 Test Structure

```
tests/
├── conftest.py              # Pytest fixtures and configuration
├── test_indicators.py       # Unit tests for indicators
├── test_models.py          # Unit tests for data models
├── test_managers.py        # Unit tests for managers
├── test_api.py             # Integration tests for API
└── test_integration.py     # End-to-end integration tests
```

## 🧪 Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test File
```bash
pytest tests/test_indicators.py
```

### Run Specific Test Class
```bash
pytest tests/test_indicators.py::TestIndicators
```

### Run Specific Test Function
```bash
pytest tests/test_indicators.py::TestIndicators::test_rsi_calculation
```

### Run with Coverage
```bash
pytest --cov=. --cov-report=html
```

### Run Only Unit Tests
```bash
pytest -m unit
```

### Run Only Integration Tests
```bash
pytest -m integration
```

### Verbose Output
```bash
pytest -v
```

### Show Print Statements
```bash
pytest -s
```

## 📋 Test Categories

### Unit Tests
- ✅ `test_indicators.py` - Technical indicators (RSI, MACD, BB, ATR)
- ✅ `test_models.py` - Position and TradeHistory models
- ✅ `test_managers.py` - PositionManager and SymbolManager

### Integration Tests
- ✅ `test_api.py` - FastAPI endpoints and WebSocket
- ✅ `test_integration.py` - Complete workflows and database

## 🎯 Test Coverage

Expected coverage:
- **Core Indicators**: >90%
- **Data Models**: >85%
- **Managers**: >80%
- **API Endpoints**: >75%
- **Overall**: >80%

## 📝 Writing New Tests

### Example Unit Test
```python
def test_my_function():
    """Test description"""
    result = my_function(input_data)
    assert result == expected_output
```

### Example Integration Test
```python
@patch('module.ExternalDependency')
def test_workflow(mock_dependency):
    """Test complete workflow"""
    # Setup
    mock_dependency.return_value = mock_data
    
    # Execute
    result = execute_workflow()
    
    # Verify
    assert result.success is True
```

## 🔧 Fixtures Available

- `sample_klines_data` - Mock Binance klines data
- `sample_price_data` - Sample price arrays for indicators
- `mock_binance_client` - Mocked Binance API client
- `mock_position` - Sample Position object
- `mock_config` - Mocked configuration

## ⚡ Performance Tests

For performance testing:
```bash
pytest --durations=10
```

## 🐛 Debugging Tests

Run with pdb:
```bash
pytest --pdb
```

Stop on first failure:
```bash
pytest -x
```

## 📊 Continuous Integration

Tests are run automatically on:
- Every commit
- Every pull request
- Before deployment

## 🔒 Test Database

Tests use SQLite in-memory database by default.
No need to configure production database.

## ⚠️ Important Notes

1. **Mock External APIs**: Always mock Binance API calls
2. **Isolate Tests**: Each test should be independent
3. **Clean Up**: Use fixtures to clean up test data
4. **Fast Execution**: Unit tests should run in <1s each
5. **Deterministic**: Tests should produce same results every time

## 📈 Test Reports

Generate HTML report:
```bash
pytest --html=report.html --self-contained-html
```

Generate JUnit XML (for CI):
```bash
pytest --junitxml=junit.xml
```
