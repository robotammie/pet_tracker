import model
import uuid
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


def exists(household_uuid: str, name: str) -> bool:
    """Check if a food with the given name already exists for a household.

    Args:
        household_uuid: UUID of the household
        name: Name of the food to check

    Returns:
        True if a food with this name exists, False otherwise
    """
    food_data = model.db.session.execute(
        select(model.FoodMeta).where(
            model.FoodMeta.household_uuid == household_uuid,
            model.FoodMeta.name == name
        )
    ).first()

    return food_data is not None


def create(household_uuid: str, name: str, food_type: str, serving_size: float, 
           unit: str, calories: int) -> model.FoodMeta:
    """Create a new FoodMeta item.
    
    Args:
        household_uuid: UUID of the household
        name: Name of the food
        food_type: Type of food (wet, dry, treats, other)
        serving_size: Serving size amount
        unit: Unit of measurement (grams, cups, oz, cans)
        calories: Calories per serving
        
    Returns:
        Created FoodMeta object
    """
    food = model.FoodMeta()
    food.uuid = str(uuid.uuid4())
    food.household_uuid = household_uuid
    food.name = name
    food.type = model.FoodType(food_type)
    food.serving_size = serving_size
    food.unit = model.Unit(unit)
    food.calories = calories
    
    model.db.session.add(food)
    model.db.session.commit()
    return food

