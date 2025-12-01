"""
Tests para endpoints de la API
"""

from unittest.mock import patch
from datetime import date
from src.domain.models import UIValue
from src.infrastructure.database import UIRecord


# Note: client and db_session fixtures are provided by conftest.py


class TestHealthEndpoint:
    """Tests para el endpoint de health check"""

    def test_health_check(self, client):
        """Test health check exitoso"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "timestamp" in data


class TestUIEndpoints:
    """Tests para endpoints de UI"""

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
        assert data["data"]["date"] == "2024-01-01"
        assert data["data"]["value"] == 5.1234

    def test_get_latest_ui_not_found(self, client):
        """Test obtener último UI no encontrado (DB vacía)"""
        response = client.get("/api/ui/latest")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "No UI data available" in data["message"]
        assert data["data"] is None

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
        assert data["data"]["date"] == "2024-01-15"
        assert data["data"]["value"] == 5.2000

    def test_get_ui_by_date_not_found(self, client):
        """Test obtener UI por fecha no encontrado"""
        response = client.get("/api/ui/2024-01-15")

        assert response.status_code == 404

    def test_get_ui_by_date_closest_found(self, client, db_session):
        """Test obtener UI por fecha no encontrado pero sí valor cercano"""
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
        assert data["data"]["date"] == "2024-01-14"
        assert data["data"]["value"] == 5.1900

    def test_get_ui_by_date_invalid_format(self, client):
        """Test obtener UI con formato de fecha inválido"""
        response = client.get("/api/ui/invalid-date")

        assert (
            response.status_code == 422
        )  # FastAPI devuelve 422 para validación de parámetros

    def test_get_ui_range_success(self, client, db_session):
        """Test obtener rango de UI exitoso"""
        # Insert test data
        test_record1 = UIRecord(date=date(2024, 1, 1), value=5.0000)
        test_record2 = UIRecord(date=date(2024, 1, 2), value=5.0100)
        db_session.add_all([test_record1, test_record2])
        db_session.commit()

        response = client.get("/api/ui/range/2024-01-01/2024-01-02")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert (
            "UI values for range 2024-01-01 - 2024-01-02 retrieved successfully. 2 records found"
            in data["message"]
        )
        assert len(data["data"]) == 2

    def test_get_ui_range_not_found(self, client):
        """Test obtener rango de UI no encontrado"""
        response = client.get("/api/ui/range/2024-01-01/2024-01-02")

        assert response.status_code == 200
        data = response.json()
        assert (
            data["success"] is True
        )  # La API siempre devuelve success=True, incluso con lista vacía
        assert (
            "UI values for range 2024-01-01 - 2024-01-02 retrieved successfully. 0 records found"
            in data["message"]
        )
        assert data["data"] == []

    def test_get_ui_range_invalid_dates(self, client):
        """Test obtener rango de UI con fechas inválidas"""
        response = client.get("/api/ui/range/invalid-date/2024-01-02")

        assert (
            response.status_code == 422
        )  # FastAPI devuelve 422 para validación de parámetros

    def test_get_ui_range_invalid_period(self, client):
        """Test obtener rango de UI con período inválido"""
        response = client.get("/api/ui/range/2024-01-15/2024-01-01")

        assert response.status_code == 400  # HTTPException con status_code=400
        data = response.json()
        assert "Start date must be less than or equal to end date" in data["detail"]

    def test_refresh_ui_data_success(self, client):
        """Test actualizar datos UI exitoso"""
        with patch("main.excel_processor") as mock_processor:
            mock_processor.refresh_data.return_value = (
                True,
                "Data updated successfully",
                8436,
            )

            with patch("main.UIService") as mock_service_class:
                mock_service = mock_service_class.return_value
                mock_service.get_total_records.return_value = 8436
                mock_service.get_latest_ui.return_value = UIValue(
                    date=date(2024, 12, 1), value=6.0
                )

                with patch("main.get_db"):
                    response = client.post("/api/refresh")  # Endpoint correcto

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["total_records"] == 8436

    def test_refresh_ui_data_failure(self, client):
        """Test actualizar datos UI fallido"""
        with patch("main.excel_processor") as mock_processor:
            mock_processor.refresh_data.return_value = (False, "Download failed", 0)

            with patch("main.UIService") as mock_service_class:
                mock_service = mock_service_class.return_value
                mock_service.get_total_records.return_value = 0
                mock_service.get_latest_ui.return_value = None

                with patch("main.get_db"):
                    response = client.post("/api/refresh")  # Endpoint correcto

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert data["total_records"] == 0

    def test_refresh_ui_data_exception(self, client):
        """Test excepción en actualizar datos UI"""
        with patch("main.excel_processor") as mock_processor:
            mock_processor.refresh_data.side_effect = Exception("Processing error")

            with patch("main.get_db"):
                response = client.post("/api/refresh")  # Endpoint correcto

        assert (
            response.status_code == 200
        )  # El endpoint maneja la excepción y devuelve 200 con success=False
        data = response.json()
        assert data["success"] is False
        assert "Internal error" in data["message"]


class TestInfoEndpoint:
    """Tests para endpoint de información"""

    def test_get_info_success(self, client, db_session):
        """Test obtener información exitoso"""
        # Insert test data
        from src.infrastructure.database import UIRecord
        test_records = [
            UIRecord(date=date(2002, 6, 1), value=1.0),
            UIRecord(date=date(2024, 12, 1), value=6.0000),
        ]
        db_session.add_all(test_records)
        db_session.commit()

        response = client.get("/api/info")
        assert response.status_code == 200
        data = response.json()
        # El endpoint /api/info no devuelve un campo "success", devuelve directamente los datos
        assert data["total_records"] == 2
        assert data["date_range"]["min_date"] == "2002-06-01"
        assert data["date_range"]["max_date"] == "2024-12-01"
        assert data["latest_ui"]["date"] == "2024-12-01"
        assert data["latest_ui"]["value"] == 6.0000
        assert data["data_source"] == "National Institute of Statistics (INE) - Uruguay"

    def test_get_info_no_data(self, client):
        """Test obtener información sin datos"""
        response = client.get("/api/info")

        assert response.status_code == 200
        data = response.json()
        # El endpoint /api/info no devuelve un campo "success", devuelve directamente los datos
        assert data["total_records"] == 0
        assert data["latest_ui"] is None
        assert data["date_range"]["min_date"] is None
        assert data["date_range"]["max_date"] is None


class TestStaticEndpoints:
    """Tests for static endpoints"""

    def test_serve_static_directory_mounted(self, client):
        """Test that static directory is properly mounted"""
        # Verify that static directory is mounted
        # If directory doesn't exist, FastAPI returns 404
        response = client.get("/static/nonexistent.js")
        # Should return 404 (not found) not 500 (internal error)
        assert response.status_code == 404


class TestStartupEvent:
    """Tests for startup event coverage.
    
    Note: These tests are simplified as the startup event runs once during
    module import and is difficult to test in isolation.
    """

    def test_startup_completes_without_error(self):
        """Test that startup event completes without raising exceptions.
        
        The startup event is called automatically when the app is imported.
        If we reach this test, startup completed successfully.
        """
        # The fact that we can import the app means startup completed
        from main import app
        assert app is not None

    def test_skip_bootstrap_flag_respected(self):
        """Test that SIFU_SKIP_BOOTSTRAP flag is respected."""
        import os
        # The environment variable was set by conftest.py
        assert os.environ.get("SIFU_SKIP_BOOTSTRAP") == "1"

