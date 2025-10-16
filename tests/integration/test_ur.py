import pytest
import importlib.util
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from src.utils.constants import MSG_NO_UR_DATA
from src.infrastructure.database import Base, get_db, URRecord
from src.domain.services import URService
from src.domain.models import URValue, URResponse
from src.domain.excel_processor import URExcelProcessor

# Optional dependency (pandas) may not be available in some minimal environments (e.g. Python 3.13 wheels not yet published)
PANDAS_AVAILABLE = importlib.util.find_spec("pandas") is not None


# Test database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///./data/test_ur.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override the DB dependency for tests."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    """Create/drop test database metadata once for the module."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    """Yield a fresh DB session (clean tables each test)."""
    # Drop & recreate all tables to ensure isolation
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def sample_ur_data(db_session):
    """Seed sample UR records for tests."""
    sample_records = [
        URRecord(año=2023, mes=1, valor=1501.26),
        URRecord(año=2023, mes=2, valor=1502.25),
        URRecord(año=2023, mes=3, valor=1579.57),
        URRecord(año=2024, mes=1, valor=1650.00),
        URRecord(año=2024, mes=2, valor=1675.50),
        URRecord(año=2025, mes=1, valor=1800.00),
        URRecord(año=2025, mes=6, valor=1827.25),
    ]

    for record in sample_records:
        db_session.add(record)
    db_session.commit()

    return sample_records


class TestURService:
    """Tests for URService core logic."""

    def test_get_ur_by_year_month_exists(self, db_session, sample_ur_data):
        """Get UR by year/month that exists."""
        service = URService(db_session)
        result = service.get_ur_by_year_month(2023, 1)

        assert result is not None
        assert result.año == 2023
        assert result.mes == 1
        assert result.valor == 1501.26

    def test_get_ur_by_year_month_not_exists(self, db_session, sample_ur_data):
        """Get UR by year/month that does not exist."""
        service = URService(db_session)
        result = service.get_ur_by_year_month(2023, 12)

        assert result is None

    def test_get_ur_by_year(self, db_session, sample_ur_data):
        """Get all UR values for a given year."""
        service = URService(db_session)
        results = service.get_ur_by_year(2023)

        assert len(results) == 3
        assert all(r.año == 2023 for r in results)
        assert results[0].mes == 1  # Ordenados por mes
        assert results[1].mes == 2
        assert results[2].mes == 3

    def test_get_ur_by_year_empty(self, db_session, sample_ur_data):
        """Get UR values for a year with no data."""
        service = URService(db_session)
        results = service.get_ur_by_year(2022)

        assert len(results) == 0

    def test_get_ur_by_range_same_year(self, db_session, sample_ur_data):
        """Get UR values for a range within the same year."""
        service = URService(db_session)
        results = service.get_ur_by_range(2023, 1, 2023, 3)

        assert len(results) == 3
        assert all(r.año == 2023 for r in results)
        assert results[0].mes == 1
        assert results[2].mes == 3

    def test_get_ur_by_range_multiple_years(self, db_session, sample_ur_data):
        """Get UR values across a multi-year range."""
        service = URService(db_session)
        results = service.get_ur_by_range(2023, 2, 2024, 1)

        assert len(results) == 3  # 2023: feb, mar + 2024: ene
        assert results[0].año == 2023 and results[0].mes == 2
        assert results[1].año == 2023 and results[1].mes == 3
        assert results[2].año == 2024 and results[2].mes == 1

    def test_get_latest_ur(self, db_session, sample_ur_data):
        """Get most recent UR value."""
        service = URService(db_session)
        result = service.get_latest_ur()

        assert result is not None
        assert result.año == 2025
        assert result.mes == 6
        assert result.valor == 1827.25

    def test_get_total_records(self, db_session, sample_ur_data):
        """Count total UR records."""
        service = URService(db_session)
        total = service.get_total_records()

        assert total == 7

    def test_get_year_range_available(self, db_session, sample_ur_data):
        """Get min/max year available."""
        service = URService(db_session)
        min_year, max_year = service.get_year_range_available()

        assert min_year == 2023
        assert max_year == 2025

    def test_get_available_years(self, db_session, sample_ur_data):
        """Get available years (descending)."""
        service = URService(db_session)
        years = service.get_available_years()

        assert years == [2025, 2024, 2023]  # Ordenados descendente


