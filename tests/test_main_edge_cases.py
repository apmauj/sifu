from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestMainEdgeCases:
    @patch("main.get_db")
    def test_get_ui_by_date_service_error(self, mock_get_db):
        mock_session = Mock()
        mock_get_db.return_value = mock_session

        with patch("main.UIService") as mock_service_class:
            mock_service = Mock()
            mock_service.get_ui_by_date.side_effect = Exception("Service error")
            mock_service_class.return_value = mock_service

            response = client.get("/api/ui/2024-01-01")
            assert response.status_code == 500

    @patch("main.get_db")
    def test_get_ur_by_year_month_service_error(self, mock_get_db):
        mock_session = Mock()
        mock_get_db.return_value = mock_session

        with patch("main.URService") as mock_service_class:
            mock_service = Mock()
            mock_service.get_ur_by_year_month.side_effect = Exception("Service error")
            mock_service_class.return_value = mock_service

            response = client.get("/api/ur/year-month/2024/1")
            assert response.status_code == 500

    def test_get_ui_by_date_invalid_date_format(self):
        response = client.get("/api/ui/invalid-date")
        assert response.status_code == 422

    def test_get_ur_by_year_month_invalid_year(self):
        response = client.get("/api/ur/year-month/invalid/1")
        assert response.status_code == 422

    def test_get_ur_by_year_month_invalid_month(self):
        response = client.get("/api/ur/year-month/2024/invalid")
        assert response.status_code == 422
