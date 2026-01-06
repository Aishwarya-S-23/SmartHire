
# Smart Hire – Automated Resume Screening and Job Role Recommendation

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![Flask](https://img.shields.io/badge/flask-2.0+-white.svg)

**Smart Hire** is an AI-powered resume analysis system that automatically screens candidate resumes, extracts key information, and predicts the top three most suitable job roles. It is designed to reduce manual HR workload and speed up the hiring decision process.

## 📋 Overview

Smart Hire performs automated candidate evaluation through the following core steps:

1.  **Resume Parsing:** Automated data extraction from PDF/Word resumes.
2.  **Skill Analysis:** Extraction and analysis of skills and experience levels.
3.  **Prediction:** Model-based prediction of the top 3 most suitable job roles.
4.  **Integration:** An API-driven backend connected to a user-friendly frontend.
5.  **Automation:** End-to-end automation of tasks typically handled manually by HR.

## ✨ Features

-   🤖 **Automated Resume Screening:** Instantly processes uploaded resumes.
-   🎯 **Top 3 Predictions:** Uses machine learning to suggest the best-fit job roles.
-   🌐 **Flask-Powered Backend:** Robust API for handling prediction requests.
-   💻 **Clean Frontend:** Simple, intuitive interface built with Vite and vanilla JavaScript.
-   🧠 **ML Ready:** Supports pre-trained or dynamically trained models.
-   🚀 **Deployment Ready:** Configured for easy deployment on Render, Railway, or Vercel.

## 🛠 Technologies Used

### Backend & AI
-   **Python:** Core programming language.
-   **Flask:** Web framework for the API.
-   **scikit-learn:** Machine learning library for predictions.
-   **pandas:** Data manipulation and analysis.
-   **nltk:** Natural language processing for text extraction.

### Frontend
-   **JavaScript:** Frontend logic.
-   **HTML/CSS:** Structure and styling.
-   **Vite:** Build tool and dev server.

## 📂 Project Structure

```text
SmartHire/
│
├── backend/
│   ├── app.py              # Flask App Factory
│   ├── main.py             # Entry point
│   ├── model.py            # ML Model definitions
│   ├── train.py            # Script to train the model
│   ├── resume_parser.py    # Logic to parse resume files
│   ├── requirements.txt    # Python dependencies
│   └── complete_job_roles_model.pkl # Serialized Model
│
├── frontend/
│   ├── index.html
│   ├── upload.html
│   ├── styles.css
│   ├── script.js
│   └── vite.config.js
│
├── dataset/                # Training data
├── run.bat                 # Windows startup script
└── README.md               # This file
```

## 🚀 Installation and Setup

### Prerequisites
-   **Python 3.8+**
-   **Node.js & npm** (for the frontend)

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/SmartHire.git
cd SmartHire
```

### 2. Setup Backend

Navigate to the backend directory and install dependencies.

```bash
cd backend
pip install -r requirements.txt
```

### 3. Start Backend Server

Launch the Flask server.

```bash
python main.py
```

The backend will be available at: **http://localhost:5000**

### 4. Run Frontend

Open a new terminal, navigate to the frontend folder, and run the Vite server.

```bash
cd frontend
npm install
npm run dev
```

Access the frontend interface at the URL provided in the terminal (usually **http://localhost:5173**).

---

### Quick Start (Windows)

The repository includes a startup script (`run.bat`) that handles the backend setup automatically.

1.  Double-click `run.bat`.
2.  The script will:
    *   Verify Python installation.
    *   Install missing dependencies.
    *   Train the ML model if the `.pkl` file is missing.
    *   Launch the Flask server.

## 🔌 API Endpoints

| Endpoint | Method | Description                               |
|----------|--------|-------------------------------------------|
| `/`      | GET    | Health check                              |
| `/predict` | POST  | Returns top 3 job role predictions        |
| `/parse` | POST   | Extracts text content from uploaded resume |

## 🌐 Deployment Link

This project is ready for deployment. You can deploy the backend on **Render** or **Railway** and the frontend on **Vercel**.

> **Access the live application here:** `[Insert Live Deployment Link Here]`

## 🤝 Contribution Guidelines

Contributions are welcome to improve Smart Hire!

1.  Fork the repository.
2.  Create a new feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

## 📄 License

This project is licensed under the **MIT License**.

## 🙏 Acknowledgements

This project was developed as an AI-driven solution to streamline HR workflows and improve recruitment efficiency.
