from app import app, db
from models import User, Bus, Route, Trip, Review, CanceledTrip


def seed_database():
    with app.app_context():
    # Create users
        user1 = User(username='user1', email='user1@example.com', password_hash='hashed_password_1')
        user2 = User(username='user2', email='user2@example.com', password_hash='hashed_password_2')
        user3 = User(username='user3', email='user3@example.com', password_hash='hashed_password_3')

        # Create buses
        bus1 = Bus(capacity=50)
        bus2 = Bus(capacity=40)
        bus3 = Bus(capacity=60)

        # Create routes
        route1 = Route(origin='Origin 1', destination='Destination 1', is_express=True)
        route2 = Route(origin='Origin 2', destination='Destination 2', is_express=False)
        route3 = Route(origin='Origin 3', destination='Destination 3', is_express=True)

        # Create trips
        trip1 = Trip(user_id=1, bus_id=1, route_id=1, qr_code='QR_CODE_1', status='active')
        trip2 = Trip(user_id=2, bus_id=2, route_id=2, qr_code='QR_CODE_2', status='completed')
        trip3 = Trip(user_id=3, bus_id=3, route_id=3, qr_code='QR_CODE_3', status='canceled')

        # Create reviews
        review1 = Review(content='Great trip!', user_id=1)
        review2 = Review(content='Average experience.', user_id=2)
        review3 = Review(content='Terrible service.', user_id=3)

        # Create canceled trips
        canceled_trip1 = CanceledTrip(trip_id=1, reason='Weather conditions')
        canceled_trip2 = CanceledTrip(trip_id=2, reason='Unexpected maintenance')

        # Add objects to the session
        db.session.add_all([user1, user2, user3, bus1, bus2, bus3, route1, route2, route3,
                            trip1, trip2, trip3, review1, review2, review3, canceled_trip1, canceled_trip2])

        # Commit the session to persist the changes
        db.session.commit()

if __name__ == '__main__':
    seed_database()
