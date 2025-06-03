import os
from datetime import datetime
from dateutil import relativedelta
from pytz import timezone
from . import model

def all():
  pet_data = model.Pet.query.all()

  pets = []
  for pet in pet_data:
     pets.append(
        {
           'id':  pet.uuid,
           'name': pet.name,
           'age': age(pet.birthdate)
        }
     )

  return(pets)

def age(birthdate):
  delta = relativedelta.relativedelta(datetime.now(timezone('America/Los_Angeles')), birthdate)
  if delta.years <= 2:
    return('{} months'.format(delta.months + (delta.years * 12)))

  return('{} years'.format(delta.years))


if __name__ == '__main__':
    from server import app

    with app.app_context():
      model.connect_to_db(app, os.environ.get('DATABASE_URL'))
      print('Connected')
