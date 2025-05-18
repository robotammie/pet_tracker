import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from . import model
from . import pet_data

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

@app.route('/')
def home():
  pets = pet_data.all()

  return render_template("homepage.html", pets=pets)

# @app.route('/pet/<name>')
# def info(name):
#   return render_template()

if __name__ == "__main__":  # pragma: no cover
    model.connect_to_db(app, os.environ.get("DATABASE_URL"))
    print(os.environ.get("DATABASE_URL"))
