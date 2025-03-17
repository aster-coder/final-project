import nltk
from transformers import pipeline
import spacy

# Download NLTK data (if needed)
try:
    nltk.data.find('punkt')
except LookupError:
    nltk.download('punkt')

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_trf")
except OSError:
    print("Downloading spaCy model...")
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# Initialize text generation model
generator = pipeline("text-generation", model="gpt2-large")

def provide_interview_feedback(question, answer):
    """
    Provides detailed feedback on an interview answer, focusing on professional wording.

    Args:
        question (str): The interview question.
        answer (str): The candidate's answer.

    Returns:
        str: Detailed feedback on the answer, focusing on professional wording.
    """

    try:
        # Extremely simplified feedback prompt
        feedback_prompt = f"Give feedback on the following answer: '{answer}'. Focus on filler words and informal language. Suggest professional improvements."
        feedback_answers = generator(feedback_prompt, max_length=200, num_return_sequences=2)
        feedback = feedback_answers[0]['generated_text'].strip()

        return f"Feedback: {feedback}"

    except Exception as e:
        return f"An error occurred: {e}"

# Example usage:
question = "Tell me about a time you had to deal with a difficult team member."
answer = "Well, like, this person was just, you know, not really doing their part. And like, they didn't really communicate, basically."

feedback = provide_interview_feedback(question, answer)
print(feedback)