from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_cors import CORS
import os
import base64
import face_recognition
import numpy as np
import cv2
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'secret_key_for_session_tracking'
CORS(app)

UPLOAD_FOLDER = "registered_users"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Dummy elections data
elections = {
    "election1": {
        "name": "Student Council Election",
        "start_time": datetime.now(),
        "end_time": datetime.now() + timedelta(minutes=5),
        "options": {
            "option1": {"name": "Alice"},
            "option2": {"name": "Bob"}
        }
    },
    "election2": {
        "name": "Club President Election",
        "start_time": datetime.now(),
        "end_time": datetime.now() + timedelta(minutes=8),
        "options": {
            "option1": {"name": "Charlie"},
            "option2": {"name": "Diana"}
        }
    }
}

votes = {
    "election1": {"option1": 0, "option2": 0},
    "election2": {"option1": 0, "option2": 0}
}

@app.route('/')
def home():
    return redirect('/signup')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    return render_template('dashboard.html', elections=elections)

@app.route('/save-face', methods=['POST'])
def save_face():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    image_data = data.get("image")

    if not name or not email or not password or not image_data:
        return jsonify({"success": False, "message": "Missing fields"}), 400

    image_data = image_data.split(",")[1]
    image_bytes = base64.b64decode(image_data)
    file_path = os.path.join(UPLOAD_FOLDER, f"{name}.jpg")
    with open(file_path, "wb") as f:
        f.write(image_bytes)

    info_path = os.path.join(UPLOAD_FOLDER, f"{name}.txt")
    with open(info_path, "w") as f:
        f.write(f"{name},{email},{password}")

    return jsonify({"success": True, "message": "User registered successfully!"})

@app.route('/verify-face', methods=['POST'])
def verify_face():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    image_data = data.get("image")

    if not email or not password or not image_data:
        return jsonify({"success": False, "message": "Missing credentials or image"}), 400

    image_data = image_data.split(",")[1]
    image_bytes = base64.b64decode(image_data)
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    input_encodings = face_recognition.face_encodings(img)
    if not input_encodings:
        return jsonify({"success": False, "message": "No face detected"}), 400

    input_encoding = input_encodings[0]

    for filename in os.listdir(UPLOAD_FOLDER):
        if filename.endswith(".txt"):
            user_txt_path = os.path.join(UPLOAD_FOLDER, filename)
            with open(user_txt_path, "r") as f:
                saved_name, saved_email, saved_password = f.read().split(",")
                if email == saved_email and password == saved_password:
                    image_path = os.path.join(UPLOAD_FOLDER, f"{saved_name}.jpg")
                    if os.path.exists(image_path):
                        known_image = face_recognition.load_image_file(image_path)
                        encodings = face_recognition.face_encodings(known_image)
                        if encodings and face_recognition.compare_faces([encodings[0]], input_encoding)[0]:
                            session['user'] = email
                            return jsonify({"success": True, "redirect": "/dashboard"})

    return jsonify({"success": False, "message": "Login failed: face or credentials mismatch"})

@app.route('/election/<election_id>')
def election_page(election_id):
    if 'user' not in session:
        return redirect('/login')

    election = elections.get(election_id)
    if not election:
        return "Election not found", 404

    total_votes = sum(votes[election_id].values())
    end_time_str = election["end_time"].strftime("%Y-%m-%d %H:%M:%S")
    now = datetime.now()
    total_seconds = (election["end_time"] - election["start_time"]).total_seconds()
    remaining_seconds = max(0, (election["end_time"] - now).total_seconds())
    percent_time_left = max(0, int((remaining_seconds / total_seconds) * 100))

    return render_template("election.html",
                           election=election,
                           election_id=election_id,
                           votes=votes[election_id],
                           total_votes=total_votes,
                           end_time=end_time_str,
                           percent_left=percent_time_left)

@app.route('/vote', methods=['POST'])
def vote():
    data = request.json
    election_id = data.get("election_id")
    option_id = data.get("option")

    if 'user' not in session:
        return jsonify({"success": False, "message": "User not logged in"}), 401

    if session.get(f'voted_{election_id}'):
        return jsonify({"success": False, "message": "You have already voted in this election."}), 403

    election = elections.get(election_id)
    if not election:
        return jsonify({"success": False, "message": "Invalid election"}), 400

    if datetime.now() > election["end_time"]:
        return jsonify({"success": False, "message": "Voting period has ended"}), 403

    if option_id in votes[election_id]:
        votes[election_id][option_id] += 1
        session[f'voted_{election_id}'] = True
        return jsonify({"success": True, "message": "Vote submitted!"})
    return jsonify({"success": False, "message": "Invalid option"}), 400

@app.route('/get-votes/<election_id>')
def get_votes(election_id):
    return jsonify(votes.get(election_id, {}))

if __name__ == '__main__':
    app.run(debug=True)
