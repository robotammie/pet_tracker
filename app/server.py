import os
import event_helper
import model
import pet_helper
import user_helper

from datetime import datetime
from flask import redirect, render_template, request, session


app = model.app
app.secret_key = 'BAD_SECRET_KEY'

@app.before_request
def load_user_and_household():
    """Load user and household data into session before each request.
    
    This function runs before every request to ensure user and household
    data is available. If no email is in session, redirects to login.
    """
    if not session.get('email'):
        return render_template("login.html")

    session['user'] = user_helper.get_user(session.get('email', None))
    if not session.get('user'):
        return render_template("login.html")
    
    session['household'] = user_helper.get_household(session.get('user'))
    if not session.get('household'):
        return render_template("login.html", error="No household found for user")

#####################################################

@app.route('/', methods=['GET', 'POST'])
def home():
    """Homepage route.
    
    GET: show all pets for the household
    POST: create a new pet (not yet implemented)
    """
    household = session.get('household')
    if not household:
        return redirect("/")
    
    try:
        pets = pet_helper.all(household.uuid)
        return render_template("homepage.html", pets=pets)
    except Exception as e:
        return render_template("homepage.html", pets=[], error="Error loading pets")


@app.route('/events', methods=['GET', 'POST'])
def show_events():
    """Events route.
    
    GET: show all events for the household
    POST: create a new event
    """
    household = session.get('household')
    user = session.get('user')
    
    if not household or not user:
        return redirect("/")
    
    match request.method:
        case 'GET':
            try:
                events = event_helper.all_events()
                return render_template("events.html", events=events)
            except Exception as e:
                return render_template("events.html", events=[], error="Error loading events")
                
        case 'POST':
            data = request.form

            # Make sure event type is an integer.
            try:
                ev_type = int(data.get('event-type'))
            except (ValueError, TypeError):
                return render_template("events.html", events=event_helper.all_events(), 
                                     error="Invalid event type")

            # Event time must be in the format YYYY-MM-DDTHH:MM.
            try:
                event_time = datetime.strptime(data.get('event-time'), '%Y-%m-%dT%H:%M')
            except (ValueError, TypeError):
                return render_template("events.html", events=event_helper.all_events(), 
                                     error="Invalid event time")

            try:
                event_helper.new(
                    household_uuid=household.uuid,
                    event_type=model.EventType(ev_type),
                    created_by=user.uuid,
                    data=data,
                    timestamp=event_time
                )
                events = event_helper.all_events()
                return render_template("events.html", events=events)
            except Exception as e:
                return render_template("events.html", events=event_helper.all_events(), 
                                     error="Error creating event")


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
    """Day view route.
    
    GET: show all events for today, aggregated by type
    """
    household = session.get('household')
    if not household:
        return redirect("/")
    
    try:
        events = event_helper.day_view(datetime.now(tz=model.APP_TIMEZONE))
        return render_template("events_day.html", events=events)
    except Exception as e:
        return render_template("events_day.html", events={}, error="Error loading day view")


@app.route('/events/new')
def new_event():
    """New event form route.
    
    GET: show the new event form
    """
    household = session.get('household')
    if not household:
        return redirect("/")
    
    try:
        now = datetime.now(tz=model.APP_TIMEZONE)
        pets = pet_helper.all(household.uuid)
        return render_template("new_event.html", now=now.strftime("%Y-%m-%dT%H:%M"), pets=pets)
    except Exception as e:
        return render_template("new_event.html", now=datetime.now(tz=model.APP_TIMEZONE).strftime("%Y-%m-%dT%H:%M"), 
                              pets=[], error="Error loading form")


@app.route('/logout')
def logout():
    """Log out the user.
    
    Clears session data and redirects to home.
    """
    session.clear()
    return redirect("/")


########################

if __name__ == "__main__":  # pragma: no cover
    model.connect_to_db(app, os.environ.get("DATABASE_URL"))
