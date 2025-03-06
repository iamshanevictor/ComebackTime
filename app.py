from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# Configure SQLAlchemy to use the PostgreSQL database.
# Use the DATABASE_URL environment variable provided by Render (or fallback to local settings)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 'postgresql://timedb_cbrx_user:CQ8zmceiocRuMUu7c1w7lWkJa2pzN7JT@dpg-cv4lfbtds78s73e09vpg-a/timedb_cbrx'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define a model for storing the countdown target date.
class Countdown(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    target_date = db.Column(db.DateTime, nullable=False)

@app.route('/')
def countdown():
    # Retrieve the target date from the database.
    countdown_entry = Countdown.query.first()
    if countdown_entry:
        target_date = countdown_entry.target_date
    else:
        # If no target date is found, calculate a default target date (4 weeks from now)
        target_date = datetime.now() + timedelta(weeks=4)
        # Optionally, create a new entry in the database
        new_entry = Countdown(target_date=target_date)
        db.session.add(new_entry)
        db.session.commit()

    # Format the date to pass to JavaScript in ISO format.
    target_date_str = target_date.strftime('%Y-%m-%dT%H:%M:%S')
    return render_template('index.html', target_date_str=target_date_str)

if __name__ == '__main__':
    app.run(debug=True)
