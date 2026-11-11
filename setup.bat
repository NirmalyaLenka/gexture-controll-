@echo off
setlocal
echo Hand Gesture Control - Setup
echo ==============================
echo.

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Python was not found. Install Python 3.11 from https://python.org
    echo Enable "Add Python to PATH" during installation.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo Creating project virtual environment...
    python -m venv .venv
    if errorlevel 1 goto :fail
)

echo Installing dependencies from requirements.txt...
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto :fail

".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto :fail

echo.
echo Verifying imports...
".venv\Scripts\python.exe" -c "import cv2, mediapipe, numpy, keyboard, mouse, screen_brightness_control; print('Dependency imports succeeded')"
if errorlevel 1 goto :fail

echo.
echo Setup complete.
echo Run the project with:
echo     .venv\Scripts\python.exe gesture_control.py
echo.
pause
exit /b 0

:fail
echo.
echo Setup failed. Read the error above, then check Python, network access and package compatibility.
pause
exit /b 1
