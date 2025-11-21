import os
import model

from datetime import datetime
from dateutil import relativedelta
from sqlalchemy import select
from sqlalchemy.orm import Session
from pytz import timezone

def all(user: model.AppUser) -> {str, any}:
  with Session(model.engine) as s:
    pet_data = s.execute(select(model.Pet).join(model.PetUser).join(model.AppUser).where(model.AppUser.uuid == user.uuid)).all()

    pets = []
    for row in pet_data:
      for pet in row:
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
    from app.server import app

    with app.app_context():
      model.connect_to_db(app, os.environ.get('DATABASE_URL'))
      print('Connected')
