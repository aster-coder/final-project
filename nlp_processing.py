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

# Initialize text summarization model
summarizer = pipeline("summarization", model="t5-large")
# Sentiment analyzer
sia = SentimentIntensityAnalyzer()


def analyze_grammar(answer):
    """Analyzes grammar and returns a list of errors."""
    doc = nlp(answer)
    errors = []

    # 1. Possessive Pronoun Errors (Already Implemented)
    for token in doc:
        if token.pos_ == "PRP$" and token.dep_ == "poss":
            if token.head.pos_ != "NOUN":
                errors.append(f"Potential possessive error with '{token.text}'.")

    # 2. Subject-Verb Agreement
    for sent in doc.sents:
        for token in sent:
            if token.dep_ == "nsubj" and token.head.pos_ == "VERB":
                if token.tag_ in ["NNS", "NNPS"] and token.head.tag_ in ["VBZ"]:
                    errors.append(f"Subject-verb agreement error: '{token.text}' (plural) with '{token.head.text}' (singular).")
                elif token.tag_ in ["NN", "NNP"] and token.head.tag_ in ["VBP"]:
                    errors.append(f"Subject-verb agreement error: '{token.text}' (singular) with '{token.head.text}' (plural).")

    # 3. Incorrect Article Usage (a/an/the)
    for token in doc:
        if token.pos_ == "DET":
            if token.text.lower() == "a" and token.head.text[0].lower() in "aeiou":
                errors.append(f"Incorrect article usage: 'a' before a vowel sound in '{token.head.text}'. Use 'an'.")
            elif token.text.lower() == "an" and token.head.text[0].lower() not in "aeiou":
                errors.append(f"Incorrect article usage: 'an' before a consonant sound in '{token.head.text}'. Use 'a'.")

    # 4. Run-on Sentences and Sentence Fragments (Basic Check)
    if len(list(doc.sents)) > 1:
        for sent in doc.sents:
            if len(sent) < 3: #very basic check.
                errors.append(f"Potential sentence fragment: '{sent.text}'.")

    # 5. Misused Homophones (Example: their/there/they're)
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

    # 6. Punctuation Errors (Basic Check)
    if answer.endswith(".") or answer.endswith("!") or answer.endswith("?"):
        pass
    else:
        errors.append("Potential missing punctuation at the end of the sentence.")

    # 7. Comma Splices (Basic check)
    for sent in doc.sents:
        if "," in sent.text and len(list(sent)) > 6:
            commas = [token for token in sent if token.text == ","]
            if len(commas) > 1:
                errors.append(f"Potential comma splice in sentence: '{sent.text}'")

    return errors

def analyze_sentence_structure(answer):
    """Analyzes sentence structure and returns detailed feedback."""
    doc = nlp(answer)
    sentences = list(doc.sents)
    feedback = []

    if not sentences:
        feedback.append("The answer seems to be empty or lacks complete sentences.")
        return feedback

    avg_len = sum(len(sent) for sent in sentences) / len(sentences)

    # 1. Sentence Length Analysis (Improved)
    if avg_len > 30:
        feedback.append("Consider breaking down long sentences for better readability. Complex sentences are good, but very long ones can be hard to follow.")
    elif avg_len < 8: #increased from 5 to 8. short sentences are not always bad.
        feedback.append("Consider combining short sentences to create more complex and detailed responses. Varying sentence length can make your writing more engaging.")

    # 2. Passive Voice Detection
    passive_sentences = [sent for sent in sentences if any(token.dep_ == "auxpass" for token in sent)]
    if passive_sentences:
        feedback.append(f"Potential passive voice detected in: {[sent.text for sent in passive_sentences]}. Consider using active voice for a more direct and engaging tone.")

    # 3. Sentence Variety Analysis
    sentence_starts = [sent[0].pos_ for sent in sentences]
    if len(set(sentence_starts)) < 2 and len(sentences) > 2: #If there are more than 2 sentences, but only one type of start.
        feedback.append("Try to vary the beginnings of your sentences. Starting multiple sentences with the same type of word can make your writing sound repetitive.")

    # 4. Complexity Analysis (Basic)
    complex_sentences = [sent for sent in sentences if any(token.dep_ in ["advcl", "csubj", "ccomp", "xcomp"] for token in sent)]
    if len(complex_sentences) < len(sentences) / 2 and len(sentences) > 2:
        feedback.append("Consider incorporating more complex sentence structures (e.g., using subordinate clauses) to demonstrate depth and sophistication in your responses.")

    # 5. Word Order and Clarity
    for sent in sentences:
        if sent[0].pos_ == "ADV" and len(sent) > 5:
            feedback.append(f"Consider revising the sentence: '{sent.text}'. Starting sentences with adverbs can sometimes lead to awkward phrasing. Try rearranging the words for clarity.")

    # 6. Repetitive Sentence Structures
    sentence_structures = [" ".join([token.dep_ for token in sent]) for sent in sentences]
    if len(set(sentence_structures)) < len(sentences) / 2 and len(sentences) > 3:
        feedback.append("Try to vary your sentence structure. Using similar sentence patterns repeatedly can make your writing sound monotonous.")

    #7. Check for excessive use of filler words.
    filler_words = ["like", "basically", "actually", "just", "you know", "kind of", "sort of"]
    for sent in sentences:
        for token in sent:
            if token.text.lower() in filler_words:
                feedback.append(f"Consider reducing filler words such as '{token.text}' in your sentences for more concise and professional language.")

    #8. Check for overuse of conjunctions at the start of sentences.
    conjunctions = ["and", "but", "or", "so", "because"]
    if sentences:
      if sentences[0][0].text.lower() in conjunctions:
        feedback.append(f"Starting sentences with conjunctions such as '{sentences[0][0].text.lower()}' can sometimes make your writing sound informal. Try varying your sentence starters.")

    return feedback

