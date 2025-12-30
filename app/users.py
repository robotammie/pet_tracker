import model

from flask import session
from sqlalchemy import select
from typing import Optional


def get_user(email: str) -> Optional[model.AppUser]:
    """Get user by email address.
    
    Args:
        email: User's email address
        
    Returns:
        AppUser object if found, None otherwise
    """
    stmt = select(model.AppUser).where(model.AppUser.email == email)
    resp = model.db.session.execute(stmt).first()
    return resp[0] if resp else None


def get_household(user: model.AppUser) -> Optional[model.Household]:
    """Get household associated with a user.
    
    Args:
        user: AppUser object
        
    Returns:
        Household object if found, None otherwise
    """
    if not user:
        return None
    stmt = select(model.Household).join(model.UserHousehold).where(model.UserHousehold.user_id == user.uuid)
    resp = model.db.session.execute(stmt).first()
    return resp[0] if resp else None