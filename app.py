from flask import Flask, render_template
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

app = Flask(__name__)

# Initialize Firebase using the service account key JSON file.
cred = credentials.Certificate("firebase-adminsdk.json")  # Adjust path if necessary.
firebase_admin.initialize_app(cred)

# Get Firestore client.
db = firestore.client()

@app.route('/')
def countdown():
    # Access the Firestore collection and document where the target date is stored.
    doc_ref = db.collection('countdown').document('target_time')
    doc = doc_ref.get()

    if doc.exists:
        # The target_date field should be stored as a Firestore Timestamp.
        target_date = doc.to_dict().get('target_date')
        # Convert Firestore Timestamp to a Python datetime object if needed.
        # Assuming target_date is already a datetime object, otherwise use .to_datetime().
        target_date_str = target_date.strftime('%Y-%m-%dT%H:%M:%S')
    else:
        # Fallback: use current time if no record is found.
        target_date_str = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    
    return render_template('index.html', target_date_str=target_date_str)

if __name__ == '__main__':
    app.run(debug=True)
