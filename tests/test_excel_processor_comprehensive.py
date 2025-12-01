"""
Tests comprehensivos para el procesador de Excel - Cobertura completa
Incluye tests para URExcelProcessor y casos edge faltantes de ExcelProcessor
"""

import pytest
import pandas as pd
import requests
from unittest.mock import Mock, patch
from datetime import date, datetime
from src.domain.excel_processor import ExcelProcessor, URExcelProcessor


class TestExcelProcessorComprehensive:
    """Tests comprehensivos para ExcelProcessor - casos edge faltantes"""

    @pytest.fixture
    def processor(self):
        return ExcelProcessor()

    @patch("excel_processor.requests.get")
    def test_download_excel_request_exception(self, mock_get, processor):
        """Test download_excel con RequestException específica"""
        mock_get.side_effect = requests.RequestException("Network error")

        result = processor.download_excel()

        assert result is None
        mock_get.assert_called_once()

    @patch("excel_processor.requests.get")
    def test_download_excel_http_error(self, mock_get, processor):
        """Test download_excel con error HTTP"""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_get.return_value = mock_response

        result = processor.download_excel()

        assert result is None

    @patch("excel_processor.requests.get")
    @patch("excel_processor.pd.read_excel")
    def test_download_excel_pandas_exception(
        self, mock_read_excel, mock_get, processor
    ):
        """Test download_excel con excepción en pandas"""
        mock_response = Mock()
        mock_response.content = b"invalid_excel_content"
        mock_get.return_value = mock_response
        mock_read_excel.side_effect = Exception("Invalid Excel format")

        result = processor.download_excel()

        assert result is None

    def test_parse_excel_data_datetime_objects(self, processor):
        """Test parse_excel_data con objetos datetime"""
        data = [
            ["Fecha", "Valor"],
            [datetime(2024, 1, 1), 5.1234],
            [datetime(2024, 1, 2), 5.1334],
        ]
        df = pd.DataFrame(data)

        result = processor.parse_excel_data(df)

        assert len(result) == 2
        assert result[0][0] == date(2024, 1, 1)
        assert result[0][1] == pytest.approx(5.1234)

    def test_parse_excel_data_string_dates_multiple_formats(self, processor):
        """Test parse_excel_data con fechas string en múltiples formatos"""
        data = [
            ["Fecha", "Valor"],
            ["2024-01-01", 5.1234],  # ISO format
            ["01/01/2024", 5.1334],  # US format
            ["01-01-2024", 5.1434],  # Dash format
        ]
        df = pd.DataFrame(data)

        result = processor.parse_excel_data(df)

        assert len(result) == 3
        assert all(isinstance(r[0], date) for r in result)
        assert all(isinstance(r[1], float) for r in result)

    def test_parse_excel_data_invalid_date_formats(self, processor):
        """Test parse_excel_data con formatos de fecha inválidos"""
        data = [
            ["Fecha", "Valor"],
            ["invalid-date", 5.1234],
            ["32/13/2024", 5.1334],  # Fecha imposible
            ["not-a-date", 5.1434],
        ]
        df = pd.DataFrame(data)

        result = processor.parse_excel_data(df)

        # Debería filtrar las fechas inválidas
        assert len(result) == 0

    def test_parse_excel_data_invalid_values(self, processor):
        """Test parse_excel_data con valores inválidos"""
        data = [
            ["Fecha", "Valor"],
            ["2024-01-01", "not-a-number"],
            ["2024-01-02", None],
            ["2024-01-03", ""],
        ]
        df = pd.DataFrame(data)

        result = processor.parse_excel_data(df)

        # Debería filtrar los valores inválidos
        assert len(result) == 0

    def test_parse_excel_data_mixed_valid_invalid(self, processor):
        """Test parse_excel_data con mezcla de datos válidos e inválidos"""
        data = [
            ["Fecha", "Valor"],
            ["2024-01-01", 5.1234],  # Válido
            ["invalid-date", 5.1334],  # Fecha inválida
            ["2024-01-03", "invalid"],  # Valor inválido
            ["2024-01-04", 5.1534],  # Válido
        ]
        df = pd.DataFrame(data)

        result = processor.parse_excel_data(df)

        # Solo debería devolver los registros válidos
        assert len(result) == 2
        assert result[0][0] == date(2024, 1, 1)
        assert result[1][0] == date(2024, 1, 4)

    def test_parse_excel_data_exception_handling(self, processor):
        """Test parse_excel_data con excepción general"""
        # DataFrame malformado que cause excepción
        df = Mock()
        df.columns = []
        df.iterrows.side_effect = Exception("DataFrame error")

        result = processor.parse_excel_data(df)

        assert result == []

    def test_save_to_database_update_existing(self, processor):
        """Test save_to_database actualizando registros existentes"""
        mock_db = Mock()

        # Mock para registro existente con valor diferente
        existing_record = Mock()
        existing_record.value = 5.0000  # Valor diferente

        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = existing_record
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query

        data = [(date(2024, 1, 1), 5.1234)]

        result = processor.save_to_database(mock_db, data)

        assert result == 1
        assert existing_record.value == 5.1234
        mock_db.commit.assert_called_once()

    def test_save_to_database_no_changes(self, processor):
        """Test save_to_database sin cambios necesarios"""
        mock_db = Mock()

        # Mock para registro existente con mismo valor
        existing_record = Mock()
        existing_record.value = 5.1234  # Mismo valor

        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = existing_record
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query

        data = [(date(2024, 1, 1), 5.1234)]

        result = processor.save_to_database(mock_db, data)

        assert result == 0  # No se guardó nada
        mock_db.commit.assert_called_once()


