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
    match request.method:
      case 'GET':
        if not session.get('email'):
          return render_template("login.html")
      case 'POST':
        session['email'] = request.form['email']
    
    session['user'] = user_helper.get_user(session.get('email', None))


@app.route('/', methods=['GET', 'POST'])
def home():
  user = session.get('user')
  pets = pet_helper.all(user)
  return render_template("homepage.html", pets=pets)


@app.route('/events', methods=['GET', 'POST'])
def show_events():
  user = session.get('user')
  match request.method:
    case 'GET':
      events = event_helper.all_events()
    case 'POST':
      data = request.form
      event_helper.new(
        event_type=int(data.get('event-type')),
        created_by=user.id,
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


@app.route('/logout')
def logout():
  session['email'] = None
  session['user'] = None
  return redirect("/")


########################

if __name__ == "__main__":  # pragma: no cover
    model.connect_to_db(app, os.environ.get("DATABASE_URL"))
    print("Connected")
