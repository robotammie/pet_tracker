import model

from datetime import datetime, timedelta
from flask import session
from pytz import timezone
from sqlalchemy import select
from sqlalchemy.orm import Session
from uuid import uuid4


class Food(model.Event):
  def __init__(self, pet_uuid, created_by, meta={}, timestamp=None):
    now = datetime.now(tz=timezone('America/Los_Angeles'))
    
    self.uuid = uuid4()
    self.pet_uuid = pet_uuid
    self.timestamp = timestamp or now
    self.type = model.EventType.Food
    self.created_at = now
    self.created_by = created_by
    self.meta = {
      'name': meta.get('name'),
      'type': meta.get('type'),
      'amount': meta.get('amount'),
      'unit': meta.get('unit'),
      'calories': meta.get('calories'),
    }

class Litter(model.Event):
  def __init__(self, created_by, pet_uuid=None, meta={}, timestamp=None):
    now = datetime.now(tz=timezone('America/Los_Angeles'))
    
    self.uuid = uuid4()
    self.pet_uuid = pet_uuid
    self.timestamp = timestamp or now
    self.type = model.EventType.Litter
    self.created_at = now
    self.created_by = created_by
    self.meta = meta  # no current meta values for this type of event
  

class Medicine(model.Event):
  def __init__(self, created_by, pet_uuid=None, meta={}, timestamp=None):
    now = datetime.now(tz=timezone('America/Los_Angeles'))
    
    self.uuid = uuid4()
    self.pet_uuid = pet_uuid
    self.timestamp = timestamp or now
    self.type = model.EventType.Medicine
    self.created_at = now
    self.created_by = created_by
    self.meta = {
      'name': meta.get('medicine'),
      'dose': meta.get('dose'),
    }

  def __repr__(self):
    return f"<Medicine {self.meta.get('name')} - {self.meta.get('dose')} - {self.timestamp}>"

# # # # # # # # # # # # # # # # # # # # #

def all_events() -> list[model.Event]:
  with Session(model.engine) as s:
    if not session['user']:
      return []
    else:
      event_data = s.execute(select(model.Event).join(model.Pet).join(model.PetUser).join(model.AppUser).where(model.AppUser.uuid == session.get('user').uuid))

    events = []
    for row in event_data:
      for event in row:
        events.append({
          'timestamp': event.timestamp,
          'pet': event.pet.name,
          'type': event.type,
          'meta': event.meta,
        })
    
  return(events)

def day_view(date: datetime) -> list[{'pet': str, 'type': model.EventType, 'meta': dict[str, any]}]:
  with Session(model.engine) as s:
    if not session['user']:
      return []
    else:
      food = s.execute(
        select(model.Event.pet_uuid, model.Event.meta)
        .join(model.Pet)
        .join(model.PetUser)
        .where(model.PetUser.user_id == session.get('user').uuid)
        .where(model.Event.type == model.EventType.Food)
        .where(model.Event.timestamp >= date)
        .where(model.Event.timestamp < date + timedelta(days=1))
      ).all()


      events = []
      for row in food:
        for event in row:
          events.append({
            'pet': event.pet.name,
            'type': event.type,
            'meta': event.meta,
          })

      return events


def new(event_type: model.EventType, created_by: str, meta={}, pet_uuid=None, timestamp=None):
  with Session(model.engine) as session:
    match event_type:
      # case model.EventType.Food:
      case model.EventType.Food:
        new_event = Food(pet_uuid=pet_uuid, created_by=created_by, meta=meta, timestamp=timestamp)
      # case model.EventType.Litter:
      case model.EventType.Litter:
        new_event = Litter(pet_uuid=pet_uuid, created_by=created_by, meta=meta, timestamp=timestamp)
      case model.EventType.Medicine:
      # case 3:
        new_event = Medicine(pet_uuid=pet_uuid, created_by=created_by, meta=meta, timestamp=timestamp)
      case _:
        return

    session.add(new_event)
    session.commit()


    



