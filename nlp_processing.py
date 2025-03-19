import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import spacy
import csv

# Download NLTK data (only once)
try:
    nltk.data.find('punkt')
    nltk.data.find('averaged_perceptron_tagger')
    nltk.data.find('vader_lexicon')
except LookupError:
    print("Downloading NLTK data...")
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

# Initialize text summarization model
#summarizer = pipeline("summarization", model="t5-large")
# Sentiment analyzer
sia = SentimentIntensityAnalyzer()

#changed to highlight common errors found in spoken speech over written text
def analyze_grammar(doc):
    """Analyzes grammar for job interview context (spoken language)."""
    errors = []

    # 1. Subject-Verb Agreement (Most noticeable in speech)
    for sent in doc.sents:
        for token in sent:
            if token.dep_ == "nsubj" and token.head.pos_ == "VERB":
                if token.tag_ in ["NNS", "NNPS"] and token.head.tag_ in ["VBZ"]:
                    errors.append(f"Subject-verb agreement error: '{token.text}' (plural) with '{token.head.text}' (singular).")
                elif token.tag_ in ["NN", "NNP"] and token.head.tag_ in ["VBP"]:
                    errors.append(f"Subject-verb agreement error: '{token.text}' (singular) with '{token.head.text}' (plural).")

    # 2. Misused Homophones (Common in speech)
    for token in doc:
        if token.text.lower() == "their" and ("there" in [t.text.lower() for t in doc] or "they're" in [t.text.lower() for t in doc]):
            if token.dep_ != "poss":
                errors.append(f"Potential homophone error: '{token.text}'. Consider 'there' or 'they're'.")

        if token.text.lower() == "there" and ("their" in [t.text.lower() for t in doc] or "they're" in [t.text.lower() for t in doc]):
            if token.dep_ == "poss":
                errors.append(f"Potential homophone error: '{token.text}'. Consider 'their'.")

        if token.text.lower() == "they're" and ("their" in [t.text.lower() for t in doc] or "there" in [t.text.lower() for t in doc]):
            if token.dep_ == "poss":
                errors.append(f"Potential homophone error: '{token.text}'. Consider 'their' or 'there'.")

    return errors
#altered again to focus more on spoken mistakes with sentence structure
def analyze_sentence_structure(doc):
    """Analyzes sentence structure for spoken job interview context."""
    sentences = list(doc.sents)
    feedback = []

    if not sentences:
        feedback.append("The answer seems to be empty or lacks complete sentences.")
        return feedback

    avg_len = sum(len(sent) for sent in sentences) / len(sentences)

    # 1. Sentence Length Analysis (Adjusted)
    if avg_len > 25:  # Adjusted threshold for spoken language
        feedback.append("Consider breaking down long sentences for better clarity. Very long sentences can be difficult to follow in spoken conversation.")

    # 2. Filler Word Analysis
    filler_words = ["like", "basically", "actually", "just", "you know", "kind of", "sort of"]
    for sent in sentences:
        for token in sent:
            if token.text.lower() in filler_words:
                feedback.append(f"Consider reducing filler words such as '{token.text}' for more concise and professional language.")

    return feedback


def analyze_keyword_context(doc, keywords):
    """Analyzes keyword usage in context for job interviews."""
    contextual_feedback = {}
    found_keywords = []

    for keyword in keywords:
        if keyword.lower() in doc.text.lower():
            found_keywords.append(keyword)
            contextual_feedback[keyword] = []

    for keyword in found_keywords:
        keyword_tokens = [token for token in doc if token.text.lower() == keyword.lower()]
        for keyword_token in keyword_tokens:
            # 1. Neighboring Words (Context)
            neighbors = [t.text for t in doc[max(0, keyword_token.i - 3):min(len(doc), keyword_token.i + 4)]]
            contextual_feedback[keyword].append(f"Context: {' '.join(neighbors)}.")

            # 2. Action Verbs
            action_verbs = ["implement", "develop", "build", "design", "create", "manage", "optimize", "analyze", "test", "debug", "solve"]
            for verb in action_verbs:
                if verb in [t.text for t in doc[max(0, keyword_token.i - 5):min(len(doc), keyword_token.i + 5)]]:
                    contextual_feedback[keyword].append(f"Used with action verb: '{verb}'.")

            # 3. Soft Skill Verbs
            soft_skill_verbs = ["communicate", "collaborate", "lead", "solve", "think", "adapt", "organize", "plan", "execute", "mentor"]
            for soft_verb in soft_skill_verbs:
                if soft_verb in [t.text for t in doc[max(0, keyword_token.i - 5):min(len(doc), keyword_token.i + 5)]]:
                    contextual_feedback[keyword].append(f"Used with soft skill verb: '{soft_verb}'.")

            # 4. Negative Context
            negative_words = ["not", "no", "never", "without", "hardly"]
            for neg_word in negative_words:
                if neg_word in [t.text for t in doc[max(0, keyword_token.i - 5):min(len(doc), keyword_token.i + 5)]]:
                    contextual_feedback[keyword].append(f"Potential negative context near '{keyword}'.")

    return contextual_feedback
