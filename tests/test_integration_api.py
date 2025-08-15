import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, UIRecord
from main import app, get_db
from datetime import date
import tempfile
import os

# Crear un archivo temporal SQLite para pruebas
@pytest.fixture(scope="function")
def sqlite_file():
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)
    yield db_path
    os.remove(db_path)

@pytest.fixture(scope="function")
def db_session(sqlite_file):
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{sqlite_file}"
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()

@pytest.fixture(scope="function")
def client(db_session, sqlite_file):
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{sqlite_file}"
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as c:
            yield c
    finally:
        app.dependency_overrides.clear()
        # Explicitly dispose engine to release file handle before fixture teardown
        engine.dispose()

def test_get_ui_by_date_integration(client, db_session):
    record = UIRecord(date=date(2024, 1, 1), value=5.1234)
    db_session.add(record)
    db_session.commit()
    response = client.get("/api/ui/2024-01-01")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["value"] == 5.1234
    assert data["data"]["date"] == "2024-01-01"

def test_get_ui_by_date_not_found_integration(client):
    response = client.get("/api/ui/2024-01-02")
    assert response.status_code == 404 