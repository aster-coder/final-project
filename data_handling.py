import sqlite3
import json
import nlp_processing
import interview_logic

def create_table_if_not_exists():
    conn = sqlite3.connect('interview_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS interview_data (  -- More generic table name
            id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Auto-incrementing ID
            answers TEXT,
            analysis TEXT
        )
    ''')
    conn.commit()
    conn.close()

def store_answer(question, answer):  # No candidate name
    conn = sqlite3.connect('interview_data.db')
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT answers, analysis FROM interview_data ORDER BY id DESC LIMIT 1") # Get the most recent data
        result = cursor.fetchone()

        answers = {}
        analysis = {}

        if result:
            answers_str = result[0]
            analysis_str = result[1]
            try:
                answers = json.loads(answers_str)
                analysis = json.loads(analysis_str)
            except json.JSONDecodeError:
                pass

        answers[question] = answer
        analysis[question + "_analysis"] = nlp_processing.analyze_answer(answer, interview_logic.interview_questions.get(question, []))

        cursor.execute("INSERT INTO interview_data (answers, analysis) VALUES (?, ?)", (json.dumps(answers), json.dumps(analysis))) # Insert new row
        conn.commit()

    except Exception as e:
        print(f"Error storing answer: {e}")
        conn.rollback()
    finally:
        conn.close()

def get_interview_data():  # No candidate name
    conn = sqlite3.connect('interview_data.db')
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT answers, analysis FROM interview_data ORDER BY id DESC LIMIT 1") # Get the most recent data
        result = cursor.fetchone()

        if result:
            answers_str = result[0]
            analysis_str = result[1]
            try:
                answers = json.loads(answers_str)
                analysis = json.loads(analysis_str)
                return answers, analysis
            except json.JSONDecodeError:
                return None, None
        else:
            return None, None

    except sqlite3.OperationalError as e:
        print(f"Error retrieving data (database might not exist): {e}")
        return None, None
    except Exception as e:
        print(f"Error retrieving data: {e}")
        return None, None
    finally:
        conn.close()