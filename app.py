#Astra Noronha M00909675 PDE3823
#backend of the website using flask to integrate 
#here is where the main function of the chatbot logic are taken from
from flask import Flask, render_template, request, jsonify, session, g, redirect, url_for
import sqlite3
import datetime
import interview_logic
import random
import json
import nlp_processing
import os
import uuid
import eye_contact_calculator
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "OLRoiKV7lSxdp17s"
DATABASE = "interview_data.db"

if not os.path.exists('temp_videos'):
    os.makedirs('temp_videos')

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def init_db():
    print("Initializing database...") #debug line
    with app.app_context():
        db = get_db()
        try:
            with app.open_resource('schema.sql', mode='r') as f:
                db.cursor().executescript(f.read())
            db.commit()
            print("Database initialized successfully.") #debug line
        except Exception as e:
            print(f"Error initializing database: {e}") #debug line

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Login code:
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user_data = cursor.fetchone()
        print(f"Login attempt: Email={email}, User data={user_data}") #debug line
        if user_data and check_password_hash(user_data['password'], password):
            user = User(user_data['user_id'], user_data['email'], user_data['password'])
            login_user(user)
            return redirect(url_for('index'))
        else:
            return "Invalid email or password"
    return render_template('login.html')

# Initialize login_manager AFTER the login route is defined
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    if user:
        return User(user['user_id'], user['email'], user['password'])
    return None

# Class for users:
class User(UserMixin):
    def __init__(self, user_id, email, password_hash):
        self.id = user_id
        self.email = email
        self.password_hash = password_hash
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, hashed_password))
            db.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return "Email already registered"
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('front_page'))  # Redirect to front_page

@app.route('/front_page')
def front_page():
    print(url_for('static', filename='favicon.ico'))
    return render_template('front_page.html')

@app.route('/dashboard')
@login_required
def dashboard():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT session_id, timestamp FROM interviews ORDER BY timestamp DESC")
    sessions = cursor.fetchall()
    return render_template('dashboard.html', sessions=sessions)

@app.route('/session/<int:session_id>')
@login_required
def view_session(session_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT interview_analysis, timestamp, session_id, eye_contact FROM interviews WHERE session_id = ?", (session_id,))
    result = cursor.fetchone()
    if result and result['interview_analysis']:
        try:
            analysis = json.loads(result['interview_analysis'])
            eye_contact = result['eye_contact']  # Get the eye_contact value
            return render_template('session_details.html', analysis=analysis, session=result, eye_contact=eye_contact) #Pass eye_contact
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}")
            return "Error decoding session analysis."
    else:
        return "Session not found or analysis data is missing."

@app.route("/", methods=["GET", "POST"])
def index():
    if current_user.is_authenticated:
        if request.method == "POST":
            session["num_questions"] = int(request.form["num_questions"]) * 5
            print(session["num_questions"])
            session["category_id"] = int(request.form["category_id"])
            session["answers"] = []
            session["question_index"] = 0
            session["asked_questions"] = []
            session["session_id"] = random.randint(1, 100000)
            print(f"Session Answers initialized: {session.get('answers')}")
            return redirect(url_for('ask_question'))
        return render_template("index.html")
    else:
        return redirect(url_for('front_page'))

@app.route("/ask_question", methods=["GET"])
def ask_question():
    if "question_index" not in session:
        return jsonify({"status": "finished", "analysis": {}})

    try:
        category_id = session["category_id"]
        asked_questions = session.get("asked_questions", [])
        question = interview_logic.get_question(category_id, asked_questions)

        if question:
            session["current_question"] = question
            session["asked_questions"] = asked_questions + [question]
            return jsonify({"question": question})
        else:
            return jsonify({"question": None})

    except Exception as e:
        print(f"Error in ask_question: {e}")
        return jsonify({"error": str(e)})


@app.route('/process_video', methods=['POST'])
def process_video():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400

    video_file = request.files['video']
    if video_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if video_file:
        video_filename = str(uuid.uuid4()) + '.webm'
        video_path = os.path.join('temp_videos', video_filename)
        video_file.save(video_path)

        eye_contact_percentage = eye_contact_calculator.detect_eye_contact_ratio(video_path)

        os.remove(video_path)

        return jsonify({'eye_contact_percentage': eye_contact_percentage})

def get_interview_data(session_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT interview_answers FROM interviews WHERE session_id = ?", (session_id,))
    result = cursor.fetchone()
    if result and result['interview_answers']:
        return json.loads(result['interview_answers'])
    return []


def save_interview_data(session_id, data):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("REPLACE INTO interviews (session_id, interview_answers, timestamp) VALUES (?, ?, ?)",
                   (session_id, json.dumps(data), datetime.datetime.now()))
    db.commit()


@app.route("/submit_answer", methods=["POST"])
def submit_answer():
    try:
        data = request.get_json()
        answer = data.get("answer", "")
        question = data.get("question", "")
        eye_contact_percentages = data.get("eye_contact_percentages", []) 
        session['eye_contact_percentages'] = eye_contact_percentages #add this line
        session_id = session.get('session_id')
        answers = get_interview_data(session_id)
        answers.append({"question": question, "answer": answer})
        save_interview_data(session_id, answers)

        # Increment question index
        session["question_index"] = session.get("question_index", 0) + 1

        # Check if it's the last question and end the interview if it is.
        if session["question_index"] >= session["num_questions"]:
            return end_interview()

        return jsonify({"status": "success"})

    except Exception as e:
        print(f"Error in submit_answer: {e}")
        return jsonify({"error": str(e)})

def end_interview():
    session_id = session.get('session_id')
    interview_data = get_interview_data(session_id)
    analysis_results = nlp_processing.process_answers([item['answer'] for item in interview_data])

    for i, result in enumerate(analysis_results):
        if i < len(interview_data):
            result['question'] = interview_data[i]['question']

    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("UPDATE interviews SET interview_analysis = ? WHERE session_id = ?",
                                    (json.dumps(analysis_results), session_id))
        eye_contact_percentages = session.get('eye_contact_percentages', [])
        print(f"Eye contact percentages from session: {eye_contact_percentages}") #debug line
        if eye_contact_percentages:
            eye_contact = sum(eye_contact_percentages) / len(eye_contact_percentages)
            print(f"Calculated eye contact average: {eye_contact}") #debug line
        else:
            eye_contact = 0
        cursor.execute("UPDATE interviews SET eye_contact = ? WHERE session_id = ?", (eye_contact, session_id))
        db.commit()
    except Exception as e:
        print(f"Database error during end interview: {e}")
    session.pop('eye_contact_percentages', None)
    return jsonify({"status": "redirect", "redirect_url": url_for('dashboard')})

@app.route('/process_speech', methods=['POST'])
def process_speech():
    data = request.get_json()
    text = data['text']
    current_question = session.get("current_question")

    submit_answer_data = {
        "answer": text,
        "question": current_question
    }

    try:
        submit_answer() #call submit answer function to save data.
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)})
    
if __name__ == "__main__":
    app.run(debug=True)