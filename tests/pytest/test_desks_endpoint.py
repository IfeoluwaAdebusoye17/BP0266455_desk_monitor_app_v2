import pytest
from datetime import datetime
from app import app, db, DeskStatus, DockingStations

@pytest.fixture
def client():

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()

def test_get_desk_info(client):
    # Add test data to the docking_stations table
    docking_station1 = DockingStations(id=1, unique_id='abc123', desk_number='aaa111')
    docking_station2 = DockingStations(id=2, unique_id='def456', desk_number='bbb222')
    db.session.add(docking_station1)
    db.session.add(docking_station2)
    db.session.commit()

    # Add test data to the desk_status table
    desk1 = DeskStatus(id=1, docking_station_id=1, status='occupied', last_updated=datetime(2020, 1, 2), employee_id='1', temperature=22.5, humidity=45.0, light=300.0, noise=50.0)
    desk2 = DeskStatus(id=2, docking_station_id=2, status='free', last_updated=datetime(2020, 1, 2), employee_id='2',temperature=23.0, humidity=40.0, light=350.0, noise=45.0)
    db.session.add(desk1)
    db.session.add(desk2)
    db.session.commit()

    # Make a GET request to the /desks endpoint
    response = client.get('/desks')
    assert response.status_code == 200

    # Check the response data
    data = response.get_json()
    assert len(data) == 2
    assert data[0]['docking_station_id'] == 1
    assert data[0]['status'] == 'occupied'
    assert data[0]['temperature'] == '22.50'
    assert data[0]['humidity'] == '45.00'
    assert data[0]['light'] == '300.00'
    assert data[0]['noise'] == '50.00'
    assert data[1]['docking_station_id'] == 2
    assert data[1]['status'] == 'free'
    assert data[1]['temperature'] == '23.00'
    assert data[1]['humidity'] == '40.00'
    assert data[1]['light'] == '350.00'
    assert data[1]['noise'] == '45.00'