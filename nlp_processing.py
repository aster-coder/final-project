import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from transformers import pipeline
import spacy

# Download NLTK data (if needed)
try:
    nltk.data.find('punkt')
    nltk.data.find('averaged_perceptron_tagger')
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('vader_lexicon')

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading spaCy model...")
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# Initialize zero-shot classification pipeline
classifier = pipeline("zero-shot-classification")

# Sentiment analyzer
sia = SentimentIntensityAnalyzer()

def analyze_grammar(answer):
    """Analyzes grammar and returns feedback."""
    doc = nlp(answer)
    errors = []
    for token in doc:
        if token.pos_ == "PRP$" and token.dep_ == "poss":
            if token.head.pos_ != "NOUN":
                errors.append(f"Potential possessive error with '{token.text}'.")
        # Add more grammar checks based on your needs
    return errors

def analyze_sentence_structure(answer):
    """Analyzes sentence structure and returns feedback."""
    doc = nlp(answer)
    sentences = list(doc.sents)
    feedback = []
    if len(sentences) > 0:
        avg_len = sum(len(sent) for sent in sentences) / len(sentences)
        if avg_len > 30:
            feedback.append("Consider breaking down long sentences for better readability.")
        if avg_len < 5:
            feedback.append("Consider combining short sentences to create more complex and detailed responses.")

    return feedback

def analyze_keyword_context(answer, keywords):
    """Analyzes keyword usage in context and returns feedback."""
    doc = nlp(answer.lower())
    found_keywords = []
    for keyword in keywords:
        if keyword.lower() in answer.lower():
            found_keywords.append(keyword)

    contextual_feedback = []
    for keyword in found_keywords:
        keyword_token = None
        for token in doc:
            if token.text == keyword.lower():
                keyword_token = token
                break

        if keyword_token:
            # Simple context check: check neighboring words
            neighbors = [t.text for t in doc[max(0, keyword_token.i - 2):min(len(doc), keyword_token.i + 3)]]
            contextual_feedback.append(f"Keyword '{keyword}' found in context: {' '.join(neighbors)}.")
        else:
            contextual_feedback.append(f"Keyword '{keyword}' found, but context could not be determined.")
    return contextual_feedback

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

            grammar_errors = analyze_grammar(answer)
            sentence_structure_feedback = analyze_sentence_structure(answer)
            technical_context = analyze_keyword_context(answer, technical_keywords)
            soft_skills_context = analyze_keyword_context(answer, soft_skills_keywords)

            analysis_results.append({
                "answer": answer,
                "sentiment": sentiment,
                "keywords": {
                    "technical": found_technical,
                    "soft_skills": found_soft_skills,
                    "technical_context": technical_context,
                    "soft_skills_context": soft_skills_context,

                },
                "grammar_errors": grammar_errors,
                "sentence_structure_feedback": sentence_structure_feedback,
            })
        print("analysis_results:", analysis_results)
        return analysis_results

    except Exception as e:
        print(f"Error in process_answers: {e}")
        return []