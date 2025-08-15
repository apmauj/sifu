import types
from unittest.mock import patch, MagicMock
from bootstrap import perform_bootstrap


def test_perform_bootstrap_all_empty():
    """When all tables empty, processors should be invoked"""
    with patch('bootstrap.get_ui_table_record_count', return_value=0), \
         patch('bootstrap.get_ur_table_record_count', return_value=0), \
         patch('bootstrap.get_exchange_rate_table_record_count', return_value=0):
        mock_ui = MagicMock(); mock_ui.refresh_data.return_value = (True, 'ok ui', 10)
        mock_ur = MagicMock(); mock_ur.refresh_data.return_value = (True, 'ok ur', 5)
        mock_ex = MagicMock(); mock_ex.refresh_data.return_value = (True, 'ok ex', 100)

        summary = perform_bootstrap(False, mock_ui, mock_ur, mock_ex)
        assert summary['ui']['attempted'] is True and summary['ui']['success'] is True
        assert summary['ur']['attempted'] is True and summary['ur']['success'] is True
        assert summary['exchange']['attempted'] is True and summary['exchange']['success'] is True
        mock_ui.refresh_data.assert_called_once()
        mock_ur.refresh_data.assert_called_once()
        mock_ex.refresh_data.assert_called_once()


def test_perform_bootstrap_present():
    """When tables already have data, processors must NOT be called"""
    with patch('bootstrap.get_ui_table_record_count', return_value=1), \
         patch('bootstrap.get_ur_table_record_count', return_value=2), \
         patch('bootstrap.get_exchange_rate_table_record_count', return_value=3):
        mock_ui = MagicMock(); mock_ur = MagicMock(); mock_ex = MagicMock()
        summary = perform_bootstrap(False, mock_ui, mock_ur, mock_ex)
        assert summary['ui']['attempted'] is False
        assert summary['ur']['attempted'] is False
        assert summary['exchange']['attempted'] is False
        mock_ui.refresh_data.assert_not_called()
        mock_ur.refresh_data.assert_not_called()
        mock_ex.refresh_data.assert_not_called()


def test_perform_bootstrap_force():
    """Force=True debe ejecutar refresh incluso con datos"""
    with patch('bootstrap.get_ui_table_record_count', return_value=10), \
         patch('bootstrap.get_ur_table_record_count', return_value=20), \
         patch('bootstrap.get_exchange_rate_table_record_count', return_value=30):
        mock_ui = MagicMock(); mock_ui.refresh_data.return_value=(True,'forced',1)
        mock_ur = MagicMock(); mock_ur.refresh_data.return_value=(True,'forced',1)
        mock_ex = MagicMock(); mock_ex.refresh_data.return_value=(True,'forced',1)
        summary = perform_bootstrap(True, mock_ui, mock_ur, mock_ex)
        assert summary['ui']['attempted'] is True
        assert summary['ur']['attempted'] is True
        assert summary['exchange']['attempted'] is True
        mock_ui.refresh_data.assert_called_once()
        mock_ur.refresh_data.assert_called_once()
        mock_ex.refresh_data.assert_called_once()
