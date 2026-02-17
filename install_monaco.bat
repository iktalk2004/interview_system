@echo off
REM 安装代码编辑器依赖

echo ========================================
echo Installing Monaco Editor
echo ========================================
echo.

cd frontend

echo Installing monaco-editor...
call npm install monaco-editor

if %errorlevel% neq 0 (
    echo.
    echo ========================================
    echo Installation failed!
    echo ========================================
    pause
    exit /b 1
)

echo.
echo ========================================
echo Installation completed successfully!
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

pause
