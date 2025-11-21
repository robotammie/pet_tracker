import model

from datetime import datetime
from flask import session
from pytz import timezone
from sqlalchemy import select
from sqlalchemy.orm import Session
from uuid import uuid4


class Food(model.Event):
  """
  meta example:
    {
      type: Hills Probiotic
      amount: 1/2 cup
      calories: 150
    }
  """

  def __init__(self, pet_uuid, created_by, meta={}, timestamp=None):
    now = datetime.now(tz=timezone('America/Los_Angeles'))
    
    self.uuid = uuid4()
    self.pet_uuid = pet_uuid
    self.timestamp = timestamp or now
    self.type = model.EventType.Food
    self.created_at = now
    self.created_by = created_by
    self.meta = meta  # TODO establish meta values and set validation


class Litter(model.Event):
  """
  meta example:
    {}
  """
  def __init__(self, created_by, pet_uuid=None, meta={}, timestamp=None):
    now = datetime.now(tz=timezone('America/Los_Angeles'))
    
    self.uuid = uuid4()
    self.pet_uuid = pet_uuid
    self.timestamp = timestamp or now
    self.type = model.EventType.Litter
    self.created_at = now
    self.created_by = created_by
    self.meta = meta  # TODO establish meta values and set validation


class Medicine(model.Event):
  """
  meta example:
    {
      Medicine: Probiotic
      Dose: 1 packet
    }
  """
  def __init__(self, created_by, pet_uuid=None, meta={}, timestamp=None):
    now = datetime.now(tz=timezone('America/Los_Angeles'))
    
    self.uuid = uuid4()
    self.pet_uuid = pet_uuid
    self.timestamp = timestamp or now
    self.type = model.EventType.Medicine
    self.created_at = now
    self.created_by = created_by
    self.meta = meta  # TODO establish meta values and set validation

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

def new(event_type: model.EventType, created_by='1', meta={}, pet_uuid=None, timestamp=None):

  with Session(model.engine) as session:
    match event_type:
      # case model.EventType.Food:
      case 1:
        new_event = Food(pet_uuid=pet_uuid, created_by=created_by, meta=meta, timestamp=timestamp)
      # case model.EventType.Litter:
      case 2:
        new_event = Litter(pet_uuid=pet_uuid, created_by=created_by, meta=meta, timestamp=timestamp)
      case model.EventType.Medicine:
      # case 3:
        new_event = Medicine(pet_uuid=pet_uuid, created_by=created_by, meta=meta, timestamp=timestamp)
      case _:
        return

    session.add(new_event)
    session.commit()


    



