import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import spacy

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
'''
def generate_feedback(analysis_result):
    """Generates focused feedback using summarization for job interviews."""
    prompt = "Provide a concise summary of the candidate's interview response, focusing on keyword usage, sentiment, and clarity. "

    if analysis_result["grammar_errors"]:
        prompt += "Grammar errors: " + ", ".join(analysis_result["grammar_errors"]) + ". "

    for keyword_type in ["technical_context", "soft_skills_context"]:
        for keyword, context_info in analysis_result["keywords"][keyword_type].items():
            if context_info:
                prompt += f"Regarding '{keyword}': " + " ".join(context_info[0:2]) + ". "

    if analysis_result["filler_words"]:
        prompt += "Filler words found: " + ", ".join(analysis_result["filler_words"]) + ". "

    sentiment = analysis_result["sentiment"]
    if sentiment["compound"] >= 0.2:
        prompt += "Strong positive sentiment detected. "
    elif 0.05 <= sentiment["compound"] < 0.2:
        prompt += "Positive sentiment detected. "
    elif sentiment["compound"] <= -0.2:
        prompt += "Strong negative sentiment detected. "
    elif sentiment["compound"] <= -0.05:
        prompt += "Negative sentiment detected. "
    else:
        prompt += "Neutral sentiment detected. "

    prompt += build_coherence_feedback(analysis_result["coherence"])

    try:
        summary = summarizer(prompt, max_length=180, min_length=50, do_sample=False)[0]['summary_text']
        # Post-processing: remove the prompt using regex
        summary = re.sub(r"^(Provide a concise summary|provide a concise summary|A concise summary|a concise summary) of the candidate's interview response, focusing on keyword usage, sentiment, and clarity\.? ?", "", summary).strip()
        return summary
    except Exception as e:
        print(f"Error during summarization: {e}")
        return "Feedback summarization failed."
'''
def process_answers(answers):
    """Processes answers and generates analysis results."""
    analysis_results = []
    technical_keywords = [
        "python", "javascript", "sql", "database", "api", "cloud", "aws", "azure", "gcp",
        "docker", "kubernetes", "react", "angular", "vue", "node.js", "java", "c++", "c#",
        "git", "version control", "algorithm", "data structure", "testing", "unit test",
        "integration test", "debugging", "performance", "optimization", "security",
        "restful", "graphql", "machine learning", "deep learning", "ai", "artificial intelligence",
        "data science", "big data", "hadoop", "spark", "linux", "windows", "macos",
        "frontend", "backend", "fullstack", "devops", "ci/cd", "agile", "scrum", "microservices",
        "object-oriented", "functional programming", "design patterns", "framework", "library",
        "data modeling", "nosql", "relational database", "etl", "data warehousing", "cybersecurity",
        "networking", "operating systems", "virtualization", "containerization", "mobile development",
        "ios", "android", "embedded systems", "firmware", "iot", "blockchain", "cryptography",
        "code review", "refactoring", "software architecture", "system design", "ui/ux",
        "web development", "mobile app", "software development", "programming", "coding", "scripting",
        "data analysis", "data visualization", "cloud computing", "serverless", "automation"
    ]
    soft_skills_keywords = [
        "communication", "teamwork", "leadership", "problem-solving", "critical thinking",
        "adaptability", "collaboration", "time management", "organization", "initiative",
        "creativity", "innovation", "decision-making", "conflict resolution", "negotiation",
        "presentation", "public speaking", "interpersonal skills", "emotional intelligence",
        "active listening", "empathy", "flexibility", "resilience", "accountability",
        "proactive", "self-motivation", "customer service", "client relations", "mentoring",
        "coaching", "strategic thinking", "project management", "risk management", "change management",
        "persuasion", "influence", "delegation", "prioritization", "planning", "execution",
        "learning agility", "growth mindset", "professionalism", "ethical", "integrity",
        "dependability", "reliability", "resourcefulness", "self-awareness", "stress management",
        "team building", "knowledge sharing", "feedback", "constructive criticism", "openness",
        "curiosity", "detail-oriented", "results-oriented", "process improvement", "efficiency",
        "customer focus", "stakeholder management", "relationship building", "networking",
        "cross-functional", "interdisciplinary", "self-improvement", "continuous learning",
        "goal-oriented", "deadline-driven", "performance-driven", "solution-oriented", "positive attitude",
        "work ethic", "commitment", "dedication", "passion", "drive", "enthusiasm"
    ]
    filler_words = ["like", "basically", "actually", "just", "you know", "kind of", "sort of"]

    for answer in answers:
        doc = nlp(answer)
        sentiment = sia.polarity_scores(answer)
        grammar_errors = analyze_grammar(doc)
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

    return analysis_results  # Returns a list of dictionaries