from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_session import Session
from flask_login import LoginManager, UserMixin, login_user, logout_user,current_user
from flask_restful import Api # type: ignore
# from models import Bus, Route, Trip, Review, CanceledTrip
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bus.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
api = Api(app)


# Configure the Flask app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bus.db'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'
app.config['SESSION_TYPE'] = 'filesystem'  # Corrected config key for session type
app.config['SESSION_COOKIE_NAME'] = 'bus_session'  # Corrected config key for session cookie name

# Initialize third-party extensions
# db = SQLAlchemy(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)
Session(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Define User model with UserMixin
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

class Bus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    capacity = db.Column(db.Integer, nullable=False)

class Route(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    origin = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    is_express = db.Column(db.Boolean, default=False)

class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bus_id = db.Column(db.Integer, db.ForeignKey('bus.id'), nullable=False)
    route_id = db.Column(db.Integer, db.ForeignKey('route.id'), nullable=False)
    qr_code = db.Column(db.String(255))
    status = db.Column(db.String(10), default='active') 

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class CanceledTrip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'), nullable=False)
    reason = db.Column(db.Text)

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    route_id = db.Column(db.Integer, db.ForeignKey('route.id'), nullable=False)
    departure_time = db.Column(db.DateTime, nullable=False)
    available_seats = db.Column(db.Integer, nullable=False)
    total_seats = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

    # Define relationships
    route = db.relationship('Route', backref=db.backref('schedules', lazy=True))

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    seat_number = db.Column(db.Integer, nullable=False)
    booking_time = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default='Pending')

     # Define relationships
    schedule = db.relationship('Schedule', backref=db.backref('bookings', lazy=True))
    user = db.relationship('User', backref=db.backref('bookings', lazy=True))

# Setup login manager
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Authentication routes and functions
@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')  # Use request.json instead of request.data
    password = request.json.get('password')

    # Check if user exists
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Check password
    if user.password_hash == password:
        login_user(user)
        return jsonify({'message': 'Login success'})
    else:
        return jsonify({'error': 'Incorrect password'}), 401

@app.route('/register', methods=['POST'])
def register():
    email = request.json.get('email')
    username = request.json.get('username')
    password = request.json.get('password')

    # Check if email is provided
    if not email:
        return jsonify({'error': 'Email is required'}), 400

    # Check if user exists
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'User already exists'}), 400

    # Create new user
    new_user = User(username=username, email=email, password_hash=password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'})

@app.route('/logout', methods=['POST'])
def logout():
    if current_user.is_authenticated:
        logout_user()
        return jsonify({'message': 'Logout successful'})
    else:
        return jsonify({'error': 'User not logged in'}), 401
    
# logic to fetch schedules based on route ID, date, and time
@app.route('/schedules', methods=['POST'])
def create_schedule():
    data = request.get_json()

    # Check if data is missing
    required_fields = ['route_id', 'departure_time', 'available_seats', 'total_seats', 'price']
    if not data or not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing fields in request data'}), 400

    # Convert departure_time string to a datetime object
    try:
        departure_time = datetime.strptime(data['departure_time'], '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return jsonify({'error': 'Invalid departure_time format. Use YYYY-MM-DD HH:MM:SS'}), 400

    # Create a new Schedule object and add it to the database
    new_schedule = Schedule(
        route_id=data['route_id'],
        departure_time=departure_time,
        available_seats=data['available_seats'],
        total_seats=data['total_seats'],
        price=data['price']
    )
    db.session.add(new_schedule)
    db.session.commit()

    return jsonify({'message': 'Schedule created successfully'}), 201


@app.route('/bookings', methods=['POST'])
def create_booking():
    data = request.get_json()

    # Check if data is missing
    required_fields = ['schedule_id', 'user_id', 'seat_number']
    if not data or not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing fields in request data'}), 400

    # Check if the seat is available in the schedule
    schedule = Schedule.query.get(data['schedule_id'])
    if not schedule or schedule.available_seats <= 0:
        return jsonify({'error': 'No available seats for this schedule'}), 400

    # Create a new Booking object and add it to the database
    new_booking = Booking(
        schedule_id=data['schedule_id'],
        user_id=data['user_id'],
        seat_number=data['seat_number']
    )
    db.session.add(new_booking)

    # Update available seats
    schedule.available_seats -= 1
    db.session.commit()

    return jsonify({'message': 'Booking created successfully'}), 201



if __name__ == '__main__':
    app.run(debug=True)