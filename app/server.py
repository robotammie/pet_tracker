import os
import event_controller
import food_helper
import model
import pet_helper
import user_helper

from datetime import datetime
from flask import redirect, render_template, request, session, send_from_directory, jsonify
from urllib.parse import quote


app = model.app
app.secret_key = 'BAD_SECRET_KEY'

@app.before_request
def load_user_and_household():
    """Load user and household data into session before each request.
    
    This function runs before every request to ensure user and household
    data is available. If no email is in session, redirects to login.
    Handles login POST requests by setting session email from form data.
    """
    # Skip authentication for static files and assets
    if request.path.startswith('/css/') or request.path.startswith('/assets/'):
        return None
    
    # Handle login POST request
    if request.method == 'POST' and request.path == '/' and not session.get('email'):
        email = request.form.get('email', '').strip()
        if email:
            session['email'] = email
        else:
            return render_template("login.html", error="Please enter an email address")
    
    # If still no email in session, show login page
    if not session.get('email'):
        return render_template("login.html")

    session['user'] = user_helper.get_user(session.get('email', None))
    if not session.get('user'):
        session.pop('email', None)  # Clear invalid email from session
        return render_template("login.html", error="User not found")
    
    session['household'] = user_helper.get_household(session.get('user'))
    if not session.get('household'):
        session.pop('email', None)  # Clear email if no household
        return render_template("login.html", error="No household found for user")

#####################################################

@app.route('/', methods=['GET', 'POST'])
def show_events():
    """Events route.
    
    GET: show all events for the household
    POST: handle login (redirects to GET) or create a new event
    """
    household = session.get('household')
    user = session.get('user')
    
    if not household or not user:
        return redirect("/")

     # If POST is a login request (handled by before_request), redirect to GET to show homepage
    if request.method == 'POST' and request.form.get('email'):
        return redirect("/")
    
    match request.method:
        case 'GET':
            try:
                events = event_controller.summary()
                pets = pet_helper.all(household.uuid)
                household_name = household.name
                # Get error or success message from query parameters
                error = request.args.get('error')
                created = request.args.get('created')
                return render_template("events.html", events=events, pets=pets, household_name=household_name, error=error, created=created)
            except Exception as e:
                return render_template("events.html", events=[], pets=[], household_name="", error="Error loading events")
                
        case 'POST':
            data = request.form

            # Make sure event type is an integer.
            try:
                ev_type = int(data.get('event-type'))
            except (ValueError, TypeError):
                return redirect("/?error=Invalid event type")

            # Event time must be in the format YYYY-MM-DDTHH:MM.
            try:
                event_time = datetime.strptime(data.get('event-time'), '%Y-%m-%dT%H:%M')
            except (ValueError, TypeError):
                return redirect("/?error=Invalid event time")

            # If save-food checkbox is checked and this is a food event, save the food
            food_save_error = None
            if ev_type == model.EventType.Food.value and data.get('save-food'):
                food_name = data.get('food-name', '').strip()
                food_type = data.get('food-type', '').strip()
                food_amount = data.get('food-amount', '').strip()
                food_unit = data.get('food-unit', '').strip()
                food_calories = data.get('food-calories', '').strip()

                # Validate food data before saving
                if food_name and food_type and food_amount and food_unit and food_calories:
                    # Check if food with same name already exists
                    if food_helper.exists(household.uuid, food_name):
                        food_save_error = f"Food '{food_name}' already exists and was not saved"
                    else:
                        try:
                            serving_size = float(food_amount)
                            calories = int(food_calories)
                            if serving_size > 0 and calories > 0:
                                food_helper.create(
                                    household_uuid=household.uuid,
                                    name=food_name,
                                    food_type=food_type,
                                    serving_size=serving_size,
                                    unit=food_unit,
                                    calories=calories
                                )
                        except (ValueError, TypeError):
                            # If food data is invalid, continue without saving food
                            pass

            try:
                event_controller.new(
                    household_uuid=household.uuid,
                    event_type=model.EventType(ev_type),
                    created_by=user.uuid,
                    data=data,
                    timestamp=event_time
                )
                # Redirect to GET to prevent double submission on refresh
                # Include food save error if one occurred
                if food_save_error:
                    return redirect(f"/?created=1&error={quote(food_save_error)}")
                return redirect("/?created=1")
            except Exception as e:
                # On error, still redirect but with error message
                # Include food save error if one occurred
                if food_save_error:
                    return redirect(f"/?error={quote(f'Error creating event: {food_save_error}')}")
                return redirect("/?error=Error creating event")


