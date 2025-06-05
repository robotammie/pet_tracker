import os
from . import model, server


if __name__ == "__main__":
  with server.app.app_context():
    model.connect_to_db(server.app, os.environ.get('DATABASE_URL'))
    print('Connected')

    # In case tables haven't been created, create them
    model.db.create_all()
    print('Created')