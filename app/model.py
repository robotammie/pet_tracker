import os

from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Float, Integer, String, DateTime, JSON, ForeignKey, Boolean, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime
from enum import Enum
from typing import Any
from pytz import timezone

# Configuration constants
APP_TIMEZONE = timezone(os.environ.get('APP_TIMEZONE', 'America/Los_Angeles'))


app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False     # Sessions expire when the browser is closed
app.config["SESSION_TYPE"] = "filesystem"
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_RECORD_QUERIES'] = True
app.config['SQLALCHEMY_ECHO'] = os.environ.get('SQLALCHEMY_ECHO', 'False').lower() == 'true'

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
  Vitals = 4

class VitalsType(Enum):
  Weight = 1
  Length = 2
class Unit(Enum):
  GRAMS = 'grams'
  CUPS = 'cups'
  OZ = 'oz'
  CANS = 'cans'

  def singularize(self, amt):
    if amt != 1:
      return self.value
    elif self == Unit.OZ:
      return 'oz'
    elif self == Unit.GRAMS:
      return 'gram'
    elif self == Unit.CUPS:
      return 'cup'
    elif self == Unit.CANS:
      return 'can'


class FoodType(Enum):
  WET = 'wet'
  DRY = 'dry'
  TREATS = 'treats'
  OTHER = 'other'

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
    """User model representing an application user."""
    uuid: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(64))
    email: Mapped[str] = mapped_column(String(64), index=True)
    # households:

    def __repr__(self):
        return "<User %s>" % (self.email)

class Household(db.Model):
    """Household model representing a group of users and pets."""
    uuid: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(64))
    email: Mapped[str] = mapped_column(String(64), index=True)

    def __repr__(self):
        return "<Household %s>" % (self.name)

class Pet(db.Model):
    """Pet model representing a pet in a household."""
    uuid: Mapped[str] = mapped_column(String(64), primary_key=True)
    household_uuid: Mapped[str] = mapped_column(String(64), ForeignKey('household.uuid'), nullable=True)
    household: Mapped["Household"] = relationship()
    species: Mapped[Species]
    name: Mapped[str] = mapped_column(String(64))
    birthdate: Mapped[datetime] = mapped_column(nullable=True)
    photo_addr: Mapped[str] = mapped_column(String(64), nullable=True)

    def __repr__(self):
        return "<Pet %s>" % (self.name)


class UserHousehold(db.Model):
    """Join table linking users to households (many-to-many relationship)."""
    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    user_id: Mapped[str] = mapped_column(String(64), ForeignKey('app_user.uuid'))
    user: Mapped["AppUser"] = relationship()
    household_id: Mapped[str] = mapped_column(String(64), ForeignKey('household.uuid'))
    household: Mapped["Household"] = relationship()

    def __repr__(self):
        return "<UserHousehold %s - %s>" % (self.user, self.household)


class Event(db.Model):
    """Event model representing care activities (feeding, litter, medicine, etc.)."""
    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    household_uuid: Mapped[str] = mapped_column(String(64), ForeignKey('household.uuid'), nullable=False)
    household: Mapped["Household"] = relationship()
    pet_uuid: Mapped[str] = mapped_column(String(64), ForeignKey('pet.uuid'), nullable=True)
    pet: Mapped["Pet"] = relationship()
    timestamp: Mapped[datetime] = mapped_column(nullable=False)
    type: Mapped[EventType] = mapped_column(nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False)
    created_by: Mapped[str] = mapped_column(String(64), ForeignKey('app_user.uuid'), nullable=True)
    created_by_user: Mapped["AppUser"] = relationship()

    def __repr__(self):
        return '<Event %s - %s>' % (self.type, self.timestamp)


class SavedEvent(db.Model):
    """Event model representing saved events that can be quick-logged."""
    uuid: Mapped[str] = mapped_column(String(64), primary_key=True)
    household_uuid: Mapped[str] = mapped_column(String(64), ForeignKey('household.uuid'), nullable=False)
    household: Mapped["Household"] = relationship()
    pet_uuid: Mapped[str] = mapped_column(String(64), ForeignKey('pet.uuid'), nullable=True)
    pet: Mapped["Pet"] = relationship()
    type: Mapped[EventType] = mapped_column(nullable=False, index=True)
    meta: Mapped[dict[str, Any]]

    def __repr__(self):
        return '<Event %s - %s>' % (self.type, self.meta)


