@echo off
title Smart Hire System
echo ========================================
echo        SMART HIRE JOB MATCHING SYSTEM
echo ========================================
echo.

:: Change to backend directory where the Python files are
cd backend

:: Check Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)

echo ✅ Python found
echo.

:: Check if requirements are installed
echo 🔍 Checking dependencies...
pip list | findstr "flask scikit-learn pandas nltk" >nul
if errorlevel 1 (
    echo 📥 Installing required packages...
    pip install -r ../requirements.txt
) else (
    echo ✅ All dependencies are installed
)

echo.

:: Check if model exists
if not exist "complete_job_matching_system.pkl" (
    echo 📊 Model not found. Training model first...
    echo This may take several minutes...
    echo.
    python train.py
    if errorlevel 1 (
        echo ❌ Training failed!
        pause
        exit /b 1
    )
) else (
    echo ✅ Pre-trained model found
)

echo.
echo 🌐 Starting Flask server...
echo 📍 Open your browser to: http://localhost:5000
echo 📍 API Health check: http://localhost:5000/health
echo 📍 Make predictions: http://localhost:5000/predict
echo.
echo 🛑 Press Ctrl+C to stop the server
echo ========================================
echo.

python main.py


pause