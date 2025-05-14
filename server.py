import os
from flask import Flask, render_template
from model import Pet, Event, connect_to_db
from pet_data import pet_data


app = Flask(__name__)

@app.route('/')
def home():
  pets = pet_data()
  return render_template("homepage.html", pets)

@app.route('/pet/<name>')
def info(name):
  return render_template()

if __name__ == "__main__":  # pragma: no cover
    connect_to_db(app, os.environ.get("DATABASE_URL"))
