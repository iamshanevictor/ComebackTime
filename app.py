import os
import json
from flask import Flask, render_template, request, redirect, url_for
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

app = Flask(__name__)

# Attempt to read the Firebase config from an environment variable:
firebase_config_json = os.environ.get("FIREBASE_CONFIG")
if firebase_config_json:
    # Parse JSON string from the environment variable
    firebase_config = json.loads(firebase_config_json)
    cred = credentials.Certificate(firebase_config)
else:
    # Fallback to local JSON file if environment variable is not set
    with open("countdown-b7de7-firebase-adminsdk-fbsvc-ae85cbcd64.json", "r") as f:
        cred = credentials.Certificate(json.load(f))

firebase_admin.initialize_app(cred)
db = firestore.client()

@app.route('/', methods=['GET'])
def countdown_and_comments():
    """
    Displays the countdown timer and existing comments (notes).
    """
    # 1. Fetch the target time for countdown
    doc_ref = db.collection('countdown').document('target_time')
    doc = doc_ref.get()
    if doc.exists:
        target_date = doc.to_dict().get('target_date')
        target_date_str = target_date.strftime('%Y-%m-%dT%H:%M:%S')
    else:
        # Fallback to current time if no document found
        target_date_str = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    
    # 2. Fetch comments from Firestore, ordered by timestamp (descending)
    comments_ref = db.collection('comments').order_by('timestamp', direction=firestore.Query.ASCENDING)
    comments_snapshot = comments_ref.stream()
    
    comments = []
    for c in comments_snapshot:
        c_dict = c.to_dict()
        comments.append({
            'id': c.id,
            'message': c_dict.get('message', ''),
            'name': c_dict.get('name', 'Anonymous'),  # Always "Anonymous"
            'upvotes': c_dict.get('upvotes', 0),
        })

    return render_template(
        'index.html',
        target_date_str=target_date_str,
        comments=comments
    )

@app.route('/add_comment', methods=['POST'])
def add_comment():
    """
    Handles new note submissions.
    """
    message = request.form.get('message', '').strip()
    
    if message:
        # Always store as "Anonymous"
        db.collection('comments').add({
            'name': "Anonymous",
            'message': message,
            'upvotes': 0,
            'timestamp': datetime.now()
        })
    
    return redirect(url_for('countdown_and_comments'))

@app.route('/upvote/<comment_id>', methods=['POST'])
def upvote_comment(comment_id):
    """
    Increments the upvote count for a given comment.
    """
    comment_ref = db.collection('comments').document(comment_id)
    doc = comment_ref.get()
    if doc.exists:
        current_upvotes = doc.to_dict().get('upvotes', 0)
        comment_ref.update({'upvotes': current_upvotes + 1})
    
    return redirect(url_for('countdown_and_comments'))

if __name__ == '__main__':
    app.run(debug=True)

