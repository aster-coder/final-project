#Astra Noronha M00909675 PDE3823
#backend of the website using flask to integrate 
#here is where the main function of the chatbot logic are taken from
from flask import Flask, render_template, request, jsonify, session, g
import pyodbc
import datetime
import data_handling  # your data handling file
import interview_logic  # your interview logic file

app = Flask(__name__)
app.secret_key = "OLRoiKV7lSxdp17s"

# MSSQL Configuration
MSSQL_SERVER = 'your_mssql_server'  # e.g., 'localhost' or 'your_server_name'
MSSQL_DATABASE = 'your_mssql_database'
MSSQL_USERNAME = 'your_mssql_username'
MSSQL_PASSWORD = 'your_mssql_password'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        try:
            connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={MSSQL_SERVER};DATABASE={MSSQL_DATABASE};UID={MSSQL_USERNAME};PWD={MSSQL_PASSWORD}'
            db = pyodbc.connect(connection_string)
            g._database = db
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Database Error: {sqlstate}")
            return None
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        if db:
            cursor = db.cursor()
            # execute your create table statements.
            with app.open_resource('schema.sql', mode='r') as f:
                for sql in f.read().split(';'):
                    if sql:
                        cursor.execute(sql)
            db.commit()

@app.before_first_request
def create_tables():
    init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/setup_interview', methods=['POST'])
def setup_interview():
    choice = request.form.get('interview_length')
    category_choice = request.form.get('interview_category')

    if choice and category_choice:
        try:
            num_questions = int(choice) * 5
            category_id = int(category_choice)

            session['num_questions'] = num_questions
            session['category_id'] = category_id
            session['current_question_index'] = 0
            session['interview_id'] = None
            session['interview_data'] = {}

            # Create a new interview record
            db = get_db()
            if db:
                cursor = db.cursor()
                cursor.execute("INSERT INTO interviews (interviewLength, interviewCategory, timestamp) VALUES (?, ?, ?)",
                               (num_questions, category_choice, datetime.datetime.now()))
                db.commit()
                session['interview_id'] = cursor.lastrowid

            return jsonify({'status': 'success'})
        except ValueError:
            return jsonify({'status': 'error', 'message': 'Invalid input'}), 400
    else:
        return jsonify({'status': 'error', 'message': 'Missing input'}), 400

@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    question = request.json.get('question')
    answer = request.json.get('answer')
    interview_data = session.get('interview_data', {})
    interview_id = session.get('interview_id')

    if question and answer:
        interview_data[question] = answer
        session['interview_data'] = interview_data

        try:
            analysis = interview_logic.analyze_answer(question, answer)
            interview_data[question + "_analysis"] = analysis
            session['interview_data'] = interview_data

            db = get_db()
            if db:
                cursor = db.cursor()
                cursor.execute("INSERT INTO questions (interviewId, questionText, answer, analysis) VALUES (?, ?, ?, ?)",
                               (interview_id, question, answer, str(analysis)))
                db.commit()

        except Exception as e:
            print(f"Error during analysis or database write: {e}")
            return jsonify({'status': 'error', 'message': f'Analysis failed: {e}'}), 500

        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'error', 'message': 'Missing question or answer'}), 400

@app.route('/get_analysis', methods=['GET'])
def get_analysis():
    interview_data = session.get('interview_data')
    if interview_data:
        return jsonify(interview_data)
    else:
        return jsonify({'status': 'no data'})

if __name__ == '__main__':
    from flask import g
    app.run(debug=True)