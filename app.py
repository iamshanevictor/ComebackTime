import os
import json
from flask import Flask, render_template
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

app = Flask(__name__)

# Retrieve the Firebase configuration from the environment variable.
firebase_config_json = os.environ.get("FIREBASE_CONFIG")
if not firebase_config_json:
    raise ValueError("FIREBASE_CONFIG environment variable is not set.")

# Parse the JSON string into a dictionary.
firebase_config = json.loads(firebase_config_json)

# Initialize Firebase Admin SDK with the service account configuration.
cred = credentials.Certificate(firebase_config)
firebase_admin.initialize_app(cred)

# Get Firestore client.
db = firestore.client()

@app.route('/')
def countdown():
    # Access the Firestore document where the target date is stored.
    doc_ref = db.collection('countdown').document('target_time')
    doc = doc_ref.get()

    if doc.exists:
        target_date = doc.to_dict().get('target_date')
        target_date_str = target_date.strftime('%Y-%m-%dT%H:%M:%S')
    else:
        # Fallback to current time if no record is found.
        target_date_str = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    
    return render_template('index.html', target_date_str=target_date_str)

if __name__ == '__main__':
    app.run(debug=True)
