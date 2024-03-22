from flask import Flask, request, jsonify, render_template
from PyPDF2 import PdfReader
import google.generativeai as genai


app = Flask(__name__, static_folder='static')

# Replace 'YOUR_API_KEY' with your actual API key
API_KEY = 'YOUR_API_KEY'
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro')

interview_started = False  # Flag to indicate if the interview has started
questions = []  # List to store questions
current_question = None  # Variable to track the current question

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/parse_resume', methods=['POST'])
def parse_resume():
    global interview_started, questions
    if 'resume' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    resume_file = request.files['resume']
    if resume_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        # Extract text from the resume PDF file
        pdf_reader = PdfReader(resume_file)
        resume_text = ""
        for page in pdf_reader.pages:
            resume_text += page.extract_text()

        # Generate questions based on resume text
        prompt = "Generate interview questions based on the following resume text:\n\n" + resume_text + "\n\nAsk each question at a time. If the user responds, ask follow-up questions or move on to the next question by analyzing the resume."
        response = model.generate_content(prompt)
        generated_questions = response.text.split("\n")  # Assuming questions are separated by newlines
        # Remove any empty questions or those starting with '*'
        questions = [question.strip() for question in generated_questions if question.strip() and not question.strip().startswith('*')]

        # Handle empty question list (if necessary)
        if not questions:
            questions = ["Tell me about yourself.", "What are your strengths and weaknesses?"]  # Default questions

        interview_started = True  # Set the flag to indicate that the interview has started
        return jsonify({'status': 'success', 'questions': questions})  # Corrected key name
    except Exception as e:
        # Handle errors during resume parsing or question generation
        return jsonify({'error': str(e)}), 500

# Undefined Variable current_question: Ensure that current_question is defined globally or passed as an argument to the process_response function.

@app.route('/start_interview', methods=['POST'])
def start_interview():
    global interview_started, questions, current_question
    if not interview_started:
        return jsonify({'error': 'Interview not started yet'}), 400

    try:
        current_question = questions.pop(0) if questions else None  # Get the next question
        return jsonify({'question': current_question})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/end_interview', methods=['POST'])
def end_interview():
    global interview_started
    interview_started = False
    return jsonify({'status': 'completed'})

@app.route('/test_question_generation', methods=['GET'])
def test_question_generation():
    global questions
    # Test the generate_questions_from_resume function
    resume_text = "Sample resume text..."
    prompt = "Generate interview questions based on the following resume text:\n\n" + resume_text + "\n\nAsk each question at a time. If the user responds, ask follow-up questions or move on to the next question by analyzing the resume."
    response = model.generate_content(prompt)
    generated_questions = response.text.split("\n")  # Assuming questions are separated by newlines
    # Remove any empty questions or those starting with '*'
    questions = [question.strip() for question in generated_questions if question.strip() and not question.strip().startswith('*')]
    # Handle empty question list (if necessary)
    if not questions:
        questions = ["Tell me about yourself.", "What are your strengths and weaknesses?"]  # Default questions
    return jsonify({'generated_questions': questions})

@app.route('/generated_questions', methods=['GET'])
def get_generated_questions():
    global questions
    return jsonify({'generated_questions': questions})

# New route to print resume data in the terminal
@app.route('/resume_info', methods=['GET'])
def resume_info():
    resume_text = request.args.get('resume_text')
    print("Resume Information:")
    print(resume_text)
    return jsonify({'status': 'success'})

@app.route('/process_response', methods=['POST'])
def process_response():
    global current_question, questions

    # Get the user's response from the request data
    response_data = request.json
    user_response = response_data.get('response', '')

    # Logic to determine the next question dynamically based on the user's response and interview context
    if current_question:
        # Handle follow-up questions based on the user's response to the current question
        next_question = get_next_question_based_on_response(current_question, user_response)
    else:
        # If there's no current question (e.g., at the beginning of the interview), get the next question from the resume
        next_question = get_next_resume_question()

    # Update the current question for the next iteration
    current_question = next_question

    # Return the next question or None if the interview is completed
    return jsonify({'question': current_question})

def get_next_question_based_on_response(current_question, user_response):
    """
    Determine the next question based on the user's response to the current question.

    Args:
    - current_question: The current question asked in the interview.
    - user_response: The user's response to the current question.

    Returns:
    - The next question to ask in the interview based on the user's response.
    """
    # Implement your logic here
    # Example logic:
    if "experience as an Android Developer Intern" in current_question:
        return "Describe your role as Club Head of the MLSA Club."
    else:
        return None

def get_next_resume_question():
    """
    Get the next question from the resume.

    Returns:
    - The next question to ask in the interview based on the resume.
    """
    # Implement your logic here
    # Example logic:
    if questions:
        return questions.pop(0)
    else:
        return None
if __name__ == '__main__':
    app.run(debug=True)
