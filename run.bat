@echo off
if not exist env (
    echo Creating virtual environment...
    C:\Python310\python -m venv env python==3.10.0
    echo.
)

echo Activating virtual environment...
call env\Scripts\activate

echo Updating pip...
python -m pip install --upgrade pip

call env\Scripts\deactivate

echo Activating virtual environment...
call env\Scripts\activate

echo Installing dependencies...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 | find /V "already satisfied"
pip install -r requirements.txt | find /V "already satisfied"

echo Running service...
python main.py
