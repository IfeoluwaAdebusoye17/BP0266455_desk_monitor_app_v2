import pytest
from unittest.mock import patch

from dock_monitor import notify_backend

BACKEND_API_URL = 'http://127.0.0.1:5000/desks'

@pytest.fixture
def mock_put():
    with patch('requests.put') as mock:
        yield mock

def test_notify_backend_occupied(mock_put):
    docking_station_id = '1'
    employee_id = '1'
    url = f'{BACKEND_API_URL}/{docking_station_id}'
    data = {'employee_id': employee_id}

    mock_put.return_value.status_code = 200

    notify_backend(docking_station_id, employee_id, occupied=True)

    mock_put.assert_called_once_with(url, json=data)

def test_notify_backend_unoccupied(mock_put):
    docking_station_id = '1'
    employee_id = '1'
    url = f'{BACKEND_API_URL}/{docking_station_id}'
    data = {'employee_id': None}

    mock_put.return_value.status_code = 200

    notify_backend(docking_station_id, employee_id, occupied=False)

    mock_put.assert_called_once_with(url, json=data)

def test_notify_backend_failure(mock_put):
    docking_station_id = '1'
    employee_id = '1'
    url = f'{BACKEND_API_URL}/{docking_station_id}'
    data = {'employee_id': employee_id}

    mock_put.return_value.status_code = 500

    notify_backend(docking_station_id, employee_id, occupied=True)

    mock_put.assert_called_once_with(url, json=data)