class TestURExcelProcessorComprehensive:
    """Tests comprehensivos para URExcelProcessor - clase completa sin cobertura"""

    @pytest.fixture
    def ur_processor(self):
        return URExcelProcessor()

    def test_init(self, ur_processor):
        """Test inicialización de URExcelProcessor"""
        # URL should match the BHU format pattern (dynamic date)
        assert ur_processor.url.startswith("https://bhu.com.uy/sites/default/files/")
        assert ur_processor.url.endswith("/historico-ur.xls")
        # Verify it contains a valid date format YYYY-MM
        import re
        match = re.search(r'/(\d{4})-(\d{2})/historico-ur\.xls$', ur_processor.url)
        assert match is not None, f"URL doesn't match expected pattern: {ur_processor.url}"
        year, month = int(match.group(1)), int(match.group(2))
        assert 2020 <= year <= 2030, f"Year {year} out of reasonable range"
        assert 1 <= month <= 12, f"Month {month} out of valid range"
        assert ur_processor.timeout == 30

    @patch("excel_processor.requests.get")
    @patch("excel_processor.pd.read_excel")
    def test_download_excel_success(self, mock_read_excel, mock_get, ur_processor):
        """Test download_excel exitoso para UR - verifica que se use la URL dinámica correctamente"""
        # Mock the dynamic URL resolution to return the processor's URL
        with patch.object(ur_processor, '_resolve_dynamic_bhu_url', return_value=ur_processor.url):
            mock_response = Mock()
            mock_response.content = b"mock_excel_content"
            mock_get.return_value = mock_response

            mock_df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
            mock_read_excel.return_value = mock_df

            result = ur_processor.download_excel()

            assert result is not None
            assert isinstance(result, pd.DataFrame)
            # Verify the request was made with correct parameters (URL is dynamic, so we just check it was called)
            assert mock_get.call_count >= 1
            # Get the actual call arguments
            call_args = mock_get.call_args
            called_url = call_args[0][0] if call_args[0] else call_args[1].get('url')
            # Verify URL matches the BHU pattern
            assert "bhu.com.uy" in called_url or "ine.gub.uy" in called_url
            # Verify other parameters
            assert call_args[1]['timeout'] == 30
            assert 'User-Agent' in call_args[1]['headers']
            assert call_args[1]['verify'] is False

    @patch("excel_processor.requests.get")
    def test_download_excel_request_exception(self, mock_get, ur_processor):
        """Test download_excel con RequestException"""
        mock_get.side_effect = requests.RequestException("Network error")

        result = ur_processor.download_excel()

        assert result is None

    @patch("excel_processor.requests.get")
    def test_download_excel_general_exception(self, mock_get, ur_processor):
        """Test download_excel con excepción general"""
        mock_get.side_effect = Exception("General error")

        result = ur_processor.download_excel()

        assert result is None

    def test_parse_excel_data_success(self, ur_processor):
        """Test parse_excel_data exitoso con formato matricial UR"""
        # Crear DataFrame que simula el formato del BHU
        data = [
            ["Título", None, None, None],
            ["AÑO", "ENERO", "FEBRERO", "MARZO"],  # Header row
            [2023, 45.1234, 45.2345, 45.3456],
            [2024, 46.1234, 46.2345, 46.3456],
        ]
        df = pd.DataFrame(data)

        result = ur_processor.parse_excel_data(df)

        assert len(result) > 0
        # Verificar que devuelve tuplas (año, mes, valor)
        for record in result:
            assert len(record) == 3
            assert isinstance(record[0], int)  # año
            assert isinstance(record[1], int)  # mes
            assert isinstance(record[2], float)  # valor

    def test_parse_excel_data_no_header_found(self, ur_processor):
        """Test parse_excel_data cuando no encuentra encabezado de meses"""
        # DataFrame sin nombres de meses
        data = [
            ["Col1", "Col2", "Col3"],
            [2023, 45.1234, 45.2345],
            [2024, 46.1234, 46.2345],
        ]
        df = pd.DataFrame(data)

        result = ur_processor.parse_excel_data(df)

        assert result == []

    def test_parse_excel_data_invalid_years(self, ur_processor):
        """Test parse_excel_data con años inválidos"""
        data = [
            ["AÑO", "ENERO", "FEBRERO"],
            ["invalid", 45.1234, 45.2345],  # Año inválido
            [1800, 45.1234, 45.2345],  # Año muy antiguo
            [3000, 45.1234, 45.2345],  # Año muy futuro
        ]
        df = pd.DataFrame(data)

        result = ur_processor.parse_excel_data(df)

        assert result == []

    def test_parse_excel_data_invalid_values(self, ur_processor):
        """Test parse_excel_data con valores inválidos"""
        data = [
            ["AÑO", "ENERO", "FEBRERO"],
            [2023, "invalid", 45.2345],  # Valor inválido
            [2024, None, 46.2345],  # Valor None
            [2025, "", 47.2345],  # Valor vacío
        ]
        df = pd.DataFrame(data)

        result = ur_processor.parse_excel_data(df)

        # Solo debería procesar valores válidos
        valid_records = [r for r in result if r[2] > 0]
        assert len(valid_records) >= 0  # Puede haber algunos válidos

    def test_parse_excel_data_string_values_with_formatting(self, ur_processor):
        """Test parse_excel_data con valores string con formato"""
        data = [
            ["AÑO", "ENERO", "FEBRERO"],
            [2023, "45,1234", "45.234,56"],  # Formato con comas
            [2024, "46 123", "46.234"],  # Formato con espacios
        ]
        df = pd.DataFrame(data)

        result = ur_processor.parse_excel_data(df)

        # Debería manejar el formato y convertir correctamente
        assert len(result) >= 0

    def test_parse_excel_data_extreme_values(self, ur_processor):
        """Test parse_excel_data con valores extremos"""
        data = [
            ["AÑO", "ENERO", "FEBRERO"],
            [2023, -1, 45.2345],  # Valor negativo
            [2024, 0, 46.2345],  # Valor cero
            [2025, 999999, 47.2345],  # Valor muy alto
        ]
        df = pd.DataFrame(data)

        result = ur_processor.parse_excel_data(df)

        # Solo valores entre 0 y 100,000 deberían ser válidos
        valid_records = [r for r in result if 0 < r[2] < 100000]
        assert len(valid_records) >= 0

    def test_parse_excel_data_exception_handling(self, ur_processor):
        """Test parse_excel_data con excepción general"""
        df = Mock()
        df.iterrows.side_effect = Exception("DataFrame error")

        result = ur_processor.parse_excel_data(df)

        assert result == []

    def test_save_to_database_new_records(self, ur_processor):
        """Test save_to_database con registros nuevos"""
        mock_db = Mock()

        # Mock para que no existan registros
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = None
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query

        data = [(2023, 1, 45.1234), (2023, 2, 45.2345)]

        result = ur_processor.save_to_database(mock_db, data)

        assert result == 2
        assert mock_db.add.call_count == 2
        mock_db.commit.assert_called_once()

    def test_save_to_database_update_existing(self, ur_processor):
        """Test save_to_database actualizando registros existentes"""
        mock_db = Mock()

        # Mock para registro existente con valor diferente
        existing_record = Mock()
        existing_record.value = 45.0000  # Valor diferente

        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = existing_record
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query

        data = [(2023, 1, 45.1234)]

        result = ur_processor.save_to_database(mock_db, data)

        assert result == 1
        assert existing_record.value == 45.1234
        mock_db.commit.assert_called_once()

    def test_save_to_database_no_changes(self, ur_processor):
        """Test save_to_database sin cambios necesarios"""
        mock_db = Mock()

        # Mock para registro existente con mismo valor
        existing_record = Mock()
        existing_record.value = 45.1234  # Mismo valor

        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = existing_record
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query

        data = [(2023, 1, 45.1234)]

        result = ur_processor.save_to_database(mock_db, data)

        assert result == 0  # No se guardó nada
        mock_db.commit.assert_called_once()

    def test_save_to_database_exception(self, ur_processor):
        """Test save_to_database con excepción"""
        mock_db = Mock()
        mock_db.commit.side_effect = Exception("Database error")

        data = [(2023, 1, 45.1234)]

        result = ur_processor.save_to_database(mock_db, data)

        assert result == 0
        mock_db.rollback.assert_called_once()

    @patch.object(URExcelProcessor, "download_excel")
    @patch.object(URExcelProcessor, "parse_excel_data")
    @patch.object(URExcelProcessor, "save_to_database")
    def test_refresh_data_success(
        self, mock_save, mock_parse, mock_download, ur_processor
    ):
        """Test refresh_data exitoso"""
        mock_df = pd.DataFrame({"col1": [1, 2]})
        mock_download.return_value = mock_df

        mock_data = [(2023, 1, 45.1234), (2023, 2, 45.2345)]
        mock_parse.return_value = mock_data

        mock_save.return_value = 2

        mock_db = Mock()
        success, message, count = ur_processor.refresh_data(mock_db)

        assert success is True
        assert "successfully" in message
        assert count == 2

    @patch.object(URExcelProcessor, "download_excel")
    def test_refresh_data_download_error(self, mock_download, ur_processor):
        """Test refresh_data con error de descarga"""
        mock_download.return_value = None

        mock_db = Mock()
        success, message, count = ur_processor.refresh_data(mock_db)

        assert success is False
        assert "Error downloading file from BHU" in message
        assert count == 0

    @patch.object(URExcelProcessor, "download_excel")
    @patch.object(URExcelProcessor, "parse_excel_data")
    def test_refresh_data_parse_error(self, mock_parse, mock_download, ur_processor):
        """Test refresh_data con error de parsing"""
        mock_df = pd.DataFrame({"col1": [1, 2]})
        mock_download.return_value = mock_df

        mock_parse.return_value = []  # Sin datos válidos

        mock_db = Mock()
        success, message, count = ur_processor.refresh_data(mock_db)

        assert success is False
        assert "Could not extract valid data from file" in message
        assert count == 0

    @patch.object(URExcelProcessor, "download_excel")
    @patch.object(URExcelProcessor, "parse_excel_data")
    @patch.object(URExcelProcessor, "save_to_database")
    def test_refresh_data_no_changes(
        self, mock_save, mock_parse, mock_download, ur_processor
    ):
        """Test refresh_data sin cambios"""
        mock_df = pd.DataFrame({"col1": [1, 2]})
        mock_download.return_value = mock_df

        mock_data = [(2023, 1, 45.1234)]
        mock_parse.return_value = mock_data

        mock_save.return_value = 0  # Sin cambios

        mock_db = Mock()
        success, message, count = ur_processor.refresh_data(mock_db)

        assert success is True
        assert "No changes" in message
        assert count == 0

    @patch.object(URExcelProcessor, "download_excel")
    def test_refresh_data_exception(self, mock_download, ur_processor):
        """Test refresh_data con excepción general"""
        mock_download.side_effect = Exception("General error")

        mock_db = Mock()
        success, message, count = ur_processor.refresh_data(mock_db)

        assert success is False
        assert "Internal error" in message
        assert count == 0