class FoodEvent(db.Model):
    """Food metadata model storing nutritional information for food items."""
    uuid: Mapped[str] = mapped_column(String(64), primary_key=True)
    event_id: Mapped[int] = mapped_column(Integer, ForeignKey('event.id'))
    event: Mapped["Event"] = relationship()
    name: Mapped[str] = mapped_column(String(64))
    type: Mapped[FoodType] = mapped_column(nullable=False)
    serving_size: Mapped[float] = mapped_column(Float)
    unit: Mapped[Unit] = mapped_column(nullable=False)
    calories: Mapped[int] = mapped_column(Integer)

    def __repr__(self):
        return f"<FoodEvent {self.name} - {self.type.value}>"

    def to_dict(self):
        return {
            'name': self.name,
            'type': self.type.value,
            'serving_size': self.serving_size,
            'unit': self.unit.value,
            'calories': self.calories,
        }


class MedicineEvent(db.Model):
    """Food metadata model storing nutritional information for food items."""
    uuid: Mapped[str] = mapped_column(String(64), primary_key=True)
    event_id: Mapped[int] = mapped_column(Integer, ForeignKey('event.id'))
    event: Mapped["Event"] = relationship()
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    dose: Mapped[str] = mapped_column(String(64), nullable=False)

    def __repr__(self):
        return f"<MedicineEvent {self.name}>"

    def to_dict(self):
        return {
            'name': self.name,
            'dose': self.dose,
        }

class VitalsEvent(db.Model):
    """Food metadata model storing nutritional information for food items."""
    uuid: Mapped[str] = mapped_column(String(64), primary_key=True)
    event_id: Mapped[int] = mapped_column(Integer, ForeignKey('event.id'))
    event: Mapped["Event"] = relationship()
    type: Mapped[VitalsType] = mapped_column(nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)

    def __repr__(self):
        return f"<VitalsEvent {self.type.value} - {self.value}>"

    def to_dict(self):
        return {
            'type': self.type.name,
            'value': self.value,
        }


class FoodMeta(db.Model):
    """Food metadata model storing nutritional information for food items."""
    uuid: Mapped[str] = mapped_column(String(64), primary_key=True)
    household_uuid: Mapped[str] = mapped_column(String(64), ForeignKey('household.uuid'))
    household: Mapped["Household"] = relationship()
    name: Mapped[str] = mapped_column(String(64))
    type: Mapped[FoodType] = mapped_column(nullable=False)
    serving_size: Mapped[float] = mapped_column(Float)
    unit: Mapped[Unit] = mapped_column(nullable=False)
    calories: Mapped[int] = mapped_column(Integer)
    archived: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    def calorie_count(self, amt: float) -> int:
        """Calculate calories for a given amount of food.
        
        Args:
            amt: Amount of food
            
        Returns:
            Calculated calorie count
        """
        return int(self.calories * amt / self.serving_size)

    def __repr__(self):
        return f"<FoodMeta {self.name} - {self.type.value}>"

class MedicineMeta(db.Model):
    """Medicine metadata model storing information for medicine items."""
    uuid: Mapped[str] = mapped_column(String(64), primary_key=True)
    household_uuid: Mapped[str] = mapped_column(String(64), ForeignKey('household.uuid'))
    household: Mapped["Household"] = relationship()
    name: Mapped[str] = mapped_column(String(64))
    archived: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    def __repr__(self):
        return f"<MedicineMeta {self.name}>"

###############################################################

def connect_to_db(app, db_uri=None):
  """Connect the database to our Flask app."""
  app.config['SQLALCHEMY_DATABASE_URI'] = db_uri or 'postgresql://pettracker'
  app.config['SQLALCHEMY_ECHO'] = os.environ.get('SQLALCHEMY_ECHO', 'False').lower() == 'true'

  db.app = app
  db.init_app(app)


if __name__ == "__main__":
  connect_to_db(app)
  print('Connected')