#Astra Noronha M00909675 PDE3823
#backend of the website using flask to integrate 
#here is where the main function of the chatbot logic are taken from
from flask import Flask, render_template, request, jsonify, session, g
import sqlite3
import datetime
import data_handling  # your data handling file
import interview_logic  # your interview logic file



app = Flask(__name__)
app.secret_key = "OLRoiKV7lSxdp17s"  # Important for session management
DATABASE = "interview_database.db"
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
        session["answers"] = {}  # Initialize answers
        session["question_index"] = 0
        return ask_question()

    return render_template("index.html")

@app.route("/question", methods=["GET", "POST"])
def ask_question():
    if "num_questions" not in session or "category_id" not in session:
        return "Interview not started. Please go to the home page."

    if session["question_index"] >= session["num_questions"]:
        return finish_interview()

    question = interview_logic.get_question(session["category_id"], session["question_index"])

    if request.method == "POST":
        session["answers"][question] = request.form["answer"]
        session["question_index"] += 1
        return ask_question()

    return render_template("question.html", question=question)

@app.route("/finish")
def finish_interview():
    if "answers" not in session:
        return "Interview not completed."

    data_handling.create_table_if_not_exists()

    for question, answer in session["answers"].items():
        data_handling.insert_answer(question, answer)

    interview_logic.run_analysis(session["answers"])

    answers, analysis = data_handling.get_interview_data()

    if answers and analysis:
        analysis_results = []
        for question, answer in answers.items():
            if "_analysis" not in question:
                current_analysis = analysis.get(question + "_analysis", {})

                analysis_data = {
                    "question": question,
                    "answer": answer,
                    "matched_keywords": ', '.join(current_analysis.get('matched_keywords', []) or ['None']),
                    "keyword_match_score": current_analysis.get('keyword_match_score', 0),
                    "sentiment": current_analysis.get('sentiment', {}),
                    "answer_length": current_analysis.get('answer_length', 0),
                    "advice_given": False,
                    "advice": [],
                }
                if current_analysis.get('keyword_match_score', 0) < len(interview_logic.interview_questions.get(question, []) or []) / 2:
                    analysis_data["advice"].append(f"Your answer to '{question}' could include more relevant keywords...")
                    analysis_data["advice_given"] = True

                if current_analysis.get('sentiment', {}).get('compound', 0) < -0.2:
                    analysis_data["advice"].append(f"Your answer to '{question}' had a somewhat negative tone...")
                    analysis_data["advice_given"] = True

                if current_analysis.get('answer_length', 0) < 20:
                    analysis_data["advice"].append(f"Your answer to '{question}' was quite short...")
                    analysis_data["advice_given"] = True

                if not analysis_data["advice_given"]:
                    analysis_data["advice"].append("Your answer looks good!")

                analysis_results.append(analysis_data)
        return render_template("results.html", analysis_results=analysis_results)
    else:
        return "No interview data found."

if __name__ == "__main__":
    app.run(debug=True)