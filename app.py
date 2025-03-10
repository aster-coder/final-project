#Astra Noronha M00909675 PDE3823
#backend of the website using flask to integrate 
#here is where the main function of the chatbot logic are taken from
from flask import Flask, render_template, request, jsonify, session, g, redirect, url_for
import sqlite3
import datetime
import data_handling
import interview_logic
import random
import json
import nlp_processing
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "OLRoiKV7lSxdp17s"
DATABASE = "interview_data.db"

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

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
    return render_template('front_page.html')

@app.route('/dashboard')
@login_required
def dashboard():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT session_id, timestamp FROM interviews")
    sessions = cursor.fetchall()
    return render_template('dashboard.html', sessions=sessions)

@app.route('/session/<int:session_id>')
@login_required
def view_session(session_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT interview_analysis, timestamp, session_id FROM interviews WHERE session_id = ?", (session_id,))
    result = cursor.fetchone()
    if result and result['interview_analysis']:
        try:
            analysis = json.loads(result['interview_analysis'])
            return render_template('session_details.html', analysis=analysis, session=result)
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

    if session["question_index"] > session["num_questions"]:
        session_id = session.get('session_id')
        interview_data = get_interview_data(session_id)
        analysis_results = nlp_processing.process_answers([item['answer'] for item in interview_data])

        # Add questions to the analysis results
        for i, result in enumerate(analysis_results):
            if i < len(interview_data):
                result['question'] = interview_data[i]['question']

        db = get_db()
        cursor = db.cursor()
        cursor.execute("UPDATE interviews SET interview_analysis = ? WHERE session_id = ?",
                        (json.dumps(analysis_results), session_id))
        db.commit()

        return jsonify({"status": "redirect", "redirect_url": url_for('dashboard')}) #redirect to dashboard.
    
    try:
        category_id = session["category_id"]
        asked_questions = session.get("asked_questions", [])
        print(f"Category ID: {category_id}")
        print(f"Asked Questions: {asked_questions}")
        question = interview_logic.get_question(category_id, asked_questions)
        print(f"Returned Question: {question}")

        if question:
            session["current_question"] = question
            session["asked_questions"] = asked_questions + [question]
            session["question_index"] += 1
            return jsonify({"question": question})
        else:
            print("No question returned.")
            return jsonify({"question": None})
    except Exception as e:
        print(f"Error in ask_question: {e}")
        return jsonify({"error": str(e)})


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
        answer = data.get("answer", "") #allow for empty answers.
        question = data.get("question", "")
        session_id = session.get('session_id')
        answers = get_interview_data(session_id)
        answers.append({"question": question, "answer": answer})
        save_interview_data(session_id, answers)
        return jsonify({"status": "success"})
    except Exception as e:
        print(f"Error in submit_answer: {e}")
        return jsonify({"error": str(e)})

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