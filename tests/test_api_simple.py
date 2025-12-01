"""
Tests simplificados para endpoints de la API.

Note: Tests de UI están en test_api.py con fixtures de base de datos.
Este archivo contiene tests complementarios para UR y otros endpoints.
"""

from datetime import date
from src.infrastructure.database import UIRecord, URRecord


# Note: client and db_session fixtures are provided by conftest.py


class TestAPISimple:
    """Tests simplificados para la API"""

    def test_health_check(self, client):
        """Test endpoint de salud"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "timestamp" in data

    def test_get_latest_ui_success(self, client, db_session):
        """Test obtener último UI exitoso"""
        # Insert test data
        test_record = UIRecord(date=date(2024, 1, 1), value=5.1234)
        db_session.add(test_record)
        db_session.commit()

        response = client.get("/api/ui/latest")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Latest UI value retrieved successfully" in data["message"]

    def test_get_latest_ui_not_found(self, client):
        """Test obtener último UI no encontrado"""
        response = client.get("/api/ui/latest")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "No UI data available" in data["message"]

    def test_get_ui_by_date_success(self, client, db_session):
        """Test obtener UI por fecha exitoso"""
        # Insert test data
        test_record = UIRecord(date=date(2024, 1, 15), value=5.2000)
        db_session.add(test_record)
        db_session.commit()

        response = client.get("/api/ui/2024-01-15")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "UI value for 2024-01-15 retrieved successfully" in data["message"]

    def test_get_ui_by_date_not_found_with_closest(self, client, db_session):
        """Test obtener UI por fecha no encontrado pero con valor cercano"""
        # Insert test data for a previous date
        test_record = UIRecord(date=date(2024, 1, 14), value=5.1900)
        db_session.add(test_record)
        db_session.commit()

        response = client.get("/api/ui/2024-01-15")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert (
            "No data for 2024-01-15. Showing closest previous value" in data["message"]
        )

    def test_get_ui_range_success(self, client, db_session):
        """Test obtener rango de UI exitoso"""
        # Insert test data
        test_records = [
            UIRecord(date=date(2024, 1, 1), value=5.0000),
            UIRecord(date=date(2024, 1, 2), value=5.0100),
        ]
        db_session.add_all(test_records)
        db_session.commit()

        response = client.get("/api/ui/range/2024-01-01/2024-01-02")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert (
            "UI values for range 2024-01-01 - 2024-01-02 retrieved successfully"
            in data["message"]
        )

    def test_get_info_success(self, client, db_session):
        """Test obtener información exitoso"""
        # Insert test data
        test_records = [
            UIRecord(date=date(2002, 6, 1), value=1.0),
            UIRecord(date=date(2024, 12, 1), value=6.0000),
        ]
        db_session.add_all(test_records)
        db_session.commit()

        response = client.get("/api/info")

        assert response.status_code == 200
        data = response.json()
        assert data["total_records"] == 2
        assert data["date_range"]["min_date"] == "2002-06-01"
        assert data["date_range"]["max_date"] == "2024-12-01"

    def test_get_latest_ur_success(self, client, db_session):
        """Test obtener último UR exitoso"""
        # Insert test data
        test_record = URRecord(year=2024, month=12, value=6.1234)
        db_session.add(test_record)
        db_session.commit()

        response = client.get("/api/ur/latest")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Latest UR value retrieved successfully" in data["message"]

    def test_get_ur_by_year_month_success(self, client, db_session):
        """Test obtener UR por año y mes exitoso"""
        # Insert test data
        test_record = URRecord(year=2024, month=1, value=5.1234)
        db_session.add(test_record)
        db_session.commit()

        response = client.get("/api/ur/year-month/2024/1")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "UR value for 2024-01 retrieved successfully" in data["message"]

    def test_get_ur_by_year_success(self, client, db_session):
        """Test obtener UR por año exitoso"""
        # Insert test data
        test_records = [
            URRecord(year=2024, month=1, value=5.1234),
            URRecord(year=2024, month=2, value=5.2234),
        ]
        db_session.add_all(test_records)
        db_session.commit()

        response = client.get("/api/ur/year/2024")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Retrieved 2 UR values for year 2024" in data["message"]

    def test_get_ur_info_success(self, client, db_session):
        """Test obtener información UR exitoso"""
        # Insert test data
        test_records = [
            URRecord(year=2020, month=1, value=4.0),
            URRecord(year=2024, month=12, value=6.0),
        ]
        db_session.add_all(test_records)
        db_session.commit()

        response = client.get("/api/ur/info")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["total_records"] == 2

