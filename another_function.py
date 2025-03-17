from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

def provide_interview_feedback_mpt(question, answer):
    """
    Provides detailed feedback on an interview answer using MPT, focusing on professional wording.

    Args:
        question (str): The interview question.
        answer (str): The candidate's answer.

    Returns:
        str: Detailed feedback on the answer, focusing on professional wording.
    """

    try:
        model_name = "mosaicml/mpt-7b-instruct"  # or "mosaicml/mpt-7b-chat", "mosaicml/mpt-30b-instruct"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True, torch_dtype=torch.bfloat16)

        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        model = model.to(device)

        prompt = f"Provide feedback on the following interview answer: Question: {question} Answer: {answer}. Focus on identifying filler words, informal language, and unclear phrasing. Suggest professional improvements."

        inputs = tokenizer(prompt, return_tensors="pt").to(device)
        outputs = model.generate(**inputs, max_new_tokens=300)
        output_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

        return f"Feedback: {output_text}"

    except Exception as e:
        return f"An error occurred: {e}"

# Example Usage
question = "Tell me about a time you had to deal with a difficult team member."
answer = "Well, like, this person was just, you know, not really doing their part. And like, they didn't really communicate, basically."

feedback = provide_interview_feedback_mpt(question, answer)
print(feedback)