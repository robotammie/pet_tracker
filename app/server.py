import os
import event_helper
import model
import pet_helper
import user_helper

from datetime import datetime
from flask import redirect, render_template, request, session
from pytz import timezone


app = model.app
app.secret_key = 'BAD_SECRET_KEY'

@app.before_request
def get_user():
    if not session.get('email'):
      return render_template("login.html")

    session['user'] = user_helper.get_user(session.get('email', None))

@app.before_request
def get_household():  # separate from get_user to allow for multiple households per user in future
  session['household'] = user_helper.get_household(session.get('user'))

#####################################################

@app.route('/', methods=['GET', 'POST'])
def home():
  """
  GET: show all pets
  POST: create a new pet
  """
  household = session.get('household')
  pets = pet_helper.all(household.uuid)
  return render_template("homepage.html", pets=pets)


@app.route('/events', methods=['GET', 'POST'])
def show_events():
  """
  GET: show all events
  POST: create a new event
  """
  user = session.get('user')
  match request.method:
    case 'GET':
      events = event_helper.all_events()
    case 'POST':
      data = request.form

      # Make sure event type is an integer.
      try:
        ev_type = int(data.get('event-type'))
      except ValueError:
        return render_template("events.html", error="Invalid event type")

      # Event time must be in the format YYYY-MM-DDTHH:MM.
      try:
        event_time = datetime.strptime(data.get('event-time'), '%Y-%m-%dT%H:%M')
      except ValueError:
        return render_template("events.html", error="Invalid event time")

      event_helper.new(
        household_uuid=session.get('household').uuid,
        event_type=model.EventType(ev_type),
        created_by=session.get('user').uuid,
        data=data,
        timestamp=event_time
      )
      events = event_helper.all_events()

  return render_template("events.html", events=events)


app.route('/events/all', methods=['GET'])
def show_events():
  """
  GET: show all events
  """
  user = session.get('user')
  match request.method:
    case 'GET':
      events = event_helper.all_events()
  
  return render_template("events.html", events=events)


@app.route('/events/day', methods=['GET'])
def show_events_day():
  """
  GET: show all events for a given day
  """
  user = session.get('user')
  match request.method:
    case 'GET':
      events = event_helper.day_view(datetime.now(tz=timezone('America/Los_Angeles')))
  
  print(events)
  return render_template("events_day.html", events=events)


@app.route('/events/new')
def new_event():
  """
  GET: show the new event form
  """
  household = session.get('household')
  now = datetime.now(tz=timezone('America/Los_Angeles'))
  pets = pet_helper.all(household.uuid)

  return render_template("new_event.html", now=now.strftime("%Y-%m-%dT%H:%M"), pets=pets)


@app.route('/logout')
def logout():
  """
  Log out the user
  """
  session['email'] = None
  session['user'] = None
  return redirect("/")


########################

if __name__ == "__main__":  # pragma: no cover
    model.connect_to_db(app, os.environ.get("DATABASE_URL"))
    print("Connected")
