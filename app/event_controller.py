import model

from datetime import datetime, timedelta, timezone
from flask import session
from sqlalchemy import select
from typing import Any, Optional


def _create_event_base(household_uuid: str, created_by: str, event_type: model.EventType, 
                       data: dict[str, Any], timestamp: Optional[datetime] = None) -> model.Event:
    """Base function to create event objects with common initialization.
    
    Args:
        household_uuid: UUID of the household
        created_by: UUID of the user creating the event
        event_type: Type of event to create
        data: Dictionary containing event-specific data
        timestamp: Optional timestamp, defaults to now
        
    Returns:
        Event object with common fields initialized
    """
    now = datetime.now(tz=model.APP_TIMEZONE)
    event = model.Event()
    event.household_uuid = household_uuid
    event.pet_uuid = data.get('pet') if event_type in [model.EventType.Food, model.EventType.Medicine] else None
    event.timestamp = timestamp or now
    event.type = event_type
    event.created_at = now
    event.created_by = created_by
    return event


def _create_food_event(household_uuid: str, created_by: str, data: dict[str, Any], 
                       timestamp: Optional[datetime] = None) -> model.Event:
    """Create a Food event.
    
    Args:
        household_uuid: UUID of the household
        created_by: UUID of the user creating the event
        data: Dictionary containing food event data
        timestamp: Optional timestamp, defaults to now
        
    Returns:
        Event object configured for Food type
    """
    event = _create_event_base(household_uuid, created_by, model.EventType.Food, data, timestamp)
    event.meta = {
        'name': data.get('food-name'),
        'type': data.get('food-type'),
        'amount': data.get('food-amount'),
        'unit': data.get('food-unit'),
        'calories': data.get('food-calories'),
    }
    return event


def _create_litter_event(household_uuid: str, created_by: str, data: dict[str, Any], 
                         timestamp: Optional[datetime] = None) -> model.Event:
    """Create a Litter event.
    
    Args:
        household_uuid: UUID of the household
        created_by: UUID of the user creating the event
        data: Dictionary containing litter event data
        timestamp: Optional timestamp, defaults to now
        
    Returns:
        Event object configured for Litter type
    """
    event = _create_event_base(household_uuid, created_by, model.EventType.Litter, data, timestamp)
    event.meta = None  # no current meta values for this type of event
    return event


def _create_medicine_event(household_uuid: str, created_by: str, data: dict[str, Any], 
                           timestamp: Optional[datetime] = None) -> model.Event:
    """Create a Medicine event.
    
    Args:
        household_uuid: UUID of the household
        created_by: UUID of the user creating the event
        data: Dictionary containing medicine event data
        timestamp: Optional timestamp, defaults to now
        
    Returns:
        Event object configured for Medicine type
    """
    event = _create_event_base(household_uuid, created_by, model.EventType.Medicine, data, timestamp)
    event.meta = {
        'name': data.get('medicine-name'),
        'dose': data.get('medicine-dose'),
    }
    return event

# # # # # # # # # # # # # # # # # # # # #

def all_events() -> list[dict[str, Any]]:
    """Get all events for the current user's household.
    
    Returns:
        List of dictionaries containing event information
    """
    if not session.get('user') or not session.get('household'):
        return []
    
    household_uuid = session.get('household').uuid
    event_data = model.db.session.execute(
        select(model.Event)
        .join(model.Pet, isouter=True)
        .order_by(model.Event.timestamp.desc())
        .where(model.Event.household_uuid == household_uuid)
    ).all()

    events = []
    for row in event_data:
        for event in row:
            events.append({
                'timestamp': event.timestamp,
                'pet': event.pet.name if event.pet_uuid and event.pet else '',
                'type': event.type.name,
                'meta': event.meta,
            })
    
    return events

