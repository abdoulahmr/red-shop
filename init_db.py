# init_db.py
from app import app
from models import db

# This creates all tables defined in models.py inside the SQLite database
with app.app_context():
    db.create_all()
    print("Database tables created successfully!")