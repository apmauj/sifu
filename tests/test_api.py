"""
Tests para endpoints de la API
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from datetime import date
from main import app
from src.domain.models import UIValue


@pytest.fixture
def client():
    """Cliente de test para FastAPI"""
    return TestClient(app)


@pytest.fixture
def mock_ui_service(monkeypatch):
    """Mock del servicio UI"""
    mock = Mock()
    monkeypatch.setattr("main.UIService", lambda db: mock)
    return mock


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

    def test_get_latest_ui_success(self, client, mock_ui_service):
        """Test obtener último UI exitoso"""
        mock_ui = UIValue(date=date(2024, 1, 1), value=5.1234)
        mock_ui_service.get_latest_ui.return_value = mock_ui

        with patch("main.get_db"):
            response = client.get("/api/ui/latest")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Latest UI value retrieved successfully" in data["message"]
        assert data["data"]["date"] == "2024-01-01"
        assert data["data"]["value"] == 5.1234

    def test_get_latest_ui_not_found(self, client, mock_ui_service):
        """Test obtener último UI no encontrado"""
        mock_ui_service.get_latest_ui.return_value = None

        with patch("main.get_db"):
            response = client.get("/api/ui/latest")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "No UI data available" in data["message"]
        assert data["data"] is None

    def test_get_latest_ui_exception(self, client, mock_ui_service):
        """Test excepción en obtener último UI"""
        mock_ui_service.get_latest_ui.side_effect = Exception("Database error")

        with patch("main.get_db"):
            response = client.get("/api/ui/latest")

        assert response.status_code == 500

    def test_get_ui_by_date_success(self, client, mock_ui_service):
        """Test obtener UI por fecha exitoso"""
        mock_ui = UIValue(date=date(2024, 1, 15), value=5.2000)
        mock_ui_service.get_ui_by_date.return_value = mock_ui

        with patch("main.get_db"):
            response = client.get("/api/ui/2024-01-15")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "UI value for 2024-01-15 retrieved successfully" in data["message"]
        assert data["data"]["date"] == "2024-01-15"
        assert data["data"]["value"] == 5.2000

    def test_get_ui_by_date_not_found(self, client, mock_ui_service):
        """Test obtener UI por fecha no encontrado"""
        mock_ui_service.get_ui_by_date.return_value = None
        mock_ui_service.get_ui_closest_to_date.return_value = None

        with patch("main.get_db"):
            response = client.get("/api/ui/2024-01-15")

        assert response.status_code == 404

    def test_get_ui_by_date_closest_found(self, client, mock_ui_service):
        """Test obtener UI por fecha no encontrado pero sí valor cercano"""
        mock_ui_service.get_ui_by_date.return_value = None
        mock_closest = UIValue(date=date(2024, 1, 14), value=5.1900)
        mock_ui_service.get_ui_closest_to_date.return_value = mock_closest

        with patch("main.get_db"):
            response = client.get("/api/ui/2024-01-15")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert (
            "No data for 2024-01-15. Showing closest previous value" in data["message"]
        )
        assert data["data"]["date"] == "2024-01-14"
        assert data["data"]["value"] == 5.1900

    def test_get_ui_by_date_invalid_format(self, client, mock_ui_service):
        """Test obtener UI con formato de fecha inválido"""
        with patch("main.get_db"):
            response = client.get("/api/ui/invalid-date")

        assert (
            response.status_code == 422
        )  # FastAPI devuelve 422 para validación de parámetros

    def test_get_ui_by_date_exception(self, client, mock_ui_service):
        """Test excepción en obtener UI por fecha"""
        mock_ui_service.get_ui_by_date.side_effect = Exception("Database error")

        with patch("main.get_db"):
            response = client.get("/api/ui/2024-01-15")

        assert response.status_code == 500

    def test_get_ui_range_success(self, client, mock_ui_service):
        """Test obtener rango de UI exitoso"""
        mock_ui_1 = UIValue(date=date(2024, 1, 1), value=5.0000)
        mock_ui_2 = UIValue(date=date(2024, 1, 2), value=5.0100)
        mock_ui_service.get_ui_by_date_range.return_value = [mock_ui_1, mock_ui_2]

        with patch("main.get_db"):
            response = client.get("/api/ui/range/2024-01-01/2024-01-02")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert (
            "UI values for range 2024-01-01 - 2024-01-02 retrieved successfully. 2 records found"
            in data["message"]
        )
        assert len(data["data"]) == 2
        assert data["data"][0]["date"] == "2024-01-01"
        assert data["data"][1]["date"] == "2024-01-02"

    def test_get_ui_range_not_found(self, client, mock_ui_service):
        """Test obtener rango de UI no encontrado"""
        mock_ui_service.get_ui_by_date_range.return_value = []

        with patch("main.get_db"):
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

    def test_get_ui_range_invalid_dates(self, client, mock_ui_service):
        """Test obtener rango de UI con fechas inválidas"""
        with patch("main.get_db"):
            response = client.get("/api/ui/range/invalid-date/2024-01-02")

        assert (
            response.status_code == 422
        )  # FastAPI devuelve 422 para validación de parámetros

    def test_get_ui_range_invalid_period(self, client, mock_ui_service):
        """Test obtener rango de UI con período inválido"""
        with patch("main.get_db"):
            response = client.get("/api/ui/range/2024-01-15/2024-01-01")

        assert response.status_code == 400  # HTTPException con status_code=400
        data = response.json()
        assert "Start date must be less than or equal to end date" in data["detail"]

    def test_get_ui_range_exception(self, client, mock_ui_service):
        """Test excepción en obtener rango de UI"""
        mock_ui_service.get_ui_by_date_range.side_effect = Exception("Database error")

        with patch("main.get_db"):
            response = client.get("/api/ui/range/2024-01-01/2024-01-02")

        assert response.status_code == 500

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

    def test_get_info_success(self, client, mock_ui_service):
        """Test obtener información exitoso"""
        mock_latest = UIValue(date=date(2024, 12, 1), value=6.0000)
        mock_ui_service.get_latest_ui.return_value = mock_latest
        mock_ui_service.get_total_records.return_value = 8436
        mock_ui_service.get_date_range_available.return_value = (
            date(2002, 6, 1),
            date(2024, 12, 1),
        )

        with patch("main.get_db"):
            response = client.get("/api/info")
            assert response.status_code == 200
            data = response.json()
            # El endpoint /api/info no devuelve un campo "success", devuelve directamente los datos
            assert data["total_records"] == 8436
            assert data["date_range"]["min_date"] == "2002-06-01"
            assert data["date_range"]["max_date"] == "2024-12-01"
            assert data["latest_ui"]["date"] == "2024-12-01"
            assert data["latest_ui"]["value"] == 6.0000
            assert (
                data["data_source"]
                == "National Institute of Statistics (INE) - Uruguay"
            )

    def test_get_info_no_data(self, client, mock_ui_service):
        """Test obtener información sin datos"""
        mock_ui_service.get_latest_ui.return_value = None
        mock_ui_service.get_total_records.return_value = 0
        mock_ui_service.get_date_range_available.return_value = (None, None)

        with patch("main.get_db"):
            response = client.get("/api/info")

        assert response.status_code == 200
        data = response.json()
        # El endpoint /api/info no devuelve un campo "success", devuelve directamente los datos
        assert data["total_records"] == 0
        assert data["latest_ui"] is None
        assert data["date_range"]["min_date"] is None
        assert data["date_range"]["max_date"] is None

    def test_get_info_exception(self, client, mock_ui_service):
        """Test excepción en obtener información"""
        mock_ui_service.get_latest_ui.side_effect = Exception("Database error")

        with patch("main.get_db"):
            response = client.get("/api/info")

        assert response.status_code == 500


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
    """Tests for startup event coverage"""

    @patch("database.SessionLocal")
    @patch("main.UIService")
    @patch("main.excel_processor")
    def test_startup_event_with_existing_data(
        self, mock_processor, mock_service_class, mock_session_local
    ):
        """Test startup event when database already has data"""
        mock_db = Mock()
        mock_session_local.return_value = mock_db

        mock_service = Mock()
        mock_service.get_total_records.return_value = 1000  # Has data
        mock_service_class.return_value = mock_service

        # Execute startup event
        import asyncio
        from main import startup_event

        asyncio.run(startup_event())

        mock_service.get_total_records.assert_called()
        mock_db.close.assert_called_once()
        mock_processor.refresh_data.assert_not_called()

    @patch("database.SessionLocal")
    @patch("main.UIService")
    @patch("main.excel_processor")
    def test_startup_event_no_data_success(
        self, mock_processor, mock_service_class, mock_session_local
    ):
        """Test startup event when no data exists and loading succeeds"""
        mock_db = Mock()
        mock_session_local.return_value = mock_db

        mock_service = Mock()
        mock_service.get_total_records.return_value = 0  # No data
        mock_service_class.return_value = mock_service

        mock_processor.refresh_data.return_value = (True, "Data loaded", 1000)

        import asyncio
        from main import startup_event

        asyncio.run(startup_event())

        mock_processor.refresh_data.assert_called_once_with(mock_db)

    @patch("database.SessionLocal")
    @patch("main.UIService")
    @patch("main.excel_processor")
    def test_startup_event_no_data_failure(
        self, mock_processor, mock_service_class, mock_session_local
    ):
        """Test startup event when no data exists and loading fails"""
        mock_db = Mock()
        mock_session_local.return_value = mock_db

        mock_service = Mock()
        mock_service.get_total_records.return_value = 0  # No data
        mock_service_class.return_value = mock_service

        mock_processor.refresh_data.return_value = (False, "Download failed", 0)

        import asyncio
        from main import startup_event

        asyncio.run(startup_event())

        mock_processor.refresh_data.assert_called_once_with(mock_db)

    @patch("database.SessionLocal")
    def test_startup_event_exception(self, mock_session_local):
        """Test startup event handles exceptions gracefully"""
        mock_session_local.side_effect = Exception("Database connection error")

        import asyncio
        from main import startup_event

        # Should not raise exception
        asyncio.run(startup_event())

        mock_session_local.assert_called_once()

