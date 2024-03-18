from flask import Flask, request, jsonify, render_template
from PyPDF2 import PdfReader
import google.generativeai as genai

app = Flask(__name__, static_folder='static')

# Replace 'YOUR_API_KEY' with your actual API key
API_KEY = 'AIzaSyB8Td8xynfJ7QzKly1xpdg6Y_4chnBkymU'  # Replace 'YOUR_API_KEY' with your actual API key
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro')

interview_started = False  # Flag to indicate if the interview has started
questions = []  # List to store questions

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

@app.route('/start_interview', methods=['POST'])
def start_interview():
    global interview_started, questions
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

if __name__ == '__main__':
    app.run(debug=True)