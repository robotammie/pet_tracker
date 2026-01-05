from typing import Any
from flask import session
import model
from sqlalchemy import select

def all() -> list[dict[str, Any]]:
    """Get all saved events for the current user's household.
    
    Returns:
        List of dictionaries containing saved event information
    """
    if not session.get('user') or not session.get('household'):
        return []
    
    household_uuid = session.get('household').uuid
    saved_events_raw = model.db.session.execute(
        select(model.SavedEvent, model.Pet)
        .join(model.Pet, isouter=True)
        .where(model.SavedEvent.household_uuid == household_uuid)
    ).all()

    event_data = []
    for event, pet in saved_events_raw:
        event_data.append({
            'uuid': event.uuid,
            'name': event.name,
            'event-type': event.type.name,
            'pet-name': pet.name if pet and pet.name else '',
            'pet-icon': pet.photo_addr if pet and pet.photo_addr else '',
            'pet-uuid': pet.uuid if pet and pet.uuid else None,
        })

    return event_data
