"""
Tests para servicios de negocio
"""
import pytest
from unittest.mock import Mock
from datetime import date
from services import UIService
from models import UIValue


class TestUIService:
    """Tests para UIService"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.mock_session = Mock()
        self.service = UIService(self.mock_session)
    
    def test_get_ui_by_date_success(self):
        """Test obtener UI por fecha exitoso"""
        mock_ui = Mock()
        mock_ui.date = date(2024, 1, 1)
        mock_ui.value = 5.1234
        self.mock_session.query().filter().first.return_value = mock_ui
        result = self.service.get_ui_by_date(date(2024, 1, 1))
        assert result is not None
        assert result.date == date(2024, 1, 1)
        assert result.value == 5.1234
    
    def test_get_ui_by_date_not_found(self):
        """Test UI no encontrada por fecha"""
        self.mock_session.query().filter().first.return_value = None
        result = self.service.get_ui_by_date(date(2024, 1, 1))
        assert result is None

    def test_get_ui_by_date_exception(self):
        """Test excepción en get_ui_by_date"""
        self.mock_session.query.side_effect = Exception("Database error")
        result = self.service.get_ui_by_date(date(2024, 1, 1))
        assert result is None
    
    def test_get_latest_ui_success(self):
        """Test obtener último UI exitoso"""
        mock_ui = Mock()
        mock_ui.date = date(2024, 12, 1)
        mock_ui.value = 6.0000
        self.mock_session.query().order_by().first.return_value = mock_ui
        result = self.service.get_latest_ui()
        assert result is not None
        assert result.date == date(2024, 12, 1)
        assert result.value == 6.0000
    
    def test_get_latest_ui_empty_db(self):
        """Test obtener último UI con DB vacía"""
        self.mock_session.query().order_by().first.return_value = None
        result = self.service.get_latest_ui()
        assert result is None

    def test_get_latest_ui_exception(self):
        """Test excepción en get_latest_ui"""
        self.mock_session.query.side_effect = Exception("Database error")
        result = self.service.get_latest_ui()
        assert result is None
    
    def test_get_ui_by_date_range_success(self):
        """Test obtener rango de UI exitoso"""
        mock_ui_1 = Mock()
        mock_ui_1.date = date(2024, 1, 1)
        mock_ui_1.value = 5.0000
        mock_ui_2 = Mock()
        mock_ui_2.date = date(2024, 1, 2)
        mock_ui_2.value = 5.0100
        self.mock_session.query().filter().order_by().all.return_value = [mock_ui_1, mock_ui_2]
        result = self.service.get_ui_by_date_range(date(2024, 1, 1), date(2024, 1, 2))
        assert len(result) == 2
        assert result[0].date == date(2024, 1, 1)
        assert result[1].date == date(2024, 1, 2)
    
    def test_get_ui_by_date_range_empty(self):
        """Test obtener rango de UI vacío"""
        self.mock_session.query().filter().order_by().all.return_value = []
        result = self.service.get_ui_by_date_range(date(2024, 1, 1), date(2024, 1, 2))
        assert len(result) == 0

    def test_get_ui_by_date_range_exception(self):
        """Test excepción en get_ui_by_date_range"""
        self.mock_session.query.side_effect = Exception("Database error")
        result = self.service.get_ui_by_date_range(date(2024, 1, 1), date(2024, 1, 2))
        assert result == []
    
    def test_get_total_records(self):
        """Test obtener total de registros"""
        self.mock_session.query().count.return_value = 100
        result = self.service.get_total_records()
        assert result == 100

    def test_get_total_records_exception(self):
        """Test excepción en get_total_records"""
        self.mock_session.query.side_effect = Exception("Database error")
        result = self.service.get_total_records()
        assert result == 0
    
    def test_get_date_range_available(self):
        """Test obtener rango de fechas disponible"""
        self.mock_session.query().order_by().first.side_effect = [ (date(2002, 6, 1),), (date(2024, 12, 1),) ]
        min_date, max_date = self.service.get_date_range_available()
        assert min_date == date(2002, 6, 1)
        assert max_date == date(2024, 12, 1)

    def test_get_date_range_available_exception(self):
        """Test excepción en get_date_range_available"""
        self.mock_session.query.side_effect = Exception("Database error")
        min_date, max_date = self.service.get_date_range_available()
        assert min_date is None
        assert max_date is None

    def test_get_ui_closest_to_date_success(self):
        """Test obtener UI más cercana a fecha exitoso"""
        mock_ui = Mock()
        mock_ui.date = date(2024, 1, 1)
        mock_ui.value = 5.1234
        # Simular que no encuentra fecha exacta, pero sí encuentra fecha cercana
        self.mock_session.query().filter().first.return_value = None
        self.mock_session.query().filter().order_by().first.return_value = mock_ui
        result = self.service.get_ui_closest_to_date(date(2024, 1, 5))
        assert result is not None
        assert result.date == date(2024, 1, 1)
        assert result.value == 5.1234

    def test_get_ui_closest_to_date_not_found(self):
        """Test UI más cercana no encontrada"""
        # Simular que no se encuentra registro exacto ni cercano
        self.mock_session.query().filter().first.return_value = None
        self.mock_session.query().filter().order_by().first.return_value = None
        result = self.service.get_ui_closest_to_date(date(2024, 1, 1))
        assert result is None

    def test_get_ui_closest_to_date_exception(self):
        """Test excepción en get_ui_closest_to_date"""
        self.mock_session.query.side_effect = Exception("Database error")
        result = self.service.get_ui_closest_to_date(date(2024, 1, 1))
        assert result is None

    def test_get_ui_closest_to_date_exact_match_found(self):
        """Test get_ui_closest_to_date when exact date match is found (line 65)"""
        mock_ui = Mock()
        mock_ui.date = date(2024, 1, 1)
        mock_ui.value = 5.1234
        
        # Mock to find exact date in first query
        self.mock_session.query().filter().first.return_value = mock_ui
        
        result = self.service.get_ui_closest_to_date(date(2024, 1, 1))
        
        assert result is not None
        assert result.date == date(2024, 1, 1)
        assert result.value == 5.1234


class TestURServiceCoverage:
    """Tests for URService to improve coverage"""
    
    def setup_method(self):
        """Setup for each test"""
        from services import URService
        self.mock_session = Mock()
        self.service = URService(self.mock_session)
    
    def test_get_ur_by_range_multi_year_complex(self):
        """Test UR range with multiple years (complex case)"""
        # Mock for 3-year range: 2020-06 to 2023-08
        mock_records = [
            Mock(year=2020, month=6, value=5.1),
            Mock(year=2020, month=12, value=5.2),
            Mock(year=2021, month=1, value=5.3),
            Mock(year=2021, month=12, value=5.4),
            Mock(year=2022, month=1, value=5.5),
            Mock(year=2022, month=12, value=5.6),
            Mock(year=2023, month=1, value=5.7),
            Mock(year=2023, month=8, value=5.8),
        ]
        
        mock_query = Mock()
        mock_query.filter.return_value.order_by.return_value.all.return_value = mock_records
        self.mock_session.query.return_value = mock_query
        
        result = self.service.get_ur_by_range(2020, 6, 2023, 8)
        
        assert len(result) == 8
        assert result[0].year == 2020
        assert result[0].month == 6
        assert result[-1].year == 2023
        assert result[-1].month == 8

    def test_get_ur_by_range_two_year_span(self):
        """Test UR range with exactly 2 years"""
        # Mock for 2-year range: 2022-03 to 2023-09
        mock_records = [
            Mock(year=2022, month=3, value=5.1),
            Mock(year=2022, month=12, value=5.2),
            Mock(year=2023, month=1, value=5.3),
            Mock(year=2023, month=9, value=5.4),
        ]
        
        mock_query = Mock()
        mock_query.filter.return_value.order_by.return_value.all.return_value = mock_records
        self.mock_session.query.return_value = mock_query
        
        result = self.service.get_ur_by_range(2022, 3, 2023, 9)
        
        assert len(result) == 4
        assert result[0].year == 2022
        assert result[0].month == 3
        assert result[-1].year == 2023
        assert result[-1].month == 9

    def test_get_ur_by_range_exception(self):
        """Test exception in get_ur_by_range"""
        self.mock_session.query.side_effect = Exception("Database error")
        
        result = self.service.get_ur_by_range(2020, 1, 2022, 12)
        
        assert result == []

    def test_get_latest_ur_exception(self):
        """Test exception in get_latest_ur"""
        self.mock_session.query.side_effect = Exception("Database error")
        
        result = self.service.get_latest_ur()
        
        assert result is None

    def test_get_total_records_exception(self):
        """Test exception in get_total_records"""
        self.mock_session.query.side_effect = Exception("Database error")
        
        result = self.service.get_total_records()
        
        assert result == 0

    def test_get_year_range_available_exception(self):
        """Test exception in get_year_range_available"""
        self.mock_session.query.side_effect = Exception("Database error")
        
        result = self.service.get_year_range_available()
        
        assert result == (None, None)

    def test_get_available_years_exception(self):
        """Test exception in get_available_years"""
        self.mock_session.query.side_effect = Exception("Database error")
        
        result = self.service.get_available_years()
        
        assert result == []

    def test_get_ur_by_year_month_exception(self):
        """Test exception in get_ur_by_year_month"""
        self.mock_session.query.side_effect = Exception("Database error")
        
        result = self.service.get_ur_by_year_month(2024, 1)
        
        assert result is None

    def test_get_ur_by_year_exception(self):
        """Test exception in get_ur_by_year"""
        self.mock_session.query.side_effect = Exception("Database error")
        
        result = self.service.get_ur_by_year(2024)
        
        assert result == [] 