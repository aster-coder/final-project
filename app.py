#Astra Noronha M00909675 PDE3823
#backend of the website using flask to integrate 
#here is where the main function of the chatbot logic are taken from
from flask import Flask, render_template, request, jsonify, session, g,redirect, url_for
import sqlite3
import datetime
import data_handling  # your data handling file
import interview_logic  # your interview logic file



app = Flask(__name__)
app.secret_key = "OLRoiKV7lSxdp17s"  # Important for session management
DATABASE = "interview_data.db"
database_initialized = False  # Global variable

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def init_db():
    with app.open_resource('schema.sql', mode='r') as f:
        get_db().executescript(f.read())
    get_db().commit()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.before_request
def before_request_func():
    global database_initialized
    if not database_initialized:
        init_db()
        database_initialized = True


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        session["num_questions"] = int(request.form["num_questions"]) * 5
        session["category_id"] = int(request.form["category_id"])
        session["answers"] = {}
        session["question_index"] = 0
        return redirect(url_for('ask_question')) #Corrected line
    return render_template("index.html")
    
@app.route("/setup_interview", methods=["POST"])
def setup_interview():
    num_questions = int(request.form["num_questions"]) 
    category_id = int(request.form["category_id"])

    session["num_questions"] = num_questions
    session["category_id"] = category_id
    session["question_index"] = 0
    session["answers"] = {}

    return jsonify({"status": "success"})

app.route("/get_question", methods=["GET"])
@app.route("/get_question", methods=["GET"])
def get_question():
    if "question_index" not in session or session["question_index"] >= session["num_questions"]:
        if "answers" in session:
            interview_logic.run_analysis(session["answers"])
        return jsonify({"status": "finished"})

    try:
        category_id = session["category_id"]
        question_index = session["question_index"]
        question = interview_logic.get_question(category_id, question_index)
        session["current_question"] = question
        if question:
            return jsonify({"question": question})
        else:
            return jsonify({"question": None})
    except Exception as e:
        print(f"Error in get_question: {e}")
        return jsonify({"error": str(e)})
    
    
@app.route("/submit_answer", methods=["POST"])
def submit_answer():
    data = request.get_json()
    question = session.get("current_question")
    answer = data.get("answer")

    if question and answer:
        session["answers"][question] = answer
        session["question_index"] += 1
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "error", "message": "Invalid question or answer."})

@app.route("/get_analysis", methods=["GET"])
def get_analysis():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT question, answer FROM answers")
    answers_data = cursor.fetchall()

    cursor.execute("SELECT question, matched_keywords, keyword_match_score, sentiment_pos, sentiment_neg, sentiment_neu, sentiment_compound, answer_length FROM analysis")
    analysis_data = cursor.fetchall()
    conn.close()

    if answers_data and analysis_data:
        answers = {row['question']: row['answer'] for row in answers_data}
        analysis = {}
        for row in analysis_data:
            analysis[row['question'] + '_analysis'] = {
                'matched_keywords': row['matched_keywords'].split(',') if row['matched_keywords'] else [],
                'keyword_match_score': row['keyword_match_score'],
                'sentiment': {
                    'pos': row['sentiment_pos'],
                    'neg': row['sentiment_neg'],
                    'neu': row['sentiment_neu'],
                    'compound': row['sentiment_compound']
                },
                'answer_length': row['answer_length']
            }
        result = {**answers, **analysis}
        return jsonify(result)
    else:
        return jsonify({}) # return empty json if no data.

if __name__ == "__main__":
    app.run(debug=True)