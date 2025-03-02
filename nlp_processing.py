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
analyzer = SentimentIntensityAnalyzer()

def analyze_answer(answer, keywords):
    analysis = {}
    matched_keywords = [keyword for keyword in keywords if keyword.lower() in answer.lower()]
    analysis['matched_keywords'] = matched_keywords
    analysis['keyword_match_score'] = len(matched_keywords)
    sentiment = analyzer.polarity_scores(answer)
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