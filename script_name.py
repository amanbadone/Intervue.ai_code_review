import requests

url = 'http://127.0.0.1:5000/generated_questions'
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    print('Generated Questions:')
    print(data.get('generated_questions'))
else:
    print('Error:', response.text)
