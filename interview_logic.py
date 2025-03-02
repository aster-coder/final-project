import random
import data_handling
import nlp_processing
import csv

interview_questions = {}
try:
    with open('interview_questions.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            question_text = row['question_text']
            sub_category = row['sub_category']
            interview_questions[question_text] = [sub_category]
except FileNotFoundError:
    print("Error: interview_questions.csv not found. Using default questions.")
    interview_questions = {
        "tell me about yourself": ["general"],
        "why are you interested in this position?": ["general"],
        "what are your strengths?": ["general"],
        "what are your weaknesses?": ["general"],
        "describe a time you faced a challenge and how you overcame it": ["general"],
        "where do you see yourself in five years?": ["general"],
        "do you have any questions for me?": ["general"],
    }
except Exception as e:
    print(f"An error occurred while reading the CSV file: {e}")
    interview_questions = {
        "tell me about yourself": ["general"],
        "why are you interested in this position?": ["general"],
        "what are your strengths?": ["general"],
        "what are your weaknesses?": ["general"],
        "describe a time you faced a challenge and how you overcame it": ["general"],
        "where do you see yourself in five years?": ["general"],
        "do you have any questions for me?": ["general"],
    }


subcategory_map = {
    1: ["general", "sales", "it", "cs"],
    2: ["sales"],
    3: ["it"],
    4: ["cs"],
}

def run_interview(num_questions, category_id):
    available_questions = []

    if category_id == 1:
        available_questions = list(interview_questions.keys())
    else:
        selected_subcategories = subcategory_map.get(category_id, [])
        for question, subcats in interview_questions.items():
            if any(subcat in subcats for subcat in selected_subcategories):
                available_questions.append(question)

    asked_questions = []

    max_questions_for_category = len(available_questions)
    num_questions = min(num_questions, max_questions_for_category)

    if num_questions not in (5, 10, 15, 20, 25, 30):
        raise ValueError(f"Invalid number of questions. Must be a multiple of 5, up to {max_questions_for_category}")

    print("Bot: Welcome to the AI Job Interview!")

    for i in range(num_questions):
        if not available_questions:
            break

        current_question = random.choice(available_questions)
        print("Bot:", current_question)
        available_questions.remove(current_question)
        asked_questions.append(current_question)

        while True:
            user_input = input("You: ")
            if user_input.lower() in ["quit", "exit"]:
                print("Thank you for your time.")
                return

            if current_question:
                data_handling.store_answer(current_question, user_input)
                current_question = ""
                break

            if "my name is " in user_input.lower():
                candidate_name = user_input.split("is ")[1].strip()
                print(f"Candidate name saved: {candidate_name}")
                break

    print("Bot: Thank you for your responses. The interview is now complete.")