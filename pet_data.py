import os
from . import model

def all():
  pets = model.Pet.query.all()

  return(pets)

if __name__ == '__main__':
    from server import app

    with app.app_context():
      model.connect_to_db(app, os.environ.get('DATABASE_URL'))
      print('Connected')
      print(pet_data())
