from app import app, db  # Ensure you import both the app and db

# Create an application context
with app.app_context():
    db.create_all()
