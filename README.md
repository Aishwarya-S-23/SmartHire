Smart Hire: Automated Resume Screening and Job Role Recommendation System
Overview

Smart Hire is an AI-based resume screening and job-matching system designed to streamline the hiring workflow. It automatically analyzes candidate resumes, processes key information, and predicts the top three job roles that best match the candidate’s profile.
This system replicates the initial screening tasks typically performed by Human Resources teams, enabling faster, more consistent, and data-driven candidate evaluation.

The application includes:

A machine learning model trained on categorized job data.

A Flask backend API for parsing resumes and generating predictions.

A frontend interface for uploading resumes and viewing recommended roles.

Features
Resume Screening

Parses resumes to extract key skills, experience, and relevant attributes required for job classification.

Job Role Classification

Predicts the best three job roles a candidate is suited for based on model inference.

Automated HR Shortlisting

Replaces manual initial screening with an intelligent and scalable decision system.

Frontend and Backend Architecture

Includes a complete backend (Flask, model pipeline, data loaders) and frontend built with HTML, CSS, JavaScript, and Vite.

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
│   ├── complete_job_roles_model.pkl
│   └── dataset/
│
├── frontend/
│   ├── index.html
│   ├── upload.html
│   ├── script.js
│   ├── styles.css
│   ├── vite.config.js
│   └── src/
│
├── run.bat
└── README.md

Installation
Prerequisites

Python 3.7 or higher

pip package manager

Node.js (optional, for frontend builds)

Backend Setup

Navigate to the backend directory:

cd backend


Install required packages:

pip install -r requirements.txt


Ensure that the trained model file complete_job_roles_model.pkl exists.
If not, run:

python train.py


Start the Flask backend server:

python main.py


The server will start at:

http://localhost:5000

Frontend Setup

Navigate to the frontend directory:

cd frontend


Install dependencies:

npm install


Start the development server:

npm run dev


Frontend runs at:

http://localhost:5173

API Endpoints
Health Check
GET /health


Returns basic service availability.

Predict Job Roles
POST /predict


Accepts a resume file and returns the top three job roles.

Running the Entire System via run.bat

The provided batch script:

Verifies Python installation.

Installs required dependencies.

Trains the model if missing.

Starts the backend Flask server.

Run:

run.bat

Deployment Notes

Backend can be deployed on Render, Railway, or any Python-compatible hosting.

Frontend can be deployed on Vercel, Netlify, or GitHub Pages.

Ensure environment variables and Python paths are set correctly on the deployment platform.

Conclusion

Smart Hire brings automation, precision, and efficiency to the hiring pipeline by intelligently matching candidates to the roles they are most suitable for.
It acts as a rapid-screening assistant for HR teams, saving time and improving the quality of shortlisting.