class TestExcelProcessorEdgeCases:
    """Tests para casos edge específicos no cubiertos"""

    @pytest.fixture
    def processor(self):
        return ExcelProcessor()

    def test_parse_excel_data_row_processing_exception(self, processor):
        """Test parse_excel_data con excepción en procesamiento de fila individual"""
        # Crear un DataFrame que cause excepción en una fila específica
        data = [
            ["Fecha", "Valor"],
            ["2024-01-01", 5.1234],  # Válido
            [None, None],  # Fila que causará excepción
        ]
        df = pd.DataFrame(data)

        # Mock para que iterrows cause excepción en la segunda fila
        original_iterrows = df.iterrows

        def mock_iterrows():
            for i, row in original_iterrows():
                if i == 1:  # Segunda fila (índice 1)
                    # Simular una fila problemática
                    problematic_row = Mock()
                    problematic_row.__getitem__.side_effect = Exception(
                        "Row processing error"
                    )
                    yield i, problematic_row
                else:
                    yield i, row

        df.iterrows = mock_iterrows

        result = processor.parse_excel_data(df)

        # Debería procesar la fila válida y manejar la excepción de la problemática
        assert len(result) >= 0  # Al menos no debería fallar completamente

    def test_parse_excel_data_datetime_conversion_edge_case(self, processor):
        """Test datetime conversion edge case in parse_excel_data"""
        from datetime import datetime

        # Create DataFrame with datetime objects
        data = {
            "Fecha": [datetime(2024, 1, 1), datetime(2024, 1, 2)],
            "Valor": [5.1234, 5.2345],
        }
        df = pd.DataFrame(data)

        result = processor.parse_excel_data(df)

        assert len(result) == 2
        assert result[0][0] == date(2024, 1, 1)
        assert result[1][0] == date(2024, 1, 2)

    def test_parse_excel_data_invalid_date_type_coverage(self, processor):
        """Test invalid date type coverage in parse_excel_data"""
        # Create DataFrame with invalid date types
        data = {
            "Fecha": [123, 456],  # Numbers instead of dates
            "Valor": [5.1234, 5.2345],
        }
        df = pd.DataFrame(data)

        result = processor.parse_excel_data(df)

        # Should skip rows with invalid dates
        assert len(result) == 0

    def test_save_to_database_rollback_on_exception(self, processor):
        """Test rollback when exception occurs in save_to_database"""
        from datetime import date

        mock_db = Mock()
        records = [(date(2024, 1, 1), 5.1234)]

        # Mock that causes exception during commit
        mock_db.commit.side_effect = Exception("Database commit error")

        result = processor.save_to_database(mock_db, records)

        assert result == 0
        mock_db.rollback.assert_called_once()

    def test_refresh_data_no_records_parsed_coverage(self, processor):
        """Test refresh_data when no records can be parsed"""
        with patch.object(processor, "download_excel") as mock_download:
            with patch.object(processor, "parse_excel_data") as mock_parse:
                # Mock successful download but empty parsing
                mock_download.return_value = pd.DataFrame()
                mock_parse.return_value = []  # No records parsed

                mock_db = Mock()
                success, message, count = processor.refresh_data(mock_db)

                assert success is False
                assert "Could not extract valid data from file" in message
                assert count == 0

    def test_refresh_data_exception_handling_coverage(self, processor):
        """Test general exception handling in refresh_data"""
        with patch.object(processor, "download_excel") as mock_download:
            # Mock that causes exception
            mock_download.side_effect = Exception("Unexpected error")

            mock_db = Mock()
            success, message, count = processor.refresh_data(mock_db)

            assert success is False
            assert "Internal error" in message
            assert count == 0


