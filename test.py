import requests

response = requests.post(
    "http://localhost:5000/predict",
    json={
        "resume_text": "Python developer with django flask experience and machine learning data science",
        "top_k": 3
    }
)

print(response.json())