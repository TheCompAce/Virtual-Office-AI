@echo off
if not exist env (
    echo Creating virtual environment...
    python -m venv env
    echo.
)

echo Activating virtual environment...
call env\Scripts\activate

echo Updating pip...
python -m pip install --upgrade pip

echo Installing dependencies...
pip install -r requirements.txt | find /V "already satisfied"

echo Running service...
python main.py
