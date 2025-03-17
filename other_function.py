from transformers import T5Tokenizer, T5ForConditionalGeneration

def provide_interview_feedback_t5(question, answer):
    """
    Provides detailed feedback on an interview answer using T5, focusing on professional wording.

    Args:
        question (str): The interview question.
        answer (str): The candidate's answer.

    Returns:
        str: Detailed feedback on the answer, focusing on professional wording.
    """

    try:
        model_name = "t5-base"  # or "t5-small", "t5-large", "t5-3b", "t5-11b", or "google/flan-t5-base"
        tokenizer = T5Tokenizer.from_pretrained(model_name)
        model = T5ForConditionalGeneration.from_pretrained(model_name)

        input_text = f"Give feedback on the following interview answer: Question: {question} Answer: {answer}. Focus on filler words and informal language. Suggest professional improvements."

        input_ids = tokenizer.encode(input_text, return_tensors="pt")

        output_ids = model.generate(input_ids, max_length=300) #adjust max length as needed
        output_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)

        return f"Feedback: {output_text}"

    except Exception as e:
        return f"An error occurred: {e}"

# Example usage:
question = "Tell me about a time you had to deal with a difficult team member."
answer = "Well, like, this person was just, you know, not really doing their part. And like, they didn't really communicate, basically."

feedback = provide_interview_feedback_t5(question, answer)
print(feedback)

#Example with Flan-T5
def provide_interview_feedback_flan_t5_improved(question, answer):
    try:
        model_name = "google/flan-t5-base"  # or large, or xl
        tokenizer = T5Tokenizer.from_pretrained(model_name)
        model = T5ForConditionalGeneration.from_pretrained(model_name)

        input_text = f"""
        Provide feedback on the following interview answers:

        Example 1:
        Question: Tell me about your experience with project management.
        Answer: I, like, did some projects, you know, and, basically, managed them.
        Feedback: The answer contains filler words like 'like', 'you know', and 'basically'. It lacks specific details. Consider using more professional language and providing concrete examples.

        Example 2:
        Question: What are your strengths?
        Answer: I'm a team player and have good communication skills.
        Feedback: This answer is good, but it could be more specific. Provide examples of how you demonstrate teamwork and communication skills.

        Question: {question}
        Answer: {answer}
        Feedback:
        """

        input_ids = tokenizer.encode(input_text, return_tensors="pt")
        output_ids = model.generate(input_ids, max_length=300)
        output_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)

        return f"Feedback: {output_text}"

    except Exception as e:
        return f"An error occurred: {e}"

# Example usage:
question = "Tell me about a time you had to deal with a difficult team member."
answer = "Well, like, this person was just, you know, not really doing their part. And like, they didn't really communicate, basically."

feedback = provide_interview_feedback_flan_t5_improved(question, answer)
print(feedback)

