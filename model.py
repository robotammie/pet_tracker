from flask_sqlalchemy import SQLAlchemy
from enum import Enum

db = SQLAlchemy()

class Species(Enum):
    CAT = 1

#####################################################

class Pet(db.Model):
    __tablename__ = 'pets'

    species = db.Column(db.Enum(Species), nullable=False)
    name = db.Column(db.String(64), nullable=False)

    def __repr__(self):
        return "<Pet %s>" % (self.name)
    
class Event(db.Model):
    __tablename__ = 'events'

    timestamp = db.Column(db.DateTime(), nullable=False)
    type = db.Column(db.String(64), nullable=False)
    meta = db.Column(db.JSON)
    created_at = db.Column(db.DateTime(), nullable=False)
    created_by = db.Column(db.String(64))

    def __repr__(self):
        return '<Event %s - %s>' (self.timestamp, self.type)

###############################################################

def connect_to_db(app, db_uri=None):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri or "postgresql:///cattracker"
    app.config['SQLALCHEMY_ECHO'] = True
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    from server import app
    connect_to_db(app)
    print('Connected')