"""
Tests simplificados para endpoints de la API
"""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from datetime import date
from main import app
from src.domain.models import UIValue


class TestAPISimple:
    """Tests simplificados para la API"""

    @pytest.fixture
    def client(self):
        """Cliente de prueba"""
        return TestClient(app)

    def test_health_check(self, client):
        """Test endpoint de salud"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "timestamp" in data

    def test_get_latest_ui_success(self, client):
        """Test obtener último UI exitoso"""
        with patch("main.UIService") as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_ui = UIValue(date=date(2024, 1, 1), value=5.1234)
            mock_service.get_latest_ui.return_value = mock_ui

            with patch("main.get_db"):
                response = client.get("/api/ui/latest")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Latest UI value retrieved successfully" in data["message"]

    def test_get_latest_ui_not_found(self, client):
        """Test obtener último UI no encontrado"""
        with patch("main.UIService") as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.get_latest_ui.return_value = None

            with patch("main.get_db"):
                response = client.get("/api/ui/latest")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "No UI data available" in data["message"]

    def test_get_ui_by_date_success(self, client):
        """Test obtener UI por fecha exitoso"""
        with patch("main.UIService") as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_ui = UIValue(date=date(2024, 1, 15), value=5.2000)
            mock_service.get_ui_by_date.return_value = mock_ui

            with patch("main.get_db"):
                response = client.get("/api/ui/2024-01-15")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "UI value for 2024-01-15 retrieved successfully" in data["message"]

    def test_get_ui_by_date_not_found_with_closest(self, client):
        """Test obtener UI por fecha no encontrado pero con valor cercano"""
        with patch("main.UIService") as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.get_ui_by_date.return_value = None
            mock_closest = UIValue(date=date(2024, 1, 14), value=5.1900)
            mock_service.get_ui_closest_to_date.return_value = mock_closest

            with patch("main.get_db"):
                response = client.get("/api/ui/2024-01-15")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert (
            "No data for 2024-01-15. Showing closest previous value" in data["message"]
        )

    def test_get_ui_range_success(self, client):
        """Test obtener rango de UI exitoso"""
        with patch("main.UIService") as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_ui_1 = UIValue(date=date(2024, 1, 1), value=5.0000)
            mock_ui_2 = UIValue(date=date(2024, 1, 2), value=5.0100)
            mock_service.get_ui_by_date_range.return_value = [mock_ui_1, mock_ui_2]

            with patch("main.get_db"):
                response = client.get("/api/ui/range/2024-01-01/2024-01-02")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert (
            "UI values for range 2024-01-01 - 2024-01-02 retrieved successfully"
            in data["message"]
        )

    def test_get_info_success(self, client):
        """Test obtener información exitoso"""
        with patch("main.UIService") as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_latest = UIValue(date=date(2024, 12, 1), value=6.0000)
            mock_service.get_latest_ui.return_value = mock_latest
            mock_service.get_total_records.return_value = 8436
            mock_service.get_date_range_available.return_value = (
                date(2002, 6, 1),
                date(2024, 12, 1),
            )

            with patch("main.get_db"):
                response = client.get("/api/info")

        assert response.status_code == 200
        data = response.json()
        assert data["total_records"] == 8436
        assert data["date_range"]["min_date"] == "2002-06-01"
        assert data["date_range"]["max_date"] == "2024-12-01"

    def test_get_latest_ur_success(self, client):
        """Test obtener último UR exitoso"""
        with patch("main.URService") as mock_service_class:
            mock_service = mock_service_class.return_value
            from src.domain.models import URValue

            mock_ur = URValue(year=2024, month=12, value=6.1234)
            mock_service.get_latest_ur.return_value = mock_ur

            with patch("main.get_db"):
                response = client.get("/api/ur/latest")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Latest UR value retrieved successfully" in data["message"]

    def test_get_ur_by_year_month_success(self, client):
        """Test obtener UR por año y mes exitoso"""
        with patch("main.URService") as mock_service_class:
            mock_service = mock_service_class.return_value
            from src.domain.models import URValue

            mock_ur = URValue(year=2024, month=1, value=5.1234)
            mock_service.get_ur_by_year_month.return_value = mock_ur

            with patch("main.get_db"):
                response = client.get("/api/ur/year-month/2024/1")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "UR value for 2024-01 retrieved successfully" in data["message"]

    def test_get_ur_by_year_success(self, client):
        """Test obtener UR por año exitoso"""
        with patch("main.URService") as mock_service_class:
            mock_service = mock_service_class.return_value
            from src.domain.models import URValue

            mock_ur_1 = URValue(year=2024, month=1, value=5.1234)
            mock_ur_2 = URValue(year=2024, month=2, value=5.2234)
            mock_service.get_ur_by_year.return_value = [mock_ur_1, mock_ur_2]

            with patch("main.get_db"):
                response = client.get("/api/ur/year/2024")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Retrieved 2 UR values for year 2024" in data["message"]

    def test_get_ur_info_success(self, client):
        """Test obtener información UR exitoso"""
        with patch("main.URService") as mock_service_class:
            mock_service = mock_service_class.return_value
            from src.domain.models import URValue

            mock_service.get_total_records.return_value = 410
            mock_service.get_year_range_available.return_value = (2020, 2024)
            mock_service.get_latest_ur.return_value = URValue(
                year=2024, month=12, value=6.0
            )
            mock_service.get_available_years.return_value = [
                2020,
                2021,
                2022,
                2023,
                2024,
            ]

            with patch("main.get_db"):
                response = client.get("/api/ur/info")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["total_records"] == 410

    # Test eliminado - endpoint obsoleto

