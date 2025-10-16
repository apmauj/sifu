import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.infrastructure.database import UIRecord
from main import app, get_db
from datetime import date
import uuid

# Marcar estos tests para que se ejecuten en aislamiento
pytestmark = pytest.mark.isolated


# Crear un archivo temporal SQLite para pruebas
@pytest.fixture(scope="function")
def sqlite_file(tmp_path):
    # Use pytest's tmp_path fixture for better isolation
    db_path = tmp_path / f"test_db_{uuid.uuid4().hex}.db"
    yield str(db_path)
    # pytest's tmp_path fixture handles cleanup automatically


@pytest.fixture(scope="function")
def db_session(sqlite_file):
    from sqlalchemy import create_engine
    from src.infrastructure.database import Base as DBBase

    SQLALCHEMY_DATABASE_URL = f"sqlite:///{sqlite_file}"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )

    # Create all tables fresh
    DBBase.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        # Cleanup
        try:
            with engine.connect() as conn:
                conn.execute(DBBase.metadata.drop_all(engine))
                conn.commit()
        except Exception:
            pass
        engine.dispose()


@pytest.fixture(scope="function")
def client(db_session, sqlite_file):
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{sqlite_file}"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
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


