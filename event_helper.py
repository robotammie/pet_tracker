from datetime import datetime
from pytz import timezone
from sqlalchemy.orm import Session
from uuid import uuid4
from . import model


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

def all_events():
  events = model.Event.query.all()
  event_info = []
  for event in events:
    event_info.append({
      'timestamp': event.timestamp,
      'pet': event.pet.name,
      'type': event.type,
      'meta': event.meta,
    })
  return(event_info)

def new(event_type, created_by='admin', meta={}, pet_uuid=None, timestamp=None):
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
        breakpoint()
        return

    session.add(new_event)
    session.commit()


    