@app.route('/events/all', methods=['GET'])
def show_events_all():
  """
  GET: show all events
  """
  user = session.get('user')
  household = session.get('household')
  
  if not household or not user:
      return redirect("/")
  
  try:
      events = event_controller.all_events()
      pets = pet_helper.all(household.uuid)
      household_name = household.name
      error = request.args.get('error')
      created = request.args.get('created')
      return render_template("events_all.html", events=events, pets=pets, household_name=household_name, error=error, created=created)
  except Exception as e:
      return render_template("events_all.html", events=[], pets=[], household_name="", error="Error loading events")


@app.route('/events/day', methods=['GET'])
def show_events_day():
    """Day view route.
    
    GET: show events for multiple days starting from today
    """
    household = session.get('household')
    if not household:
        return redirect("/")
    
    try:
        pets = pet_helper.all(household.uuid)
        household_name = household.name
        # Load initial days (first 5 days with data)
        initial_days = event_controller.days_view(datetime.now(tz=model.APP_TIMEZONE), limit=5)
        return render_template("events_day.html", days=initial_days, pets=pets, household_name=household_name)
    except Exception as e:
        return render_template("events_day.html", days=[], pets=[], household_name="", error="Error loading day view")


@app.route('/api/events/days', methods=['GET'])
def api_events_days():
    """API endpoint for infinite scroll.
    
    GET: returns JSON with events for days starting from a given date
    Query params:
        - start_date: ISO date string (YYYY-MM-DD), defaults to today
        - limit: number of days to return, defaults to 5
    """
    household = session.get('household')
    if not household:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        # Get start_date from query params, default to today
        start_date_str = request.args.get('start_date')
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            start_date = start_date.replace(tzinfo=model.APP_TIMEZONE)
        else:
            start_date = datetime.now(tz=model.APP_TIMEZONE)
        
        # Get limit from query params, default to 5
        limit = int(request.args.get('limit', 5))
        
        days = event_controller.days_view(start_date, limit=limit)
        return jsonify({'days': days})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


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
        foods = food_helper.all(household.uuid)
        return render_template("new_event.html", now=now.strftime("%Y-%m-%dT%H:%M"), pets=pets, foods=foods)
    except Exception as e:
        return render_template("new_event.html", now=datetime.now(tz=model.APP_TIMEZONE).strftime("%Y-%m-%dT%H:%M"), 
                              pets=[], foods=[], error="Error loading form")


@app.route('/pets', methods=['GET', 'POST'])
def home():
    """Homepage route.
    
    GET: show all pets for the household
    POST: handle login (redirects to GET) or create a new pet (not yet implemented)
    """
    household = session.get('household')
    if not household:
        return redirect("/")

    # GET request or POST for creating pet
    try:
        pets = pet_helper.all(household.uuid)
        return render_template("homepage.html", household_name=household.name, pets=pets)
    except Exception as e:
        return render_template("homepage.html", pets=[], household_name=household.get('name', ''), error="Error loading pets")


@app.route('/logout')
def logout():
    """Log out the user.
    
    Clears session data and redirects to home.
    """
    session.clear()
    return redirect("/")


@app.route('/assets/<path:filename>')
def serve_assets(filename):
    """Serve static assets from the assets folder."""
    import os
    assets_dir = os.path.join(os.path.dirname(__file__), 'assets')
    return send_from_directory(assets_dir, filename)


@app.route('/css/<path:filename>')
def serve_css(filename):
    """Serve CSS files from the templates folder."""
    import os
    app_dir = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(app_dir, 'templates')
    return send_from_directory(templates_dir, filename)


########################

if __name__ == "__main__":  # pragma: no cover
    model.connect_to_db(app, os.environ.get("DATABASE_URL"))
