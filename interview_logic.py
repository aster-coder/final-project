import random
import data_handling
import nlp_processing
import csv

SUBCATEGORY_MAPPING = {
    "general": 1,
    "sales": 2,
    "it": 3,
    "cs": 4,
}

interview_questions = {}

def load_questions(filepath="interview_questions.csv"):
    """Loads questions from a CSV file."""
    questions = {}
    try:
        with open(filepath, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                sub_category = row['sub_category'].lower()  # Normalize to lowercase
                if sub_category in SUBCATEGORY_MAPPING:
                    category_id = SUBCATEGORY_MAPPING[sub_category]
                    question = row['question_text']
                    if category_id not in questions:
                        questions[category_id] = []
                    questions[category_id].append(question)
    except FileNotFoundError:
        print(f"Error: CSV file '{filepath}' not found. Using default questions.")
        questions = {
            1: ["tell me about yourself", "why are you interested in this position?", "what are your strengths?",
                "what are your weaknesses?", "describe a time you faced a challenge and how you overcame it",
                "where do you see yourself in five years?", "do you have any questions for me?"],
            2: ["Describe a successful sales experience.", "How would you handle a difficult customer?"],
            3: ["Explain the concept of cloud computing.", "What is a database index?"],
            4: ["What is object oriented programming?", "Explain a time you used an algorithm to solve a problem."]
        }
    except Exception as e:
        print(f"Error loading questions: {e}")
        questions = {
            1: ["tell me about yourself", "why are you interested in this position?", "what are your strengths?",
                "what are your weaknesses?", "describe a time you faced a challenge and how you overcame it",
                "where do you see yourself in five years?", "do you have any questions for me?"],
            2: ["Describe a successful sales experience.", "How would you handle a difficult customer?"],
            3: ["Explain the concept of cloud computing.", "What is a database index?"],
            4: ["What is object oriented programming?", "Explain a time you used an algorithm to solve a problem."]
        }
    return questions

interview_questions = load_questions()

def get_question(category_id, question_index):
    """Gets a question based on category and index."""
    if category_id in interview_questions:
        if 0 <= question_index < len(interview_questions[category_id]):
            return interview_questions[category_id][question_index]
        else:
            return None  # Index out of range
    else:
        return None  # Category not found

def run_analysis(answers):
    #Your analysis logic
    print("Running analysis")
    print(answers)