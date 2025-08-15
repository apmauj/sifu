import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from datetime import datetime, timedelta
from main import app, _cache_lock

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_caches():
    """Reset in-memory caches before each test.

    Previous implementation only reassigned local variables and did not mutate the
    module attributes, causing warm caches from startup to persist. We now explicitly
    set the module-level globals to None under the shared lock.
    """
    import main as main_module
    with _cache_lock:
        main_module.bcu_cache = None  # type: ignore
        main_module.brou_cache = None  # type: ignore
    yield

@patch('main._update_bcu_cache')
def test_bcu_current_uses_cache(mock_update):
    # First call forces refresh because cache empty
    resp1 = client.get('/api/exchange-rate/current')
    assert resp1.status_code == 200
    # Second call immediately should NOT force another refresh (mock called only once)
    resp2 = client.get('/api/exchange-rate/current')
    assert resp2.status_code == 200
    assert mock_update.call_count == 1

@patch('main._update_bcu_cache')
@patch('main.bcu_cache', { 'data': [{'currency':'USD','buy_rate':1,'sell_rate':1,'average_rate':1,'source':'BCU','timestamp':datetime.utcnow().isoformat()}], 'updated_at': datetime.utcnow() - timedelta(minutes=10) })
def test_bcu_current_recent_cache(mock_update):
    resp = client.get('/api/exchange-rate/current')
    assert resp.status_code == 200
    # recent cache (<55m) -> no refresh
    mock_update.assert_not_called()

@patch('main._update_bcu_cache')
@patch('main.bcu_cache', { 'data': [{'currency':'USD','buy_rate':1,'sell_rate':1,'average_rate':1,'source':'BCU','timestamp':datetime.utcnow().isoformat()}], 'updated_at': datetime.utcnow() - timedelta(hours=2) })
def test_bcu_current_stale_cache(mock_update):
    resp = client.get('/api/exchange-rate/current')
    assert resp.status_code == 200
    # stale cache (>55m) -> refresh
    mock_update.assert_called_once()

@patch('main._update_bcu_cache')
def test_bcu_current_force_refresh(mock_update):
    resp = client.get('/api/exchange-rate/current?force_refresh=true')
    assert resp.status_code == 200
    mock_update.assert_called_once()

@patch('main._update_brou_cache')
def test_brou_current_uses_cache(mock_update):
    resp1 = client.get('/api/brou/current')
    assert resp1.status_code == 200
    resp2 = client.get('/api/brou/current')
    assert resp2.status_code == 200
    assert mock_update.call_count == 1

@patch('main._update_brou_cache')
@patch('main.brou_cache', { 'data': [{'currency':'USD','buy_rate':1,'sell_rate':1,'average_rate':1,'arbitrage_buy':1,'arbitrage_sell':1,'preferential':None,'source':'BROU','timestamp':datetime.utcnow().isoformat()}], 'updated_at': datetime.utcnow() - timedelta(minutes=5) })
def test_brou_current_recent_cache(mock_update):
    resp = client.get('/api/brou/current')
    assert resp.status_code == 200
    mock_update.assert_not_called()

@patch('main._update_brou_cache')
@patch('main.brou_cache', { 'data': [{'currency':'USD','buy_rate':1,'sell_rate':1,'average_rate':1,'arbitrage_buy':1,'arbitrage_sell':1,'preferential':None,'source':'BROU','timestamp':datetime.utcnow().isoformat()}], 'updated_at': datetime.utcnow() - timedelta(hours=2) })
def test_brou_current_stale_cache(mock_update):
    resp = client.get('/api/brou/current')
    assert resp.status_code == 200
    mock_update.assert_called_once()

@patch('main._update_brou_cache')
def test_brou_current_force_refresh(mock_update):
    resp = client.get('/api/brou/current?force_refresh=true')
    assert resp.status_code == 200
    mock_update.assert_called_once()
