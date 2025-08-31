import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from database import Base, UIRecord
from main import app, get_db
from datetime import date
import tempfile
import os

# Crear un archivo temporal SQLite para pruebas
@pytest.fixture(scope="function")
def sqlite_file():
    # Use a more unique filename in current directory for Windows compatibility
    import uuid
    temp_dir = os.getcwd()
    db_path = os.path.join(temp_dir, f"test_db_{uuid.uuid4().hex}.db")
    
    # Ensure the file doesn't exist before creating
    if os.path.exists(db_path):
        os.remove(db_path)
    
    yield db_path
    
    # Ensure cleanup happens even if test fails
    try:
        if os.path.exists(db_path):
            os.remove(db_path)
    except (OSError, PermissionError):
        # In Windows, file might be locked, try to remove on next run
        pass

@pytest.fixture(scope="function")
def db_session(sqlite_file):
    from sqlalchemy import create_engine
    from database import Base
    
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{sqlite_file}"
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    
    # Create a new connection and drop all tables to ensure clean state
    with engine.connect() as conn:
        # Use SQLAlchemy's drop_all to properly clean up all tables and indexes
        try:
            Base.metadata.drop_all(bind=engine)
        except Exception as e:
            print(f"Warning during drop_all: {e}")
            pass  # Ignore errors if tables don't exist
    
    # Create all tables fresh
    Base.metadata.create_all(bind=engine)
    
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        # Clean up database
        try:
            with engine.connect() as conn:
                Base.metadata.drop_all(bind=engine)
        except Exception as e:
            print(f"Warning during final cleanup: {e}")
            pass
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