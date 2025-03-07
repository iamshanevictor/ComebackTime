import os
import json
from flask import Flask, render_template, request, redirect, url_for
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

app = Flask(__name__)

# 1. Initialize Firebase: try environment variable first, else local JSON file.
firebase_config_json = os.environ.get("FIREBASE_CONFIG")

if firebase_config_json:
    # Parse the JSON string from the environment variable.
    firebase_config = json.loads(firebase_config_json)
    cred = credentials.Certificate(firebase_config)
else:
    # Fallback to the local service account JSON (not committed to Git).
    with open("firebase-adminsdk.json", "r") as f:
        cred = credentials.Certificate(json.load(f))

firebase_admin.initialize_app(cred)
db = firestore.client()

@app.route('/', methods=['GET'])
def countdown_and_comments():
    """
    Displays the countdown (target_date) and the existing comments.
    """
    # 2. Countdown logic (fetch from Firestore).
    doc_ref = db.collection('countdown').document('target_time')
    doc = doc_ref.get()
    if doc.exists:
        target_date = doc.to_dict().get('target_date')
        target_date_str = target_date.strftime('%Y-%m-%dT%H:%M:%S')
    else:
        # Fallback to the current time if no document is found.
        target_date_str = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    
    # 3. Fetch comments from Firestore, ordered by timestamp descending.
    comments_ref = db.collection('comments').order_by('timestamp', direction=firestore.Query.DESCENDING)
    comments_snapshot = comments_ref.stream()
    
    comments = []
    for c in comments_snapshot:
        c_dict = c.to_dict()
        comments.append({
            'id': c.id,
            'name': c_dict.get('name', 'Anonymous'),
            'message': c_dict.get('message', ''),
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
    Handles new comment submissions from the form.
    """
    name = request.form.get('name', '').strip()
    message = request.form.get('message', '').strip()
    
    # Default to "Anonymous" if no name provided
    if not name:
        name = "Anonymous"
    
    if message:
        db.collection('comments').add({
            'name': name,
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
