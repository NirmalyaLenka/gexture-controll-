@echo off
echo Hand Gesture Control - Setup
echo ==============================
echo.

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found. Please install Python 3.11 from https://python.org
    echo Make sure to tick "Add Python to PATH" during install.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYVER=%%i
echo Found: %PYVER%
echo.

echo Installing required packages...
python -m pip install --upgrade pip
python -m pip install opencv-python mediapipe numpy keyboard mouse screen-brightness-control

echo.
echo Verifying installation...
python -c "import cv2, mediapipe, numpy, keyboard, mouse; print('All packages installed successfully')"

if %errorlevel% neq 0 (
    echo.
    echo Something went wrong. Check the errors above.
    pause
    exit /b 1
)

echo.
echo Setup complete. Run the project with:
echo     python gesture_control.py
echo.
pause
