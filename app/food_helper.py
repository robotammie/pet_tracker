import model
from sqlalchemy import select
from typing import Any

def all(household_uuid: str) -> list[dict[str, Any]]:
    """Get all FoodMeta items for a household.
    
    Args:
        household_uuid: UUID of the household
        
    Returns:
        List of dictionaries containing food metadata
    """
    food_data = model.db.session.execute(
        select(model.FoodMeta).where(model.FoodMeta.household_uuid == household_uuid)
    ).all()

    foods = []
    for row in food_data:
        for food in row:
            foods.append({
                'uuid': food.uuid,
                'name': food.name,
                'type': food.type.value,
                'serving_size': food.serving_size,
                'unit': food.unit.value,
                'calories': food.calories,
            })

    return foods