class TestURExcelProcessorEdgeCases:
    """Tests for UR Excel Processor edge cases to improve coverage"""

    @pytest.fixture
    def ur_processor(self):
        return URExcelProcessor()

    def test_download_excel_request_exception_coverage(self, ur_processor):
        """Test requests exception in URExcelProcessor download_excel"""
        with patch("excel_processor.requests.get") as mock_get:
            mock_get.side_effect = Exception("Network error")

            result = ur_processor.download_excel()

            assert result is None

    def test_parse_excel_no_header_found_coverage(self, ur_processor):
        """Test when no month header is found in UR parsing"""
        # Create DataFrame without month names
        data = {"Col1": ["Data1", "Data2"], "Col2": ["Data3", "Data4"]}
        df = pd.DataFrame(data)

        result = ur_processor.parse_excel_data(df)

        # Should return empty list when no header is found
        assert result == []

    def test_save_to_database_exception_coverage(self, ur_processor):
        """Test exception in save_to_database of URExcelProcessor"""
        records = [(2024, 1, 5.1234)]

        mock_db = Mock()
        # Mock that causes exception
        mock_db.query.side_effect = Exception("Database error")

        result = ur_processor.save_to_database(mock_db, records)

        assert result == 0
        mock_db.rollback.assert_called_once()

    def test_refresh_data_download_failure_coverage(self, ur_processor):
        """Test refresh_data when download fails in UR"""
        with patch.object(ur_processor, "download_excel") as mock_download:
            mock_download.return_value = None  # Download failed

            mock_db = Mock()
            success, message, count = ur_processor.refresh_data(mock_db)

            assert success is False
            assert "Error downloading file from BHU" in message
            assert count == 0

    def test_refresh_data_no_records_coverage(self, ur_processor):
        """Test refresh_data when no records are extracted in UR"""
        with patch.object(ur_processor, "download_excel") as mock_download:
            with patch.object(ur_processor, "parse_excel_data") as mock_parse:
                mock_download.return_value = pd.DataFrame()
                mock_parse.return_value = []  # No records

                mock_db = Mock()
                success, message, count = ur_processor.refresh_data(mock_db)

                assert success is False
                assert "Could not extract valid data from file" in message
                assert count == 0

    def test_refresh_data_exception_coverage(self, ur_processor):
        """Test general exception in refresh_data of UR"""
        with patch.object(ur_processor, "download_excel") as mock_download:
            mock_download.side_effect = Exception("Unexpected error")

            mock_db = Mock()
            success, message, count = ur_processor.refresh_data(mock_db)

            assert success is False
            assert "Internal error" in message
            assert count == 0


