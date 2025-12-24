import model

from datetime import datetime, timedelta
from flask import session
from pytz import timezone
from sqlalchemy import select
from sqlalchemy.orm import Session


class Food(model.Event):
  def __init__(self, household_uuid, created_by, data={}, timestamp=None):
    now = datetime.now(tz=timezone('America/Los_Angeles'))
    
    self.household_uuid = household_uuid
    self.pet_uuid = data.get('pet') or None
    self.timestamp = timestamp or now
    self.type = model.EventType.Food
    self.created_at = now
    self.created_by = created_by
    self.meta = {
      'name': data.get('food-name'),
      'type': data.get('food-type'),
      'amount': data.get('food-amount'),
      'unit': data.get('food-unit'),
      'calories': data.get('food-calories'),
    }
class Litter(model.Event):
  def __init__(self, household_uuid, created_by, data={}, timestamp=None):
    now = datetime.now(tz=timezone('America/Los_Angeles'))
    
    self.household_uuid = household_uuid
    self.pet_uuid = data.get('pet') or None
    self.timestamp = timestamp or now
    self.type = model.EventType.Litter
    self.created_at = now
    self.created_by = created_by
    self.meta = None  # no current meta values for this type of event
  

class Medicine(model.Event):
  def __init__(self, household_uuid, created_by, data={}, timestamp=None):
    now = datetime.now(tz=timezone('America/Los_Angeles'))
    
    self.household_uuid = household_uuid
    self.pet_uuid = data.get('pet') or None
    self.timestamp = timestamp or now
    self.type = model.EventType.Medicine
    self.created_at = now
    self.created_by = created_by
    self.meta = {
      'name': data.get('medicine-name'),
      'dose': data.get('medicine-dose'),
    }

  def __repr__(self):
    return f"<Medicine {self.meta.get('name')} - {self.meta.get('dose')} - {self.timestamp}>"

# # # # # # # # # # # # # # # # # # # # #

def all_events() -> list[model.Event]:
  with Session(model.engine) as s:
    if not session['user']:
      return []
    else:
      event_data = s.execute(
        select(model.Event).join(model.Pet, isouter=True).order_by(model.Event.timestamp.desc())
        .where(model.Event.household_uuid == session.get('household').uuid)
      )

    events = []
    for row in event_data:
      for event in row:
        events.append({
          'timestamp': event.timestamp,
          'pet': event.pet.name if event.pet_uuid else '',
          'type': event.type.name,
          'meta': event.meta,
        })
    
  return(events)

def day_view(date: datetime) -> list[{'type': model.EventType, 'pet': str, 'meta': dict[str, any]}]:
  with Session(model.engine) as s:
    start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = start_date + timedelta(days=1)
    query = (select(model.Event.type, model.Pet.name, model.Event.meta).join(model.Pet, isouter=True)
      .where(model.Event.household_uuid == session.get('household').uuid)
      .where(model.Event.timestamp >= start_date)
      .where(model.Event.timestamp < end_date))
    events_data = s.execute(query)

  events = dict[str, any]([])
  print('events_data', events_data)
  for event in events_data:
    match event[0]:
      case model.EventType.Food:
        val = events.get('Food', {})
        val.update([(event[1], events.get('Food', {}).get(event[1], 0) + float(event[2].get('calories', 0)))])    
        events.update({ 'Food': val })
      case model.EventType.Litter:
        val = events.get('Litter', {})
        val.update([('', events.get('Litter', {}).get('', 0) + 1 )])    
        events.update({'Litter': val})
      # case model.EventType.Medicine:
      #   events.update({ 'Medicine': events.get('Medicine', 0) + 1 })

  return(events)


def new(household_uuid: str, event_type: model.EventType, created_by: str, data: dict[str, any], timestamp=None):
  with Session(model.engine) as session:

    match event_type:
      # case model.EventType.Food:
      case model.EventType.Food:
        new_event = Food(household_uuid=household_uuid, created_by=created_by, data=data, timestamp=timestamp)
      # case model.EventType.Litter:
      case model.EventType.Litter:
        new_event = Litter(household_uuid=household_uuid, created_by=created_by, data=data, timestamp=timestamp)
      case model.EventType.Medicine:
      # case 3:
        new_event = Medicine(household_uuid=household_uuid, created_by=created_by, data=data, timestamp=timestamp)
      case _:
        return

    session.add(new_event)
    session.commit()


    



