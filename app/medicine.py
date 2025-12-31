import model
import uuid
from sqlalchemy import select
from typing import Any

def all(household_uuid: str) -> list[dict[str, Any]]:
    """Get all MedicineMeta items for a household.
    
    Args:
        household_uuid: UUID of the household
        
    Returns:
        List of dictionaries containing medicine metadata
    """
    medicines_raw = model.db.session.execute(
        select(model.MedicineMeta).where(model.MedicineMeta.household_uuid == household_uuid)
    ).all()

    medicines = []
    for row in medicines_raw:
        for med in row:
            medicines.append({
                'uuid': med.uuid,
                'name': med.name,
            })

    return medicines


def exists(household_uuid: str, name: str) -> bool:
    """Check if a medicine with the given name already exists for a household.

    Args:
        household_uuid: UUID of the household
        name: Name of the medicine to check

    Returns:
        True if a medicine with this name exists, False otherwise
    """
    medicine_data = model.db.session.execute(
        select(model.MedicineMeta).where(
            model.MedicineMeta.household_uuid == household_uuid,
            model.MedicineMeta.name == name
        )
    ).first()

    return medicine_data is not None


def create(household_uuid: str, name: str) -> model.MedicineMeta:
    """Create a new MedicineMeta item.
    
    Args:
        household_uuid: UUID of the household
        name: Name of the medicine
        
    Returns:
        Created MedicineMeta object
    """
    medicine = model.MedicineMeta()
    medicine.uuid = str(uuid.uuid4())
    medicine.household_uuid = household_uuid
    medicine.name = name
    
    model.db.session.add(medicine)
    model.db.session.commit()
    return medicine