def summary() -> list[dict[str, Any]]:
    """Get a summary of events for the current user's household.
    
    Returns:
        List of dictionaries containing event information
    """
    if not session.get('user') or not session.get('household'):
        return []
    
    household_uuid = session.get('household').uuid
    event_data = model.db.session.execute(
        select(model.Event.type, model.Pet.name, model.Event.timestamp, model.Event.meta)
        .distinct(model.Event.type, model.Event.pet_uuid)
        .join(model.Pet, isouter=True)
        .order_by(model.Event.type, model.Event.pet_uuid, model.Event.timestamp.desc())
        .where(model.Event.household_uuid == household_uuid)
    ).all()

    events = []
    for row in event_data:
        delta = datetime.now(tz=model.APP_TIMEZONE) - row.timestamp
        if delta.days > 29:
            time_ago = "weeks ago"
        elif delta.days > 7:
            time_ago = f"{delta.days // 7} weeks ago"
        elif delta.days > 0:
            time_ago = f"{delta.days} days ago"
        elif delta.seconds > 3600:
            time_ago = f"{delta.seconds // 3600} hours ago"
        elif delta.seconds > 60:
            time_ago = f"{delta.seconds // 60} minutes ago"
        else:
            time_ago = f"{delta.seconds} seconds ago"

        events.append({
            'type': row.type.name,
            'pet': row.name if row.name else '',
            'time_ago': time_ago,
            'meta': row.meta,
        })
    
    return events

def day_view(date: datetime) -> dict[str, Any]:
    """Get aggregated events for a specific day.
    
    Args:
        date: Date to view events for
        
    Returns:
        Dictionary with event types as keys and aggregated data as values
    """
    if not session.get('household'):
        return {}
    
    household_uuid = session.get('household').uuid
    start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = start_date + timedelta(days=1)
    
    query = (select(model.Event.type, model.Pet.name, model.Event.meta)
             .join(model.Pet, isouter=True)
             .where(model.Event.household_uuid == household_uuid)
             .where(model.Event.timestamp >= start_date)
             .where(model.Event.timestamp < end_date))
    events_data = model.db.session.execute(query).all()

    events: dict[str, Any] = {}
    for event_row in events_data:
        event_type, pet_name, meta = event_row[0], event_row[1], event_row[2]
        pet_name = pet_name or ''
        
        match event_type:
            case model.EventType.Food:
                if 'Food' not in events:
                    events['Food'] = {}
                calories = float(meta.get('calories', 0)) if meta else 0
                events['Food'][pet_name] = events['Food'].get(pet_name, 0) + calories
            case model.EventType.Litter:
                if 'Litter' not in events:
                    events['Litter'] = {}
                events['Litter'][pet_name] = events['Litter'].get(pet_name, 0) + 1
            case model.EventType.Medicine:
                if 'Medicine' not in events:
                    events['Medicine'] = {}
                events['Medicine'][pet_name] = events['Medicine'].get(pet_name, 0) + 1

    return events


def new(household_uuid: str, event_type: model.EventType, created_by: str, 
        data: dict[str, Any], timestamp: Optional[datetime] = None) -> Optional[model.Event]:
    """Create a new event.
    
    Args:
        household_uuid: UUID of the household
        event_type: Type of event to create
        created_by: UUID of the user creating the event
        data: Dictionary containing event-specific data
        timestamp: Optional timestamp, defaults to now
        
    Returns:
        Created Event object, or None if event type is invalid
    """
    try:
        match event_type:
            case model.EventType.Food:
                new_event = _create_food_event(household_uuid, created_by, data, timestamp)
            case model.EventType.Litter:
                new_event = _create_litter_event(household_uuid, created_by, data, timestamp)
            case model.EventType.Medicine:
                new_event = _create_medicine_event(household_uuid, created_by, data, timestamp)
            case _:
                return None

        model.db.session.add(new_event)
        model.db.session.commit()
        return new_event
    except Exception as e:
        model.db.session.rollback()
        raise


    



