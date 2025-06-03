import os
from datetime import datetime
from flask import render_template, request
from pytz import timezone

from . import event_helper
from . import model
from . import pet_helper

app = model.app

@app.route('/')
def home():
  pets = pet_helper.all()

  return render_template("homepage.html", pets=pets)

@app.route('/events', methods=['GET', 'POST'])
def show_events():
  match request.method:
    case 'GET':
      events = event_helper.all_events()
    case 'POST':
      data = request.form
      event_helper.new(
        event_type=int(data.get('event-type')),
        created_by='admin',
        meta=data.get('meta'),
        pet_uuid=data.get('pet'),
        timestamp=data.get('event-time')
      )
      events = event_helper.all_events()

  return render_template("events.html", events=events)

@app.route('/events/new')
def new_event():
  now = datetime.now(tz=timezone('America/Los_Angeles'))
  pets = pet_helper.all()

  return render_template("new_event.html", now=now.strftime("%Y-%m-%dT%H:%M"), pets=pets)


########################

if __name__ == "__main__":  # pragma: no cover
    model.connect_to_db(app, os.environ.get("DATABASE_URL"))
    print("Connected")