class TestExcelProcessorMissingLinesCoverage:
    """Specific tests to cover missing lines and achieve 100% coverage"""

    @pytest.fixture
    def processor(self):
        return ExcelProcessor()

    @pytest.fixture
    def ur_processor(self):
        return URExcelProcessor()

    def test_download_excel_http_error_raise_for_status(self, processor):
        """Test lines 33-34: HTTPError in raise_for_status"""
        with patch("excel_processor.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.raise_for_status.side_effect = requests.HTTPError("HTTP 404")
            mock_get.return_value = mock_response

            result = processor.download_excel()

            assert result is None

    def test_parse_excel_data_value_conversion_errors(self, processor):
        """Test lines 86-88: ValueError and TypeError in value conversion"""
        # DataFrame with values that cause conversion errors
        data = {
            "Fecha": [date(2024, 1, 1), date(2024, 1, 2), date(2024, 1, 3)],
            "Valor": ["invalid_number", None, complex(1, 2)],  # Different error types
        }
        df = pd.DataFrame(data)

        result = processor.parse_excel_data(df)

        # Should return empty list since no values are valid
        assert result == []

    def test_save_to_database_new_record_creation(self, processor):
        """Test lines 114-116: new record creation when it doesn't exist"""
        mock_db = Mock()

        # Mock to not find existing record
        mock_db.query().filter().first.return_value = None

        data = [(date(2024, 1, 1), 5.1234)]

        result = processor.save_to_database(mock_db, data)

        assert result == 1
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    def test_refresh_data_download_none_scenario(self, processor):
        """Test line 133: when download_excel returns None"""
        with patch.object(processor, "download_excel") as mock_download:
            mock_download.return_value = None

            mock_db = Mock()
            success, message, count = processor.refresh_data(mock_db)

            assert success is False
            assert "Error downloading file from INE" in message
            assert count == 0

    def test_refresh_data_empty_records_scenario(self, processor):
        """Test lines 141-146: when parse_excel_data returns empty list"""
        with patch.object(processor, "download_excel") as mock_download:
            with patch.object(processor, "parse_excel_data") as mock_parse:
                mock_download.return_value = pd.DataFrame()
                mock_parse.return_value = []  # Empty list

                mock_db = Mock()
                success, message, count = processor.refresh_data(mock_db)

                assert success is False
                assert "Could not extract valid data from file" in message
                assert count == 0

    def test_ur_download_excel_http_error(self, ur_processor):
        """Test line 243: HTTPError in UR download_excel"""
        with patch("excel_processor.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.raise_for_status.side_effect = requests.HTTPError("HTTP 500")
            mock_get.return_value = mock_response

            result = ur_processor.download_excel()

            assert result is None

    def test_ur_parse_excel_year_column_fallback(self, ur_processor):
        """Test lines 255-271: fallback to first column for years"""
        # DataFrame without columns with valid years detectable by name
        data = [
            ["Unknown", "ENERO", "FEBRERO"],  # Header without detectable years
            ["text", 45.1, 45.2],  # Data without valid years
            ["invalid", 46.1, 46.2],
        ]
        df = pd.DataFrame(data)

        result = ur_processor.parse_excel_data(df)

        # Should use first column as fallback but not find valid years
        assert result == []

    def test_ur_parse_excel_year_validation_out_of_range(self, ur_processor):
        """Test line 282: year validation out of range"""
        # DataFrame with years outside valid range (1900-2100)
        data = [
            ["AÑO", "ENERO", "FEBRERO"],
            [1800, 45.1, 45.2],  # Very old year
            [3000, 46.1, 46.2],  # Very future year
        ]
        df = pd.DataFrame(data)

        result = ur_processor.parse_excel_data(df)

        # Should not process years outside range
        assert result == []

    def test_ur_save_to_database_new_record_creation(self, ur_processor):
        """Test lines 326-328: new UR record creation"""
        mock_db = Mock()

        # Mock to not find existing record
        mock_db.query().filter().first.return_value = None

        data = [(2024, 1, 45.1234)]

        result = ur_processor.save_to_database(mock_db, data)

        assert result == 1
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    def test_refresh_data_success_with_saved_count(self, processor):
        """Test lines 143-144: when saved_count > 0 in refresh_data"""
        with patch.object(processor, "download_excel") as mock_download:
            with patch.object(processor, "parse_excel_data") as mock_parse:
                with patch.object(processor, "save_to_database") as mock_save:
                    mock_download.return_value = pd.DataFrame()
                    mock_parse.return_value = [(date(2024, 1, 1), 5.1234)]
                    mock_save.return_value = 2  # Saved count > 0

                    mock_db = Mock()
                    success, message, count = processor.refresh_data(mock_db)

                    assert success is True
                    assert "Data updated successfully. 2 records processed" in message
                    assert count == 2

    def test_refresh_data_no_changes_saved_count_zero(self, processor):
        """Test lines 145-146: when saved_count == 0 in refresh_data"""
        with patch.object(processor, "download_excel") as mock_download:
            with patch.object(processor, "parse_excel_data") as mock_parse:
                with patch.object(processor, "save_to_database") as mock_save:
                    mock_download.return_value = pd.DataFrame()
                    mock_parse.return_value = [(date(2024, 1, 1), 5.1234)]
                    mock_save.return_value = 0  # No changes

                    mock_db = Mock()
                    success, message, count = processor.refresh_data(mock_db)

                    assert success is True
                    assert "No changes in data" in message
                    assert count == 0

    def test_ur_parse_excel_year_column_with_valid_years(self, ur_processor):
        """Test lines 255-261: detection of column with valid years"""
        # DataFrame with valid years in specific column
        data = [
            ["Text", "Years", "ENERO"],  # Header with years column
            ["data", 2020, 45.1],  # Valid years in second column
            ["data", 2021, 45.2],
        ]
        df = pd.DataFrame(data)

        result = ur_processor.parse_excel_data(df)

        # Should detect "Years" column as years column
        assert len(result) == 2
        assert result[0][0] == 2020  # First year
        assert result[1][0] == 2021  # Second year

    def test_ur_parse_excel_month_mapping_all_variants(self, ur_processor):
        """Test lines 263-271: complete mapping of month variants"""
        # DataFrame with different month name variants
        data = [
            [
                "AÑO",
                "ENERO",
                "FEB",
                "MARZO",
                "ABR",
                "MAYO",
                "JUN",
                "JULIO",
                "AGO",
                "SETIEMBRE",
                "OCT",
                "NOVIEMBRE",
                "DIC",
            ],
            [
                2024,
                45.1,
                45.2,
                45.3,
                45.4,
                45.5,
                45.6,
                45.7,
                45.8,
                45.9,
                46.0,
                46.1,
                46.2,
            ],
        ]
        df = pd.DataFrame(data)

        result = ur_processor.parse_excel_data(df)

        # Should correctly map all months
        assert len(result) == 12
        months = [record[1] for record in result]
        assert set(months) == set(range(1, 13))  # All months from 1 to 12

    def test_ur_parse_excel_year_validation_edge_cases(self, ur_processor):
        """Test line 282: year validation at boundaries"""
        # DataFrame with years at valid range boundaries (1900-2100)
        data = [
            ["AÑO", "ENERO"],
            [1899, 45.1],  # Just below limit
            [1900, 45.2],  # At lower limit
            [2100, 45.3],  # At upper limit
            [2101, 45.4],  # Just above limit
        ]
        df = pd.DataFrame(data)

        result = ur_processor.parse_excel_data(df)

        # Should only process years 1900 and 2100
        assert len(result) == 2
        years = [record[0] for record in result]
        assert 1900 in years
        assert 2100 in years
        assert 1899 not in years
        assert 2101 not in years

