#imports
import random
import csv
#all categories used in the project, can be expanded here
SUBCATEGORY_MAPPING = {
    "general": 1,
    "sales": 2,
    "it": 3,
    "cs": 4,
}
#The interview questions are taken from a CSV file, and in case the file is not found there are generic questions listed
#The questions are taken randomly from the list rather than in order to give a unique interview experience
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

def get_question(category_id, asked_questions=None):
    """Gets a random question based on category."""
    if asked_questions is None:
        asked_questions = []

    if category_id in interview_questions:
        available_questions = [
            q for q in interview_questions[category_id] if q not in asked_questions
        ]
        if available_questions:
            return random.choice(available_questions)
        else:
            return None  # No more questions available in this category
    else:
        return None  # Category not found

