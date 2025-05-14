import os
from model import Pet, connect_to_db

def pet_data():
  pets = Pet.query.all()

  return(pets)

if __name__ == '__main__':
    from server import app

    with app.app_context():
      connect_to_db(app, os.environ.get('DATABASE_URL'))
      print('Connected')
      print(pet_data())
