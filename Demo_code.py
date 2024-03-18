from flask import Flask, request, jsonify, render_template
import google.generativeai as genai

app = Flask(__name__, static_folder='static')

genai.configure(api_key='AIzaSyB8Td8xynfJ7QzKly1xpdg6Y_4chnBkymU')  # Replace 'YOUR_API_KEY' with your actual API key
model = genai.GenerativeModel('gemini-pro')

interview_started = False  # Flag to indicate if the interview has started

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/parse_resume', methods=['POST'])
def parse_resume():
    global interview_started
    if 'resume' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    resume_file = request.files['resume']
    if resume_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    resume_data = parse_resume(resume_file)
    questions = generate_questions_from_resume(resume_data)
    interview_started = True  # Set the flag to indicate that the interview has started
    return jsonify({'questions': questions})

def parse_resume(resume_file):
    # Implement resume parsing logic here
    # Example: Extract relevant information from the resume
    # Return the parsed resume data
    return {}

def generate_questions_from_resume(resume_data):
    # Implement logic to generate questions based on resume data
    # Example: Generate questions based on parsed resume data
    # Return the list of generated questions
    return []

@app.route('/process_response', methods=['POST'])
def process_response():
    data = request.json
    if 'response' not in data:
        return jsonify({'error': 'No response provided'}), 400
    user_response = data['response']
    # Only ask questions if the interview has started
    if interview_started:
        next_question = generate_next_question(user_response)
    else:
        next_question = "Let's start the interview first."
    return jsonify({'question': next_question})

def generate_next_question(user_response):
    # Implement logic to generate the next question based on user response
    # Example: Use Gemini Pro model to generate next question
    response = model.generate_content("Generate next question based on user response")
    next_question = response.text.replace('*', '')  # Remove * from the question
    return next_question

if __name__ == '__main__':
    app.run(debug=True)