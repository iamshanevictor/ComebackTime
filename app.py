from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Update with your PostgreSQL credentials:
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost:5432/countdown_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define a model that reflects the target_time table
class TargetTime(db.Model):
    __tablename__ = 'target_time'
    id = db.Column(db.Integer, primary_key=True)
    target_date = db.Column(db.DateTime, nullable=False)

@app.route('/')
def countdown():
    # Retrieve the first record from the target_time table.
    record = TargetTime.query.first()
    if record:
        target_date_str = record.target_date.strftime('%Y-%m-%dT%H:%M:%S')
    else:
        # Fallback to the current time if no record is found.
        target_date_str = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    
    return render_template('index.html', target_date_str=target_date_str)

if __name__ == '__main__':
    app.run(debug=True)
