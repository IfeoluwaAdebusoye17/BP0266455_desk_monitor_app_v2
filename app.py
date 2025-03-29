from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
import os
from dotenv import load_dotenv

load_dotenv()
database_uri = os.getenv('SQL_DATABASE_URI')

app = Flask(__name__)

#PostgreSQL database connection
app.config[ 'SQLALCHEMY_DATABASE_URI'] = database_uri
app.config[ 'SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app) #Set up communication via ORM
socketio = SocketIO(app) #Sets up real time communication

#Defining models for the database
class Employees(db.Model):
    __tablename__ = 'employees'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    laptop_id = db.Column(db.String(50), nullable=False, unique=True)

class DockingStations(db.Model):
    __tablename__ = 'docking_stations'
    id = db.Column(db.Integer, primary_key=True)
    unique_id = db.Column(db.String(50), nullable=False, unique=True)
    desk_number = db.Column(db.String(10), nullable=False)

class DeskStatus(db.Model):
    __tablename__ = 'desk_status'
    id = db.Column(db.Integer, primary_key=True)
    docking_station_id = db.Column(db.Integer, db.ForeignKey('docking_stations.id'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    status = db.Column(db.String(20), default='free')
    last_updated = db.Column(db.DateTime, default=db.func.current_timestamp())
    temperature = db.Column(db.Numeric(5, 2))
    humidity = db.Column(db.Numeric(5, 2))
    light = db.Column(db.Numeric(6, 2))
    noise = db.Column(db.Numeric(5, 2))

class PastOcupancyIeq(db.Model):
    __tablename__ = 'past_occupancy_ieq'
    id = db.Column(db.Integer, primary_key=True)
    desk_id = db.Column(db.Integer)
    docking_station_id = db.Column(db.Integer)
    status = db.Column(db.String(20))
    last_updated = db.Column(db.DateTime)
    temperature = db.Column(db.Numeric(5, 2))
    humidity = db.Column(db.Numeric(5, 2))
    light = db.Column(db.Numeric(6, 2))
    noise = db.Column(db.Numeric(5, 2))

class PredictedData(db.Model):
    __tablename__ = 'predicted_data'
    id = db.Column(db.Integer, primary_key=True)
    Zone = db.Column(db.Integer)
    Desk = db.Column(db.Integer)
    Hour = db.Column(db.Integer)
    DayOfWeek = db.Column(db.Integer)
    DayOfMonth = db.Column(db.Integer)
    Occupied = db.Column(db.Integer)
    Predicted_Temperature = db.Column(db.Numeric(8, 4))
    Predicted_Humidity = db.Column(db.Numeric(8, 4))
    Predicted_Light = db.Column(db.Numeric(9, 4))
    Predicted_Noise = db.Column(db.Numeric(8, 4))

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/past")
def past():
    records = PastOcupancyIeq.query.all()
    return render_template('past.html', records=records)

@app.route("/predicted")
def predicted():
    records = PredictedData.query.all()
    return render_template('predicted.html', records=records)


#API endpoint to get the desk statuses
@app.route('/desks', methods=['GET'])
def get_desk_info():
    desks = DeskStatus.query.all()
    return jsonify([
        {
            'docking_station_id': desk.docking_station_id,
            'status': desk.status,
            'last_updated': desk.last_updated,
            'temperature': desk.temperature,
            'humidity': desk.humidity,
            'light': desk.light,
            'noise': desk.noise    
        } for desk in desks])

#API endpoint to update desk status when laptop connected
@app.route('/desks/<int:docking_station_id>', methods=['PUT'])
def update_desk_status(docking_station_id):
    data = request.get_json()
    employee_id = data.get('employee_id') # Could be None when unoccupied
    desk = DeskStatus.query.filter_by(docking_station_id=docking_station_id).first()

    if desk:
        if employee_id is not None:
            desk.employee_id = employee_id
            desk.status = 'occupied'
        else:
            desk.employee_id = None
            desk.status = 'free' #Mark as free when unoccppied
        db.session.commit()
        socketio.emit('desk_update', {'desk_id': desk.id, 'status': desk.status}, namespace='/', to=None)
        return jsonify({'message': 'Desk status updated'}), 200
    else:
        return jsonify({'message': 'Docking station not found'}), 404

if __name__ == '__main__':
    socketio.run(app)