def find_filler_words(doc, filler_words):
    """Finds and returns filler words from the document."""
    found_filler_words = []
    for token in doc:
        if token.text.lower() in filler_words:
            found_filler_words.append(token.text.lower())
    return found_filler_words

def analyze_coherence(doc):
    """Analyzes coherence based on transition words and logical flow."""
    transition_words = ["however", "therefore", "furthermore", "moreover", "in addition", "consequently", "as a result", "thus", "on the other hand", "for example"]
    transition_count = 0
    for token in doc:
        if token.text.lower() in transition_words:
            transition_count += 1

    sentences = list(doc.sents)
    if len(sentences) > 1:
        avg_sentence_length = sum(len(sent) for sent in sentences) / len(sentences)
    else:
        avg_sentence_length = 0

    coherence_feedback = {
        "transition_count": transition_count,
        "avg_sentence_length": avg_sentence_length,
        "feedback": []
    }

    if transition_count < len(sentences) / 3:
        coherence_feedback["feedback"].append("Consider using more transition words to improve the flow of your answer.")
    if avg_sentence_length > 30:
        coherence_feedback["feedback"].append("Try to vary sentence length to improve readability and coherence.")

    return coherence_feedback

def build_coherence_feedback(coherence_analysis):
    """Builds coherence feedback string from analysis."""
    feedback_text = ""
    if coherence_analysis and coherence_analysis["feedback"]:
        feedback_text += "Coherence feedback: " + ", ".join(coherence_analysis["feedback"]) + ". "
    return feedback_text

def load_keywords(filepath="keywords.csv"):
    """Loads keywords from a CSV file."""
    technical_keywords = []
    soft_skills_keywords = []
    try:
        with open(filepath, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                keyword = row['keyword'].strip().lower() #make lowercase for consistency
                keyword_type = row['type'].strip().lower() #make lowercase for consistency
                if keyword_type == 'technical':
                    technical_keywords.append(keyword)
                elif keyword_type == 'soft':
                    soft_skills_keywords.append(keyword)
    except FileNotFoundError:
        print(f"Error: Keyword file '{filepath}' not found.")
        return [], []
    except KeyError:
        print("Error: CSV file must have 'keyword' and 'type' columns.")
        return [], []
    return technical_keywords, soft_skills_keywords

def process_answers(answers):
    """Processes answers and generates analysis results."""
    analysis_results = []
    technical_keywords, soft_skills_keywords = load_keywords()

    if not technical_keywords and not soft_skills_keywords:
        return []  # Return empty if no keywords loaded

    filler_words = ["like", "basically", "actually", "just", "you know", "kind of", "sort of"]

    for answer in answers:
        doc = nlp(answer)
        sentiment = sia.polarity_scores(answer)
        grammar_errors = analyze_grammar(doc)
        sentence_structure_feedback = analyze_sentence_structure(doc) # added sentence structure analysis
        technical_context = analyze_keyword_context(doc, technical_keywords)
        soft_skills_context = analyze_keyword_context(doc, soft_skills_keywords)
        found_filler_words = find_filler_words(doc, filler_words)
        coherence = analyze_coherence(doc)

        combined_feedback = ""

        combined_feedback += f"Sentiment: {sentiment['compound']:.2f}. "

        if grammar_errors:
            combined_feedback += f"Grammar errors: {', '.join(grammar_errors)}. "

        if found_filler_words:
            combined_feedback += f"Filler words: {', '.join(found_filler_words)}. "

        if sentence_structure_feedback: # added sentence structure feedback
            combined_feedback += f"Sentence Structure feedback: {', '.join(sentence_structure_feedback)}. "

        if coherence["feedback"]:
            combined_feedback += f"Coherence feedback: {', '.join(coherence['feedback'])}. "

        for keyword_type, context_data in [("technical_context", technical_context), ("soft_skills_context", soft_skills_context)]:
            for keyword, context_info in context_data.items():
                if context_info:
                    combined_feedback += f"Keyword '{keyword}' context: {', '.join(context_info)}. "

        analysis_result = {
            "answer": answer,
            "sentiment": sentiment,
            "keywords": {
                "technical_context": technical_context,
                "soft_skills_context": soft_skills_context,
            },
            "grammar_errors": grammar_errors,
            "filler_words": found_filler_words,
            "coherence": coherence,
            "combined_feedback": combined_feedback.strip()  # Added combined feedback
        }

        analysis_results.append(analysis_result)

    return analysis_results  