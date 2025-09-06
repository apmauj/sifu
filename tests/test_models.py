"""
Tests para modelos de datos
"""

from datetime import date
from models import (
    UIValue,
    UIResponse,
    UIRangeRequest,
    RefreshResponse,
    URValue,
    URResponse,
    URRangeRequest,
)


class TestUIValue:
    """Tests para el modelo UIValue"""

    def test_ui_value_creation(self):
        """Test crear UIValue correctamente"""
        ui_value = UIValue(date=date(2024, 1, 1), value=5.1234)
        assert ui_value.date == date(2024, 1, 1)
        assert ui_value.value == 5.1234

    def test_ui_value_dict(self):
        """Test conversión a diccionario"""
        ui_value = UIValue(date=date(2024, 1, 1), value=5.1234)
        result = ui_value.dict()
        assert result["date"] == "2024-01-01"
        assert result["value"] == 5.1234

    def test_ui_value_dict_with_string_date(self):
        """Test conversión a diccionario con fecha como string"""
        ui_value = UIValue(date="2024-01-01", value=5.1234)
        result = ui_value.dict()
        assert result["date"] == "2024-01-01"
        assert result["value"] == 5.1234


class TestURValue:
    """Tests para el modelo URValue"""

    def test_ur_value_creation(self):
        """Test crear URValue correctamente"""
        ur_value = URValue(year=2024, month=1, value=5.1234)
        assert ur_value.year == 2024
        assert ur_value.month == 1
        assert ur_value.value == 5.1234

    def test_ur_value_dict(self):
        """Test conversión a diccionario"""
        ur_value = URValue(year=2024, month=1, value=5.1234)
        result = ur_value.dict()
        assert result["year"] == 2024
        assert result["month"] == 1
        assert result["value"] == 5.1234


class TestUIResponse:
    """Tests para el modelo UIResponse"""

    def test_ui_response_success(self):
        """Test respuesta exitosa"""
        ui_value = UIValue(date=date(2024, 1, 1), value=5.1234)
        response = UIResponse(success=True, message="Value retrieved", data=ui_value)
        assert response.success is True
        assert response.message == "Value retrieved"
        assert response.data.value == 5.1234

    def test_ui_response_error(self):
        """Test respuesta de error"""
        response = UIResponse(success=False, message="Error", data=None)
        assert response.success is False
        assert response.message == "Error"
        assert response.data is None

    def test_ui_response_dict(self):
        """Test conversión a diccionario"""
        response = UIResponse(success=True, message="Success", data={"test": "data"})
        result = response.dict()
        assert result["success"] is True
        assert result["message"] == "Success"
        assert result["data"] == {"test": "data"}


class TestURResponse:
    """Tests para el modelo URResponse"""

    def test_ur_response_success(self):
        """Test respuesta exitosa"""
        ur_value = URValue(year=2024, month=1, value=5.1234)
        response = URResponse(success=True, message="Value retrieved", data=ur_value)
        assert response.success is True
        assert response.message == "Value retrieved"
        assert response.data.value == 5.1234

    def test_ur_response_dict(self):
        """Test conversión a diccionario"""
        response = URResponse(success=True, message="Success", data={"test": "data"})
        result = response.dict()
        assert result["success"] is True
        assert result["message"] == "Success"
        assert result["data"] == {"test": "data"}


class TestUIRangeRequest:
    """Tests para el modelo UIRangeRequest"""

    def test_ui_range_creation(self):
        """Test crear UIRangeRequest correctamente"""
        ui_range = UIRangeRequest(
            start_date=date(2024, 1, 1), end_date=date(2024, 1, 31)
        )
        assert ui_range.start_date == date(2024, 1, 1)
        assert ui_range.end_date == date(2024, 1, 31)

    def test_ui_range_validation(self):
        """Test validación de fechas"""
        # Fecha fin antes que inicio debería ser válida en el modelo
        # La validación se hace en el servicio
        ui_range = UIRangeRequest(
            start_date=date(2024, 1, 31), end_date=date(2024, 1, 1)
        )
        assert ui_range.start_date == date(2024, 1, 31)
        assert ui_range.end_date == date(2024, 1, 1)


class TestURRangeRequest:
    """Tests para el modelo URRangeRequest"""

    def test_ur_range_creation(self):
        """Test crear URRangeRequest correctamente"""
        ur_range = URRangeRequest(
            start_year=2024, start_month=1, end_year=2024, end_month=12
        )
        assert ur_range.start_year == 2024
        assert ur_range.start_month == 1
        assert ur_range.end_year == 2024
        assert ur_range.end_month == 12

    def test_ur_range_defaults(self):
        """Test valores por defecto"""
        ur_range = URRangeRequest(start_year=2024)
        assert ur_range.start_year == 2024
        assert ur_range.start_month == 1
        assert ur_range.end_year == 2024
        assert ur_range.end_month == 12


class TestRefreshResponse:
    """Tests para el modelo RefreshResponse"""

    def test_refresh_response_success(self):
        """Test respuesta de refresh exitosa"""
        response = RefreshResponse(
            success=True,
            message="Database updated",
            total_records=8436,
            last_updated=date(2024, 12, 1),
        )
        assert response.success is True
        assert response.message == "Database updated"
        assert response.total_records == 8436
        assert response.last_updated == date(2024, 12, 1)

    def test_refresh_response_dict(self):
        """Test conversión a diccionario"""
        response = RefreshResponse(
            success=True,
            message="Success",
            total_records=100,
            last_updated=date(2024, 1, 1),
        )
        result = response.dict()
        assert result["success"] is True
        assert result["message"] == "Success"
        assert result["total_records"] == 100
        assert result["last_updated"] == "2024-01-01"

    def test_refresh_response_dict_no_date(self):
        """Test conversión a diccionario sin fecha"""
        response = RefreshResponse(
            success=True, message="Success", total_records=100, last_updated=None
        )
        result = response.dict()
        assert result["last_updated"] is None
