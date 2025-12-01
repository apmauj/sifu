"""
Shared pytest fixtures for SIFU tests.
This module sets up the test database and provides common fixtures.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os

# Set up test environment before importing main
os.environ.setdefault("SIFU_SKIP_BOOTSTRAP", "1")

from src.infrastructure.database import Base, get_db
from main import app


# Global test engine (session-scoped)
_test_engine = None
_TestingSessionLocal = None


def get_test_engine():
    """Get or create the test database engine."""
    global _test_engine, _TestingSessionLocal
    if _test_engine is None:
        SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
        _test_engine = create_engine(
            SQLALCHEMY_DATABASE_URL,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        # Create all tables
        Base.metadata.create_all(bind=_test_engine)
        _TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_test_engine)
    return _test_engine, _TestingSessionLocal


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Create test database tables once per test session."""
    engine, TestingSessionLocal = get_test_engine()
    
    # Override the get_db dependency
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield engine
    
    # Cleanup
    app.dependency_overrides.clear()
    engine.dispose()


@pytest.fixture
def db_session(setup_test_database):
    """Database session for direct database access in tests.
    
    Each test gets a clean session and data is rolled back after the test.
    """
    engine, TestingSessionLocal = get_test_engine()
    
    # Start a connection that will be used for this test
    connection = engine.connect()
    transaction = connection.begin()
    
    # Create a session bound to this connection
    session = TestingSessionLocal(bind=connection)
    
    # Override get_db to use this specific session
    def override_get_db():
        yield session
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield session
    
    # Rollback the transaction to clean up test data
    session.close()
    transaction.rollback()
    connection.close()
    
    # Restore the original override
    engine, TestingSessionLocal = get_test_engine()
    def restore_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    app.dependency_overrides[get_db] = restore_get_db


@pytest.fixture
def client(setup_test_database):
    """TestClient that uses the test database."""
    with TestClient(app) as c:
        yield c
