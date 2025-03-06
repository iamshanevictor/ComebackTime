import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Use the DATABASE_URL environment variable provided by Render
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Model for the target time
class TargetTime(db.Model):
    __tablename__ = 'target_time'
    id = db.Column(db.Integer, primary_key=True)
    target_date = db.Column(db.DateTime, nullable=False)

@app.route('/')
def countdown():
    record = TargetTime.query.first()
    if record:
        target_date_str = record.target_date.strftime('%Y-%m-%dT%H:%M:%S')
    else:
        # Fallback: use current time
        target_date_str = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    return render_template('index.html', target_date_str=target_date_str)

if __name__ == '__main__':
    app.run(debug=True)
