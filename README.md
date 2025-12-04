Smart Hire – Automated Resume Screening and Job Role Recommendation

Smart Hire is an AI-powered resume analysis system that automatically screens candidate resumes, extracts key information, and predicts the top three most suitable job roles.
It reduces manual HR workload and speeds up the hiring decision process.

Overview

Smart Hire performs automated candidate evaluation through these core steps:

Resume parsing and data extraction

Skill and experience analysis

Model-based prediction of the top three job roles

API-driven backend connected to a user-friendly frontend

End-to-end automation of tasks typically handled manually by HR

Features

Automated resume screening

Top 3 job-role prediction using machine learning

Flask-powered backend for predictions

Clean and simple frontend interface

Pre-trained or dynamically trained ML model

Ready for deployment on platforms like Render, Railway, or Vercel

Project Structure
SmartHire/
│
├── backend/
│   ├── app.py
│   ├── main.py
│   ├── model.py
│   ├── train.py
│   ├── resume_parser.py
│   ├── requirements.txt
│   └── complete_job_roles_model.pkl
│
├── frontend/
│   ├── index.html
│   ├── upload.html
│   ├── styles.css
│   ├── script.js
│   └── vite.config.js
│
├── dataset/
├── run.bat
└── README.md

Installation and Setup
1. Clone the Repository
git clone https://github.com/your-username/SmartHire.git
cd SmartHire

2. Setup Backend
cd backend
pip install -r requirements.txt

3. Start Backend Server
python main.py


Access server at:

http://localhost:5000

4. Run Frontend

Open the frontend folder and run:

npm install
npm run dev

Deployment Link

This helps users, recruiters, and collaborators access the system instantly.

API Endpoints
Endpoint	Method	Description
/	GET	Health check
/predict	POST	Returns top 3 job role predictions
/parse	POST	Extracts content from uploaded resume
Run Script (Windows)

The repository contains a startup script run.bat that:

Verifies Python installation

Installs missing dependencies

Trains the ML model if not present

Launches the Flask server

Run it using:

run.bat

Technologies Used

Python

Flask

scikit-learn

pandas

nltk

JavaScript

HTML/CSS

Vite

Machine Learning algorithms

Contribution Guidelines

Contributions are welcome.

Fork the repository

Create a new feature branch

Commit your changes

Open a Pull Request

License

This project is licensed under the MIT License.

Acknowledgements

This project was developed as an AI-driven solution to streamline HR workflows and improve recruitment efficiency.
