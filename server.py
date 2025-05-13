import os
from flask import Flask, render_template
from model import Pet, Event, connect_to_db, db


app = Flask(__name__)

@app.route('/')
def home():
    return render_template("homepage.html")

if __name__ == "__main__":  # pragma: no cover
    connect_to_db(app, os.environ.get("DATABASE_URL"))
