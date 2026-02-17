@echo off
REM 代码题目模块快速启动脚本

echo ========================================
echo Code Questions Module Setup
echo ========================================
echo.

cd /d "%~dp0"

echo [1/5] Installing frontend dependencies...
cd frontend
call npm install monaco-editor
cd ..

echo.
echo [2/5] Creating database migrations...
cd backend
python manage.py makemigrations code_questions

echo.
echo [3/5] Applying database migrations...
python manage.py migrate code_questions

echo.
echo [4/5] Generating sample code questions...
python manage.py generate_code_questions

echo.
echo [5/5] Setup completed!
echo ========================================
echo.
echo Next steps:
echo 1. Start backend server:
echo    cd backend
echo    python manage.py runserver
echo.
echo 2. Start frontend server:
echo    cd frontend
echo    npm run dev
echo.
echo 3. Access code practice page:
echo    http://localhost:5173/code-practice
echo.
echo ========================================

pause
