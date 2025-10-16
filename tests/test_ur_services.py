"""
Tests para servicios de UR
"""

from unittest.mock import Mock
from src.domain.services import URService


class TestURService:
    """Tests para URService"""

    def setup_method(self):
        """Setup para cada test"""
        self.mock_session = Mock()
        self.service = URService(self.mock_session)

    def test_get_ur_by_year_month_success(self):
        """Test obtener UR por año y mes exitoso"""
        mock_ur = Mock()
        mock_ur.year = 2024
        mock_ur.month = 1
        mock_ur.value = 5.1234
        self.mock_session.query().filter().first.return_value = mock_ur

        result = self.service.get_ur_by_year_month(2024, 1)

        assert result is not None
        assert result.year == 2024
        assert result.month == 1
        assert result.value == 5.1234

    def test_get_ur_by_year_month_not_found(self):
        """Test UR no encontrada por año y mes"""
        self.mock_session.query().filter().first.return_value = None

        result = self.service.get_ur_by_year_month(2024, 1)

        assert result is None

    def test_get_ur_by_year_month_exception(self):
        """Test excepción en get_ur_by_year_month"""
        self.mock_session.query.side_effect = Exception("Database error")

        result = self.service.get_ur_by_year_month(2024, 1)

        assert result is None

    def test_get_ur_by_year_success(self):
        """Test obtener UR por año exitoso"""
        mock_ur_1 = Mock()
        mock_ur_1.year = 2024
        mock_ur_1.month = 1
        mock_ur_1.value = 5.1234

        mock_ur_2 = Mock()
        mock_ur_2.year = 2024
        mock_ur_2.month = 2
        mock_ur_2.value = 5.2234

        self.mock_session.query().filter().order_by().all.return_value = [
            mock_ur_1,
            mock_ur_2,
        ]

        result = self.service.get_ur_by_year(2024)

        assert len(result) == 2
        assert result[0].year == 2024
        assert result[0].month == 1
        assert result[1].month == 2

    def test_get_ur_by_year_empty(self):
        """Test obtener UR por año vacío"""
        self.mock_session.query().filter().order_by().all.return_value = []

        result = self.service.get_ur_by_year(2024)

        assert len(result) == 0

    def test_get_ur_by_year_exception(self):
        """Test excepción en get_ur_by_year"""
        self.mock_session.query.side_effect = Exception("Database error")

        result = self.service.get_ur_by_year(2024)

        assert result == []

    def test_get_latest_ur_success(self):
        """Test obtener último UR exitoso"""
        mock_ur = Mock()
        mock_ur.year = 2024
        mock_ur.month = 12
        mock_ur.value = 6.0000

        self.mock_session.query().order_by().first.return_value = mock_ur

        result = self.service.get_latest_ur()

        assert result is not None
        assert result.year == 2024
        assert result.month == 12
        assert result.value == 6.0000

    def test_get_latest_ur_empty_db(self):
        """Test obtener último UR con DB vacía"""
        self.mock_session.query().order_by().first.return_value = None

        result = self.service.get_latest_ur()

        assert result is None

    def test_get_ur_by_range_success(self):
        """Test obtener UR por rango exitoso"""
        mock_ur_1 = Mock()
        mock_ur_1.year = 2024
        mock_ur_1.month = 1
        mock_ur_1.value = 5.1234

        mock_ur_2 = Mock()
        mock_ur_2.year = 2024
        mock_ur_2.month = 2
        mock_ur_2.value = 5.2234

        self.mock_session.query().filter().order_by().all.return_value = [
            mock_ur_1,
            mock_ur_2,
        ]

        result = self.service.get_ur_by_range(2024, 1, 2024, 2)

        assert len(result) == 2
        assert result[0].year == 2024
        assert result[0].month == 1
        assert result[1].month == 2

    def test_get_ur_by_range_empty(self):
        """Test obtener UR por rango vacío"""
        self.mock_session.query().filter().order_by().all.return_value = []

        result = self.service.get_ur_by_range(2024, 1, 2024, 12)

        assert len(result) == 0

    def test_get_ur_by_range_exception(self):
        """Test excepción en get_ur_by_range"""
        self.mock_session.query.side_effect = Exception("Database error")

        result = self.service.get_ur_by_range(2024, 1, 2024, 12)

        assert result == []

    def test_get_total_records(self):
        """Test obtener total de registros UR"""
        self.mock_session.query().count.return_value = 410

        result = self.service.get_total_records()

        assert result == 410

    def test_get_year_range_available(self):
        """Test obtener rango de años disponible"""
        self.mock_session.query().order_by().first.side_effect = [
            (2020,),  # min_year
            (2024,),  # max_year
        ]

        min_year, max_year = self.service.get_year_range_available()

        assert min_year == 2020
        assert max_year == 2024

    def test_get_available_years(self):
        """Test obtener años disponibles"""
        mock_years = [(2020,), (2021,), (2022,), (2023,), (2024,)]
        self.mock_session.query().distinct().order_by().all.return_value = mock_years

        result = self.service.get_available_years()

        assert result == [2020, 2021, 2022, 2023, 2024]

    def test_get_available_years_exception(self):
        """Test excepción en get_available_years"""
        self.mock_session.query.side_effect = Exception("Database error")

        result = self.service.get_available_years()

        assert result == []

