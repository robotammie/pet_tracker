import os
import model

from datetime import datetime
from dateutil import relativedelta
from sqlalchemy import select
from typing import Any

def all(household_uuid: str) -> list[dict[str, Any]]:
  """Get all pets for a household.
  
  Args:
    household_uuid: UUID of the household
    
  Returns:
    List of dictionaries containing pet id, name, and age
  """
  pet_data = model.db.session.execute(
    select(model.Pet).where(model.Pet.household_uuid == household_uuid)
  ).all()

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

  return pets

def age(birthdate):
  """Calculate and format pet age from birthdate.
  
  Args:
    birthdate: datetime object or None
    
  Returns:
    str: Formatted age string or 'Unknown' if birthdate is None
  """
  if birthdate is None:
    return 'Unknown'
  
  delta = relativedelta.relativedelta(datetime.now(model.APP_TIMEZONE), birthdate)
  if delta.years <= 2:
    return('{} months'.format(delta.months + (delta.years * 12)))

  return('{} years'.format(delta.years))


if __name__ == '__main__':
    from app.server import app

    with app.app_context():
      model.connect_to_db(app, os.environ.get('DATABASE_URL'))
      print('Connected')
