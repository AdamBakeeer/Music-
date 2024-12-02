from app import app, db
from app.populate import populate_database

# Run the database population logic within the app context
with app.app_context():
    populate_database()