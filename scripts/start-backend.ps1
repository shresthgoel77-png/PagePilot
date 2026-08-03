powershell
Set-Location -Path "backend"
if (-Not (Test-Path "venv")) {
    python -m venv venv
}
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