class TestURAPI:
    """API endpoint tests for UR."""

    def test_get_latest_ur_success(self, client, sample_ur_data):
        """Endpoint: latest UR value."""
        response = client.get("/api/ur/latest")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["año"] == 2025
        assert data["data"]["mes"] == 6
        assert data["data"]["valor"] == 1827.25

    def test_get_ur_by_year_month_success(self, client, sample_ur_data):
        """Endpoint: UR by year/month success."""
        response = client.get("/api/ur/year-month/2023/1")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["año"] == 2023
        assert data["data"]["mes"] == 1
        assert data["data"]["valor"] == 1501.26

    def test_get_ur_by_year_month_not_found(self, client, sample_ur_data):
        """Endpoint: UR by year/month not found."""
        response = client.get("/api/ur/year-month/2023/12")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "No UR data available for 2023-12" in data["message"]

    def test_get_ur_by_year_month_invalid_month(self, client, sample_ur_data):
        """Endpoint: invalid month parameter."""
        response = client.get("/api/ur/year-month/2023/13")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "Month must be between 1 and 12" in data["message"]

    def test_get_ur_by_year_success(self, client, sample_ur_data):
        """Endpoint: UR by year success."""
        response = client.get("/api/ur/year/2023")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 3
        assert all(item["año"] == 2023 for item in data["data"])

    def test_get_ur_by_year_empty(self, client, sample_ur_data):
        """Endpoint: UR by year - no data."""
        response = client.get("/api/ur/year/2022")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert data["message"].startswith(MSG_NO_UR_DATA)
        assert "2022" in data["message"]

    def test_get_ur_by_range_success(self, client, sample_ur_data):
        """Endpoint: UR by explicit range success."""
        response = client.get("/api/ur/range/2023/1/2023/3")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 3

    def test_get_ur_by_range_invalid_months(self, client, sample_ur_data):
        """Endpoint: range with invalid months."""
        response = client.get("/api/ur/range/2023/0/2023/13")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        # Accept standardized constant message (singular 'Month')
        assert "Month must be between 1 and 12" in data["message"]

    def test_get_ur_by_range_invalid_range(self, client, sample_ur_data):
        """Endpoint: invalid chronological range."""
        response = client.get("/api/ur/range/2024/6/2024/3")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "Start period must be before or equal to end period" in data["message"]

    def test_get_ur_by_range_post(self, client, sample_ur_data):
        """Endpoint: POST range (accepts legacy Spanish keys)."""
        payload = {"año_inicio": 2023, "mes_inicio": 1, "año_fin": 2023, "mes_fin": 2}
        response = client.post("/api/ur/range", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 2

    def test_get_ur_info(self, client, sample_ur_data):
        """Endpoint: general UR info stats."""
        response = client.get("/api/ur/info")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["total_records"] == 7
        assert data["data"]["year_range"]["min_year"] == 2023
        assert data["data"]["year_range"]["max_year"] == 2025
        assert len(data["data"]["available_years"]) == 3


@pytest.mark.skipif(not PANDAS_AVAILABLE, reason="pandas not installed")
class TestURExcelProcessor:
    """Excel processor tests for UR."""

    def test_parse_excel_data_empty(self):
        """Parse empty DataFrame returns empty list."""
        import pandas as pd

        processor = URExcelProcessor()

        empty_df = pd.DataFrame()
        result = processor.parse_excel_data(empty_df)

        assert result == []

    def test_parse_excel_data_sample(self):
        """Parse sample DataFrame with header row."""
        import pandas as pd

        processor = URExcelProcessor()
        # Create sample data simulating BHU format
        data = {
            "AÑO": [2023, 2024],
            "ENERO": [1501.26, 1650.00],
            "FEBRERO": [1502.25, 1675.50],
            "MARZO": [1579.57, None],
        }
        df = pd.DataFrame(data)

        # Simulate first row contains headers by inserting a header row
        header_row = pd.DataFrame(
            [["AÑO", "ENERO", "FEBRERO", "MARZO"]], columns=df.columns
        )
        df_with_header = pd.concat([header_row, df], ignore_index=True)

        result = processor.parse_excel_data(df_with_header)

        # Basic sanity
        assert len(result) >= 4  # At least 4 valid records

        # Specific values
        records_dict = {(r[0], r[1]): r[2] for r in result}
        assert records_dict.get((2023, 1)) == 1501.26
        assert records_dict.get((2023, 2)) == 1502.25
        assert records_dict.get((2024, 1)) == 1650.00


class TestURModels:
    """UR models tests."""

    def test_ur_value_creation(self):
        """Create URValue instance."""
        ur_value = URValue(año=2023, mes=6, valor=1500.50)

        assert ur_value.año == 2023
        assert ur_value.mes == 6
        assert ur_value.valor == 1500.50

    def test_ur_value_validation(self):
        """Validate URValue and serialization (bilingual keys)."""
        # Valid data
        ur_value = URValue(año=2023, mes=12, valor=1500.50)
        assert ur_value.mes == 12

        # Serialization (returns both Spanish & English keys)
        data = ur_value.dict()
        assert data["año"] == 2023
        assert data["mes"] == 12
        assert data["valor"] == 1500.50

    def test_ur_response_success(self):
        """URResponse with single value success."""
        ur_value = URValue(año=2023, mes=6, valor=1500.50)
        response = URResponse(success=True, message="Test successful", data=ur_value)

        assert response.success is True
        assert response.message == "Test successful"
        assert response.data.año == 2023

    def test_ur_response_list(self):
        """URResponse with list of values."""
        ur_values = [
            URValue(año=2023, mes=1, valor=1500.50),
            URValue(año=2023, mes=2, valor=1510.75),
        ]
        response = URResponse(success=True, message="List of values", data=ur_values)

        assert response.success is True
        assert len(response.data) == 2
        assert response.data[0].mes == 1
        assert response.data[1].mes == 2


# Integration tests
class TestURIntegration:
    """Integration tests covering basic workflow."""

    def test_full_workflow(self, client, db_session):
        """Full workflow: insert records then query endpoints."""
        # 1. Add sample records directly
        sample_records = [
            URRecord(año=2023, mes=6, valor=1500.00),
            URRecord(año=2023, mes=7, valor=1510.00),
        ]

        for record in sample_records:
            db_session.add(record)
        db_session.commit()

        # 2. Test latest endpoint
        response = client.get("/api/ur/latest")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        # 3. Test specific year-month endpoint
        response = client.get("/api/ur/year-month/2023/6")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["valor"] == 1500.00

        # 4. Test year endpoint
        response = client.get("/api/ur/year/2023")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 2


if __name__ == "__main__":
    # Allow running this file directly for quick debugging
    pytest.main([__file__, "-v", "--tb=short"])


