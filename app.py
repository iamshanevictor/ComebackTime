import os
import json
from flask import Flask, render_template, request, redirect, url_for
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

app = Flask(__name__)

# 1. Initialize Firebase using environment variable (or JSON file if you prefer).
firebase_config_json = os.environ.get("FIREBASE_CONFIG")
if not firebase_config_json:
    raise ValueError("FIREBASE_CONFIG environment variable is not set.")

firebase_config = json.loads(firebase_config_json)
cred = credentials.Certificate(firebase_config)
firebase_admin.initialize_app(cred)

db = firestore.client()

@app.route('/', methods=['GET'])
def countdown_and_comments():
    """
    Displays the countdown and existing comments.
    """
    # Countdown logic
    doc_ref = db.collection('countdown').document('target_time')
    doc = doc_ref.get()
    if doc.exists:
        target_date = doc.to_dict().get('target_date')
        target_date_str = target_date.strftime('%Y-%m-%dT%H:%M:%S')
    else:
        target_date_str = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    
    # Fetch comments from Firestore, ordered by timestamp descending (optional).
    comments_ref = db.collection('comments').order_by('timestamp', direction=firestore.Query.DESCENDING)
    comments_snapshot = comments_ref.stream()
    
    comments = []
    for c in comments_snapshot:
        c_dict = c.to_dict()
        # Each comment doc might have fields: name, message, upvotes, timestamp
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
    Handles new comment form submission.
    """
    name = request.form.get('name', '').strip()
    message = request.form.get('message', '').strip()
    
    # Default to "Anonymous" if no name provided
    if not name:
        name = "Anonymous"
    
    if message:
        # Create a new document in Firestore with the provided name, message, and default upvotes = 0
        db.collection('comments').add({
            'name': name,
            'message': message,
            'upvotes': 0,
            'timestamp': datetime.now()
        })
    
    # Redirect back to the main page
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