def analyze_keyword_context(answer, keywords):
    """Analyzes keyword usage in context and returns detailed feedback."""
    doc = nlp(answer.lower())
    found_keywords = []
    contextual_feedback = {}  # Use a dictionary to store feedback per keyword

    for keyword in keywords:
        if keyword.lower() in answer.lower():
            found_keywords.append(keyword)
            contextual_feedback[keyword] = []  # Initialize feedback list for this keyword

    for keyword in found_keywords:
        keyword_tokens = [token for token in doc if token.text == keyword.lower()]

        if keyword_tokens:
            for keyword_token in keyword_tokens:
                # 1. Neighboring Words and Phrases
                neighbors = [t.text for t in doc[max(0, keyword_token.i - 3):min(len(doc), keyword_token.i + 4)]]
                contextual_feedback[keyword].append(f"Context: {' '.join(neighbors)}.")

                # 2. Dependency Analysis
                dependencies = [
                    (token.text, token.dep_, token.head.text)
                    for token in doc
                    if token.head == keyword_token or keyword_token.head == token
                ]
                if dependencies:
                    contextual_feedback[keyword].append(f"Dependencies: {dependencies}.")
                else:
                    contextual_feedback[keyword].append("No direct dependencies found.")

                # 3. Part-of-Speech Analysis
                pos_info = f"Part of speech: {keyword_token.pos_}."
                contextual_feedback[keyword].append(pos_info)

                # 4. Sentence Level Context
                sentence = list(keyword_token.sent)
                contextual_feedback[keyword].append(f"Sentence context: {' '.join([token.text for token in sentence])}.")

                # 5. Entity Recognition (If Applicable)
                if keyword_token.ent_type_:
                  contextual_feedback[keyword].append(f"Entity type: {keyword_token.ent_type_}.")

                # 6. Check for Negative Context
                negative_words = ["not", "no", "never", "without", "hardly"]
                for neg_word in negative_words:
                    if neg_word in [t.text for t in doc[max(0, keyword_token.i - 5):min(len(doc), keyword_token.i + 5)]]:
                        contextual_feedback[keyword].append(f"Potential negative context detected near '{keyword}'.")

                #7. Check for usage with action verbs.
                action_verbs = ["implement", "develop", "build", "design", "create", "manage", "optimize", "analyze", "test", "debug", "solve"]
                for verb in action_verbs:
                    if verb in [t.text for t in doc[max(0, keyword_token.i - 5):min(len(doc), keyword_token.i + 5)]]:
                        contextual_feedback[keyword].append(f"Used with action verb: '{verb}'.")

                #8. Check for usage with soft skill related verbs.
                soft_skill_verbs = ["communicate", "collaborate", "lead", "solve", "think", "adapt", "organize", "plan", "execute", "mentor"]
                for soft_verb in soft_skill_verbs:
                    if soft_verb in [t.text for t in doc[max(0, keyword_token.i - 5):min(len(doc), keyword_token.i + 5)]]:
                        contextual_feedback[keyword].append(f"Used with soft skill verb: '{soft_verb}'.")

        else:
            contextual_feedback[keyword].append("Context could not be determined.")

    return contextual_feedback

def generate_feedback(analysis_result):
    """Generates feedback using BART summarization."""
    feedback_text = ""

    # Build the feedback text from analysis results (similar to your previous code)
    if analysis_result["grammar_errors"]:
        feedback_text += "Grammar errors: " + ", ".join(analysis_result["grammar_errors"]) + ". "
    if analysis_result["sentence_structure_feedback"]:
        feedback_text += "Sentence structure feedback: " + ", ".join(analysis_result["sentence_structure_feedback"]) + ". "
    for keyword_type in ["technical_context", "soft_skills_context"]:
        for keyword, context_info in analysis_result["keywords"][keyword_type].items():
            if context_info:
                feedback_text += f"Regarding '{keyword}': " + " ".join(context_info[0:2]) + ". "
    sentiment = analysis_result["sentiment"]
    if sentiment["compound"] >= 0.05:
        feedback_text += "Your answer conveys a positive sentiment."
    elif sentiment["compound"] <= -0.05:
        feedback_text += "Your answer conveys a negative sentiment."
    else:
        feedback_text += "Your answer conveys a neutral sentiment."

    try:
        summary = summarizer(feedback_text, max_length=200, min_length=30, do_sample=False)[0]['summary_text']
        return summary
    except Exception as e:
        print(f"Error during summarization: {e}")
        return "Feedback summarization failed."

def process_answers(answers):
    print("process_answers called with answers:", answers)
    try:
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

        for answer in answers:
            sentiment = sia.polarity_scores(answer)
            found_technical = [keyword for keyword in technical_keywords if keyword.lower() in answer.lower()]
            found_soft_skills = [keyword for keyword in soft_skills_keywords if keyword.lower() in answer.lower()]

            grammar_errors = analyze_grammar(answer)
            sentence_structure_feedback = analyze_sentence_structure(answer)
            technical_context = analyze_keyword_context(answer, technical_keywords)
            soft_skills_context = analyze_keyword_context(answer, soft_skills_keywords)

            analysis_result = {
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
            }

            # Generate and add feedback to the result
            analysis_result["generated_feedback"] = generate_feedback(analysis_result)

            analysis_results.append(analysis_result)

        print("analysis_results:", analysis_results)
        return analysis_results
    except Exception as e:
        print(f"An error occurred: {e}")
        return []