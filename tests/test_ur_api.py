"""
Tests para endpoints de UR en la API
"""
import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from datetime import date
from main import app
from models import URValue, URResponse
from services import URService


class TestUREndpoints:
    """Tests para endpoints de UR"""
    
    @pytest.fixture
    def client(self):
        """Cliente de prueba"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_ur_service(self):
        """Mock del servicio UR"""
        with patch('main.URService') as mock:
            yield mock.return_value
    
    def test_get_latest_ur_success(self, client, mock_ur_service):
        """Test obtener último UR exitoso"""
        mock_ur = URValue(year=2024, month=12, value=6.1234)
        mock_ur_service.get_latest_ur.return_value = mock_ur
        
        with patch('main.get_db'):
            response = client.get("/api/ur/latest")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Latest UR value retrieved successfully" in data["message"]
        assert data["data"]["year"] == 2024
        assert data["data"]["month"] == 12
        assert data["data"]["value"] == 6.1234
    
    def test_get_latest_ur_not_found(self, client, mock_ur_service):
        """Test obtener último UR no encontrado"""
        mock_ur_service.get_latest_ur.return_value = None
        
        with patch('main.get_db'):
            response = client.get("/api/ur/latest")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "No UR data available" in data["message"]
        assert data["data"] is None
    
    def test_get_latest_ur_exception(self, client, mock_ur_service):
        """Test excepción en obtener último UR"""
        mock_ur_service.get_latest_ur.side_effect = Exception("Database error")
        
        with patch('main.get_db'):
            response = client.get("/api/ur/latest")
        
        assert response.status_code == 500
    
    def test_get_ur_by_year_month_success(self, client, mock_ur_service):
        """Test obtener UR por año y mes exitoso"""
        mock_ur = URValue(year=2024, month=1, value=5.1234)
        mock_ur_service.get_ur_by_year_month.return_value = mock_ur
        
        with patch('main.get_db'):
            response = client.get("/api/ur/year-month/2024/1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "UR value for 2024-01 retrieved successfully" in data["message"]
        assert data["data"]["year"] == 2024
        assert data["data"]["month"] == 1
        assert data["data"]["value"] == 5.1234
    
    def test_get_ur_by_year_month_not_found(self, client, mock_ur_service):
        """Test obtener UR por año y mes no encontrado"""
        mock_ur_service.get_ur_by_year_month.return_value = None
        
        with patch('main.get_db'):
            response = client.get("/api/ur/year-month/2024/1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "No UR data available for 2024-01" in data["message"]
        assert data["data"] is None
    
    def test_get_ur_by_year_month_invalid_month(self, client, mock_ur_service):
        """Test obtener UR con mes inválido"""
        with patch('main.get_db'):
            response = client.get("/api/ur/year-month/2024/13")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "Month must be between 1 and 12" in data["message"]
    
    def test_get_ur_by_year_month_exception(self, client, mock_ur_service):
        """Test excepción en obtener UR por año y mes"""
        mock_ur_service.get_ur_by_year_month.side_effect = Exception("Database error")
        
        with patch('main.get_db'):
            response = client.get("/api/ur/year-month/2024/1")
        
        assert response.status_code == 500
    
    def test_get_ur_by_year_success(self, client, mock_ur_service):
        """Test obtener UR por año exitoso"""
        mock_ur_1 = URValue(year=2024, month=1, value=5.1234)
        mock_ur_2 = URValue(year=2024, month=2, value=5.2234)
        mock_ur_service.get_ur_by_year.return_value = [mock_ur_1, mock_ur_2]
        
        with patch('main.get_db'):
            response = client.get("/api/ur/year/2024")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Retrieved 2 UR values for year 2024" in data["message"]
        assert len(data["data"]) == 2
        assert data["data"][0]["year"] == 2024
        assert data["data"][0]["month"] == 1
    
    def test_get_ur_by_year_not_found(self, client, mock_ur_service):
        """Test obtener UR por año no encontrado"""
        mock_ur_service.get_ur_by_year.return_value = []
        
        with patch('main.get_db'):
            response = client.get("/api/ur/year/2024")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "No UR data available for year 2024" in data["message"]
        assert data["data"] == []
    
    def test_get_ur_by_year_exception(self, client, mock_ur_service):
        """Test excepción en obtener UR por año"""
        mock_ur_service.get_ur_by_year.side_effect = Exception("Database error")
        
        with patch('main.get_db'):
            response = client.get("/api/ur/year/2024")
        
        assert response.status_code == 500
    
    def test_get_ur_by_range_success(self, client, mock_ur_service):
        """Test obtener UR por rango exitoso"""
        mock_ur_1 = URValue(year=2024, month=1, value=5.1234)
        mock_ur_2 = URValue(year=2024, month=2, value=5.2234)
        mock_ur_service.get_ur_by_range.return_value = [mock_ur_1, mock_ur_2]
        
        with patch('main.get_db'):
            response = client.get("/api/ur/range/2024/1/2024/2")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Retrieved 2 UR values for range 2024-01 to 2024-02" in data["message"]
        assert len(data["data"]) == 2
    
    def test_get_ur_by_range_invalid_months(self, client, mock_ur_service):
        """Test obtener UR por rango con meses inválidos"""
        with patch('main.get_db'):
            response = client.get("/api/ur/range/2024/13/2024/14")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "Month must be between 1 and 12" in data["message"]
    
    def test_get_ur_by_range_invalid_period(self, client, mock_ur_service):
        """Test obtener UR por rango con período inválido"""
        with patch('main.get_db'):
            response = client.get("/api/ur/range/2024/6/2024/1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "Start period must be before or equal to end period" in data["message"]
    
    def test_get_ur_by_range_not_found(self, client, mock_ur_service):
        """Test obtener UR por rango no encontrado"""
        mock_ur_service.get_ur_by_range.return_value = []
        
        with patch('main.get_db'):
            response = client.get("/api/ur/range/2024/1/2024/2")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "No UR data available for range 2024-01 to 2024-02" in data["message"]
    
    def test_get_ur_by_range_exception(self, client, mock_ur_service):
        """Test excepción en obtener UR por rango"""
        mock_ur_service.get_ur_by_range.side_effect = Exception("Database error")
        
        with patch('main.get_db'):
            response = client.get("/api/ur/range/2024/1/2024/2")
        
        assert response.status_code == 500
    
    def test_get_ur_by_range_post(self, client, mock_ur_service):
        """Test obtener UR por rango usando POST"""
        mock_ur_1 = URValue(year=2024, month=1, value=5.1234)
        mock_ur_service.get_ur_by_range.return_value = [mock_ur_1]
        
        request_data = {
            "start_year": 2024,
            "start_month": 1,
            "end_year": 2024,
            "end_month": 1
        }
        
        with patch('main.get_db'):
            response = client.post("/api/ur/range", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_refresh_ur_data_success(self, client):
        """Test actualizar datos UR exitoso"""
        with patch('main.ur_excel_processor') as mock_processor:
            mock_processor.refresh_data.return_value = (True, "Data updated successfully", 410)
            
            with patch('main.URService') as mock_service_class:
                mock_service = mock_service_class.return_value
                mock_service.get_total_records.return_value = 410
                mock_service.get_latest_ur.return_value = URValue(year=2024, month=12, value=6.0)
                
                with patch('main.get_db'):
                    response = client.post("/api/ur/refresh")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["total_records"] == 410
    
    def test_refresh_ur_data_failure(self, client):
        """Test actualizar datos UR fallido"""
        with patch('main.ur_excel_processor') as mock_processor:
            mock_processor.refresh_data.return_value = (False, "Download failed", 0)
            
            with patch('main.URService') as mock_service_class:
                mock_service = mock_service_class.return_value
                mock_service.get_total_records.return_value = 0
                mock_service.get_latest_ur.return_value = None
                
                with patch('main.get_db'):
                    response = client.post("/api/ur/refresh")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert data["total_records"] == 0
    
    def test_refresh_ur_data_exception(self, client):
        """Test excepción en actualizar datos UR"""
        with patch('main.ur_excel_processor') as mock_processor:
            mock_processor.refresh_data.side_effect = Exception("Processing error")
            
            with patch('main.get_db'):
                response = client.post("/api/ur/refresh")
        
        assert response.status_code == 500
    
    def test_get_ur_info_success(self, client):
        """Test obtener información UR exitoso"""
        with patch('main.URService') as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.get_total_records.return_value = 410
            mock_service.get_year_range_available.return_value = (2020, 2024)
            mock_service.get_latest_ur.return_value = URValue(year=2024, month=12, value=6.0)
            mock_service.get_available_years.return_value = [2020, 2021, 2022, 2023, 2024]
            
            with patch('main.get_db'):
                response = client.get("/api/ur/info")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["total_records"] == 410
        assert data["data"]["year_range"]["min_year"] == 2020
        assert data["data"]["year_range"]["max_year"] == 2024
        assert data["data"]["available_years"] == [2020, 2021, 2022, 2023, 2024]
    
    def test_get_ur_info_exception(self, client):
        """Test excepción en obtener información UR"""
        with patch('main.URService') as mock_service_class:
            mock_service_class.side_effect = Exception("Database error")
            
            with patch('main.get_db'):
                response = client.get("/api/ur/info")
        
        assert response.status_code == 500
    
    # Test eliminado - endpoint obsoleto
    
 