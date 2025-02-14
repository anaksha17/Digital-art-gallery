from app import app
from models import db

# Create the tables in the database
with app.app_context():
    db.create_all()  # This will create the tables based on the models defined in models.py
    print("Tables created successfully!")
