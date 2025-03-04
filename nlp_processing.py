import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from transformers import pipeline

# Download NLTK data (if needed)
try:
    nltk.data.find('punkt')
    nltk.data.find('averaged_perceptron_tagger')
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('vader_lexicon')

# Initialize zero-shot classification pipeline
classifier = pipeline("zero-shot-classification")

# Sentiment analyzer
sia = SentimentIntensityAnalyzer()
"""
def analyze_answer(answer, keywords):
    analysis = {}
    matched_keywords = [keyword for keyword in keywords if keyword.lower() in answer.lower()]
    analysis['matched_keywords'] = matched_keywords
    analysis['keyword_match_score'] = len(matched_keywords)
    sentiment = sia.polarity_scores(answer)
    analysis['sentiment'] = sentiment
    analysis['sentiment_score'] = sentiment['compound']
    analysis['answer_length'] = len(answer.split())
    return analysis

def get_intent(user_input, candidate_labels):  # Pass candidate labels as argument
    try:
        classified = classifier(user_input, candidate_labels)
        return classified["labels"][0]
    except Exception as e:
        print(f"Error in intent recognition: {e}")
        return None  # Or handle the error as appropriate
"""
def process_answers(answers):
    print("process_answers called with answers:", answers)
    try:
        analysis_results = []

        technical_keywords = ["python", "javascript", "sql", "database", "api", "cloud"]
        soft_skills_keywords = ["communication", "teamwork", "leadership", "problem-solving", "critical thinking"]

        for answer in answers:
            sentiment = sia.polarity_scores(answer)
            found_technical = [keyword for keyword in technical_keywords if keyword.lower() in answer.lower()]
            found_soft_skills = [keyword for keyword in soft_skills_keywords if keyword.lower() in answer.lower()]

            analysis_results.append({
                "answer": answer,
                "sentiment": sentiment,
                "keywords": {
                    "technical": found_technical,
                    "soft_skills": found_soft_skills
                }
            })
        print("analysis_results:", analysis_results)
        return analysis_results

    except Exception as e:
        print(f"Error in process_answers: {e}")
        return []