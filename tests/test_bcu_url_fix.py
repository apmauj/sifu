from unittest.mock import patch
from excel_processor import ExchangeRateBCUProcessor
from constants import URL_BCU_EXCHANGE_RATES


class TestBCUURLFix:
    """Test BCU URL fix and connection handling"""
    
    def test_bcu_url_constant_updated(self):
        """Test that BCU URL constant has been updated"""
        # Verify the URL has been updated to the new endpoint
        assert "Estadisticas-e-Indicadores" in URL_BCU_EXCHANGE_RATES
        assert "Cotizaciones.aspx" in URL_BCU_EXCHANGE_RATES
        assert URL_BCU_EXCHANGE_RATES.startswith("https://www.bcu.gub.uy/")
    
    def test_bcu_processor_uses_correct_url(self):
        """Test BCU processor uses the updated URL"""
        processor = ExchangeRateBCUProcessor()
        assert processor.url == URL_BCU_EXCHANGE_RATES
        assert "Estadisticas-e-Indicadores" in processor.url
    
    def test_bcu_processor_handles_webservice_failure_gracefully(self):
        """Test BCU processor handles webservice failures gracefully"""
        processor = ExchangeRateBCUProcessor()
        
        # Mock py_bcu to simulate failure
        with patch('py_bcu.bcu_cotizacion.get_cotizacion') as mock_get_cotizacion:
            mock_get_cotizacion.side_effect = Exception("Webservice unavailable")
            
            # Should return historical data fallback
            result, is_from_bcu = processor.get_current_rates()
            assert isinstance(result, list)
            assert len(result) > 0
            assert is_from_bcu  # Should be fallback data
    
    def test_bcu_processor_historical_data_fallback(self):
        """Test BCU processor returns historical data when BCU webservice is unavailable"""
        processor = ExchangeRateBCUProcessor()
        
        # Mock webservice to fail
        with patch.object(processor, 'get_current_rates_from_webservice', return_value=([], False)):
            # Should return historical current rates
            result, is_from_bcu = processor.get_current_rates()
            
            # Verify historical data structure
            assert isinstance(result, list)
            assert len(result) > 0
            assert is_from_bcu  # Should be historical data
            
            # Check historical data has expected structure (tuple format)
            historical_rate = result[0]
            assert isinstance(historical_rate, tuple)
            assert len(historical_rate) == 4  # (currency, buy, sell, average)
            
            # Verify data types
            currency, buy_rate, sell_rate, average_rate = historical_rate
            assert isinstance(currency, str)
            assert isinstance(buy_rate, (int, float))
            assert isinstance(sell_rate, (int, float))
            assert isinstance(average_rate, (int, float, type(None)))
    
    def test_webservice_successful_response(self):
        """Test webservice successful response"""
        processor = ExchangeRateBCUProcessor()
        
        # Mock successful webservice response
        with patch('py_bcu.bcu_cotizacion.get_cotizacion') as mock_get_cotizacion:
            mock_get_cotizacion.return_value = (40.8, 41.2)  # Sample USD rates
            
            # Should return webservice data
            result, is_from_bcu = processor.get_current_rates_from_webservice()
            assert isinstance(result, list)
            assert len(result) > 0
            assert is_from_bcu  # Should be real BCU data
    
    def test_minimal_sample_rates_structure(self):
        """Test that minimal sample rates have correct structure"""
        processor = ExchangeRateBCUProcessor()
        
        # Get minimal sample rates
        sample_rates = processor._get_minimal_sample_rates()
        
        # Verify structure
        assert isinstance(sample_rates, list)
        assert len(sample_rates) == 4  # USD, EUR, ARS, BRL
        
        # Check each rate
        for rate in sample_rates:
            assert isinstance(rate, tuple)
            assert len(rate) == 4  # (currency, buy, sell, average)
            currency, buy_rate, sell_rate, average_rate = rate
            assert isinstance(currency, str)
            assert isinstance(buy_rate, (int, float))
            assert isinstance(sell_rate, (int, float))
            assert isinstance(average_rate, (int, float, type(None)))
            assert buy_rate < sell_rate  # Buy should be less than sell
    
    def test_bcu_webservice_integration(self):
        """Test BCU webservice integration with mocked py_bcu"""
        processor = ExchangeRateBCUProcessor()
        
        # Mock py_bcu get_cotizacion function
        with patch('py_bcu.bcu_cotizacion.get_cotizacion') as mock_get_cotizacion:
            # Mock successful responses for different currencies
            mock_get_cotizacion.side_effect = [
                (40.8, 41.2),  # USD
                (47.0, 47.5),  # EUR
                (7.5, 7.7),    # BRL
                (0.034, 0.036), # ARS
    
            ]
            
            # Should return real BCU data
            result, is_from_bcu = processor.get_current_rates_from_webservice()
            
            # Verify webservice data structure
            assert isinstance(result, list)
            assert len(result) == 4  # All 4 currencies
            assert is_from_bcu  # Should be real BCU data
            
            # Check first currency (USD)
            usd_rate = result[0]
            assert usd_rate[0] == 'USD'
            assert isinstance(usd_rate[1], float)  # buy_rate
            assert isinstance(usd_rate[2], float)  # sell_rate
            assert isinstance(usd_rate[3], float)  # avg_rate
            
            # Verify get_cotizacion was called for each currency
            assert mock_get_cotizacion.call_count == 4 