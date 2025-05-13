import os
from model import connect_to_db, db
from server import app


if __name__ == "__main__":
  with app.app_context():
    connect_to_db(app, os.environ.get('DATABASE_URL'))
    print('Connected')

    # In case tables haven't been created, create them
    db.create_all()
    print('Created')