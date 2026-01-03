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


def _create_vitals_event(household_uuid: str, created_by: str, data: dict[str, Any], 
                         timestamp: Optional[datetime] = None) -> model.Event:
    """Create a Vitals event.

    Args:
        household_uuid: UUID of the household
        created_by: UUID of the user creating the event
        data: Dictionary containing vitals event data
        timestamp: Optional timestamp, defaults to now

    Returns:
        Event object configured for Vitals type
    """
    event = _create_event_base(household_uuid, created_by, model.EventType.Vitals, data, timestamp)
    event.meta = {
        'weight': data.get('vitals-weight'),
        'weight-unit': data.get('vitals-weight-unit'),
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
    events_raw = model.db.session.execute(
        select(model.Event)
        .join(model.Pet, isouter=True)
        .order_by(model.Event.timestamp.desc())
        .where(model.Event.household_uuid == household_uuid)
    ).all()

    event_data = []
    for row in events_raw:
        for event in row:
            event_data.append({
                'timestamp': event.timestamp,
                'pet-name': event.pet.name if event.pet_uuid and event.pet else '',
                'pet-icon': event.pet.photo_addr if event.pet_uuid and event.pet and event.pet.photo_addr else '',
                'type': event.type.name,
                'meta': event.meta,
            })
    
    return event_data

def summary() -> list[dict[str, Any]]:
    """Get a summary of events for the current user's household.
    
    Returns:
        List of dictionaries containing event information
    """
    if not session.get('user') or not session.get('household'):
        return []
    
    household_uuid = session.get('household').uuid
    events_raw = model.db.session.execute(
        select(model.Event.type, model.Pet.name, model.Pet.photo_addr, model.Event.timestamp, model.Event.meta)
        .distinct(model.Event.type, model.Event.pet_uuid)
        .join(model.Pet, isouter=True)
        .order_by(model.Event.type, model.Event.pet_uuid, model.Event.timestamp.desc())
        .where(model.Event.household_uuid == household_uuid)
    ).all()

    event_data = []
    for row in events_raw:
        delta = datetime.now(tz=model.APP_TIMEZONE) - row.timestamp
        if delta.days > 29:
            time_ago = "weeks ago"
        elif delta.days > 7:
            time_ago = f"{delta.days // 7} weeks ago"
        elif delta.days > 1:
            time_ago = f"{delta.days} days ago"
        elif delta.seconds > 3600:
            time_ago = f"{delta.seconds // 3600} hours ago"
        elif delta.seconds > 60:
            time_ago = f"{delta.seconds // 60} minutes ago"
        else:
            time_ago = f"{delta.seconds} seconds ago"

        event_data.append({
            'type': row.type.name,
            'pet-name': row.name if row.name else '',
            'pet-icon': row.photo_addr if row.photo_addr else '',
            'time_ago': time_ago,
            'meta': row.meta,
        })
    
    return event_data

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
    
    query = (select(model.Event.type, model.Pet.name, model.Pet.photo_addr, model.Event.meta)
             .join(model.Pet, isouter=True)
             .where(model.Event.household_uuid == household_uuid)
             .where(model.Event.timestamp >= start_date)
             .where(model.Event.timestamp < end_date))
    events_raw = model.db.session.execute(query).all()

    event_data: dict[str, Any] = {}
    for event_row in events_raw:
        event_type, pet_name, pet_icon, meta = event_row[0], event_row[1], event_row[2], event_row[3]
        pet_name = pet_name or ''
        
        match event_type:
            case model.EventType.Food:
                if 'Food' not in event_data:
                    event_data['Food'] = {}
                calories = float(meta.get('calories', 0)) if meta else 0
                event_data['Food'][(pet_name, pet_icon)] = event_data['Food'].get((pet_name, pet_icon), 0) + calories
            case model.EventType.Litter:
                if 'Litter' not in event_data:
                    event_data['Litter'] = {}
                event_data['Litter'][(pet_name, pet_icon)] = event_data['Litter'].get((pet_name, pet_icon), 0) + 1
            case model.EventType.Medicine:
                if 'Medicine' not in event_data:
                    event_data['Medicine'] = {}
                event_data['Medicine'][(pet_name, pet_icon)] = event_data['Medicine'].get((pet_name, pet_icon), 0) + 1

    return event_data


def days_view(start_date: datetime, limit: int = 10) -> list[dict[str, Any]]:
    """Get aggregated events for multiple days starting from a given date.
    
    Args:
        start_date: Starting date (will go backwards in time from this date)
        limit: Maximum number of days to return
        
    Returns:
        List of dictionaries, each containing date and events for that day.
        Only includes days that have events. Days are ordered from newest to oldest.
    """
    if not session.get('household'):
        return []
    
    household_uuid = session.get('household').uuid
    days_data = []
    
    # Start from the given date and go backwards
    current_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    
    for _ in range(limit * 2):  # Check up to 2x limit days to find days with data
        if len(days_data) >= limit:
            break
            
        day_start = current_date
        day_end = day_start + timedelta(days=1)
        
        query = (select(model.Event.type, model.Pet.name, model.Pet.photo_addr, model.Event.meta)
                 .join(model.Pet, isouter=True)
                 .where(model.Event.household_uuid == household_uuid)
                 .where(model.Event.timestamp >= day_start)
                 .where(model.Event.timestamp < day_end))
        events_raw = model.db.session.execute(query).all()
        
        # Only include days that have events
        if events_raw:
            event_data: dict[str, Any] = {}
            for event_row in events_raw:
                event_type, pet_name, pet_icon, meta = event_row[0], event_row[1], event_row[2], event_row[3]
                pet_name = pet_name or ''
                
                match event_type:
                    case model.EventType.Food:
                        if 'Food' not in event_data:
                            event_data['Food'] = {}
                        calories = float(meta.get('calories', 0)) if meta else 0
                        event_data['Food'][(pet_name, pet_icon)] = event_data['Food'].get((pet_name, pet_icon), 0) + calories
                    case model.EventType.Litter:
                        if 'Litter' not in event_data:
                            event_data['Litter'] = {}
                        event_data['Litter'][(pet_name, pet_icon)] = event_data['Litter'].get((pet_name, pet_icon), 0) + 1
                    case model.EventType.Medicine:
                        if 'Medicine' not in event_data:
                            event_data['Medicine'] = {}
                        # Store medicine name and dose, not just count
                        medicine_key = (pet_name, pet_icon)
                        if medicine_key not in event_data['Medicine']:
                            event_data['Medicine'][medicine_key] = []
                        medicine_info = {
                            'name': meta.get('name', '') if meta else '',
                            'dose': meta.get('dose', '') if meta else ''
                        }
                        event_data['Medicine'][medicine_key].append(medicine_info)
            
            # Convert tuple keys to JSON-serializable format
            # Use a special delimiter that's unlikely to appear in pet names or paths
            serializable_events: dict[str, Any] = {}
            for event_type, event_data in event_data.items():
                serializable_events[event_type] = {}
                for pet_key, value in event_data.items():
                    # Convert tuple to string key: "pet_name|||pet_icon"
                    pet_name, pet_icon = pet_key
                    key_str = f"{pet_name}|||{pet_icon}"
                    serializable_events[event_type][key_str] = value
            
            # Format date for display
            if current_date.date() == datetime.now(tz=model.APP_TIMEZONE).date():
                date_str = "Today"
            elif current_date.date() == (datetime.now(tz=model.APP_TIMEZONE) - timedelta(days=1)).date():
                date_str = "Yesterday"
            else:
                date_str = current_date.strftime("%b %d")
            
            days_data.append({
                'date': date_str,
                'date_iso': current_date.strftime("%Y-%m-%d"),
                'events': serializable_events
            })
        
        # Move to previous day
        current_date = current_date - timedelta(days=1)
    
    return days_data


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
            case model.EventType.Vitals:
                new_event = _create_vitals_event(household_uuid, created_by, data, timestamp)
            case _:
                return None

        model.db.session.add(new_event)
        model.db.session.commit()
        return new_event
    except Exception as e:
        model.db.session.rollback()
        raise


    



