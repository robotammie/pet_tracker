import os

from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, DateTime, JSON, ForeignKey, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime
from enum import Enum
from typing import Any


app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False     # Sessions expire when the browser is closed
app.config["SESSION_TYPE"] = "filesystem"
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_RECORD_QUERIES'] = True
app.config['SQLALCHEMY_ECHO'] = True

Session(app)
db = SQLAlchemy(app)
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

class Species(Enum):
  CAT = 1
  DOG = 2

class EventType(Enum):
  Food = 1
  Litter = 2
  Medicine = 3

class Base(DeclarativeBase):
    pass

db.Model.registry.update_type_annotation_map(
  {
    datetime: DateTime(timezone=True),
    dict[str, Any]: JSON
  }
)

#####################################################

class AppUser(db.Model):
  uuid: Mapped[str] = mapped_column(String(64), primary_key=True)
  name: Mapped[str] = mapped_column(String(64))
  email: Mapped[str] = mapped_column(String(64), index=True)
  # households:

  def __repr__(self):
    return "<User %s>" % (self.email)

class Household(db.Model):
  uuid: Mapped[str] = mapped_column(String(64), primary_key=True)
  name: Mapped[str] = mapped_column(String(64))
  email: Mapped[str] = mapped_column(String(64), index=True)

  def __repr__(self):
    return "<User %s>" % (self.email)

class Pet(db.Model):
  uuid: Mapped[str] = mapped_column(String(64), primary_key=True)
  species: Mapped[Species]
  name: Mapped[str] = mapped_column(String(64))
  birthdate: Mapped[datetime] = mapped_column(nullable=True)
  photo_addr: Mapped[str] = mapped_column(String(64), nullable=True)

  def __repr__(self):
    return "<Pet %s>"% (self.name)


class PetUser(db.Model):
  id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
  user_id: Mapped[str] = mapped_column(String(64), ForeignKey('app_user.uuid'))
  pet_id: Mapped[str] = mapped_column(String(64), ForeignKey('pet.uuid'))

def __repr__(self):
    return "<PetUser %s - %s>" % (self.user, self.pet)


class Event(db.Model):
  id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
  pet_uuid: Mapped[str] = mapped_column(String(64), ForeignKey('pet.uuid'), nullable=True)
  pet: Mapped["Pet"] = relationship()
  timestamp: Mapped[datetime] = mapped_column(nullable=False)
  type: Mapped[EventType] = mapped_column(nullable=False, index=True)
  meta: Mapped[dict[str, Any]]
  created_at: Mapped[datetime] = mapped_column(nullable=False)
  created_by: Mapped[str] = mapped_column(String(64), ForeignKey('app_user.uuid'), nullable=True)

  def __repr__(self):
    return '<Event %s - %s>' % (self.timestamp, self.type)

###############################################################

def connect_to_db(app, db_uri=None):
  """Connect the database to our Flask app."""
  app.config['SQLALCHEMY_DATABASE_URI'] = db_uri or 'postgresql://pettracker'
  app.config['SQLALCHEMY_ECHO'] = True

  db.app = app
  db.init_app(app)


if __name__ == "__main__":
  connect_to_db(app)
  print('Connected')