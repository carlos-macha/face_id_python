@echo off
call venv\Scripts\activate
uvicorn app.main:app --reload
pause

# .\start_server.bat