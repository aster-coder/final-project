#Astra Noronha M00909675 PDE3823
#backend of the website using flask to integrate 
#here is where the main function of the chatbot logic are taken from
from flask import Flask, render_template, request, jsonify, session, g,redirect, url_for
import sqlite3
import datetime
import data_handling  # your data handling file
import interview_logic  # your interview logic file
import random
import json
import nlp_processing

app = Flask(__name__)
app.secret_key = "OLRoiKV7lSxdp17s"
DATABASE = "interview_data.db"  # Use the same database

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

@app.route("/", methods=["GET", "POST"])
def index():
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


@app.route("/ask_question", methods=["GET"])
def ask_question():
    if "question_index" not in session:
        return jsonify({"status": "finished", "analysis": {}})

    if session["question_index"] > session["num_questions"]:
        session_id = session.get('session_id')
        answers = get_interview_data(session_id)
        analysis_results = nlp_processing.process_answers(answers)
        db = get_db()
        cursor = db.cursor()
        cursor.execute("UPDATE interviews SET interview_analysis = ? WHERE session_id = ?", (json.dumps(analysis_results), session_id))
        db.commit()
        return jsonify({"status": "finished", "analysis": analysis_results})

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
    cursor.execute("REPLACE INTO interviews (session_id, interview_answers, timestamp) VALUES (?, ?, ?)", (session_id, json.dumps(data), datetime.datetime.now()))
    db.commit()

@app.route("/submit_answer", methods=["POST"])
def submit_answer():
    try:
        data = request.get_json()
        answer = data["answer"]
        session_id = session.get('session_id')
        answers = get_interview_data(session_id) #get existing answers
        answers.append(answer) #append new answer
        save_interview_data(session_id, answers) #save updated answers
        return jsonify({"status": "success"})
    except Exception as e:
        print(f"Error in submit_answer: {e}")
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)