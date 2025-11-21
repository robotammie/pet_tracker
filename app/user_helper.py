import model

from flask import session
from sqlalchemy import select
from sqlalchemy.orm import Session
from time import sleep


def get_user(email: str) -> model.AppUser:
    with Session(model.engine) as s:
        stmt = select(model.AppUser).where(model.AppUser.email == email)
        resp = s.execute(stmt).first()
        user = resp[0] if resp else None
    return user