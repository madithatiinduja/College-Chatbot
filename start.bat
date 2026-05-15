@echo off
echo ========================================
echo    Cllg Chatbot - Starting Server
echo ========================================
echo.
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo Starting Flask server...
echo.
echo The chatbot will be available at:
echo http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.
python app.py
pause 