from unittest.mock import Mock
from datetime import date
from services import UIService, URService, ExchangeRateService

class TestUIServiceEdgeCases:
    def test_get_ui_by_date_database_error(self):
        mock_db = Mock()
        mock_db.query.side_effect = Exception("Database error")
        service = UIService(mock_db)
        result = service.get_ui_by_date(date(2024, 1, 1))
        assert result is None

class TestURServiceEdgeCases:
    def test_get_ur_by_year_month_database_error(self):
        mock_db = Mock()
        mock_db.query.side_effect = Exception("Database error")
        service = URService(mock_db)
        result = service.get_ur_by_year_month(2024, 1)
        assert result is None

class TestExchangeRateServiceEdgeCases:
    def test_get_exchange_rate_by_date_database_error(self):
        mock_db = Mock()
        mock_db.query.side_effect = Exception("Database error")
        service = ExchangeRateService(mock_db)
        result = service.get_exchange_rate_by_date(date(2024, 1, 1))
        assert result == []
