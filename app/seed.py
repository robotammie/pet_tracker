import os
import model


if __name__ == "__main__":
  with model.app.app_context():
    # model.connect_to_db(model.app, os.environ.get('DATABASE_URL'))
    print('Connected')

    # In case tables haven't been created, create them
    model.db.create_all()
    print('Created')