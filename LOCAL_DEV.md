# Local Development Execution Note

When running the FastAPI backend locally, Windows developers MUST use `scripts/start-backend.ps1` in PowerShell instead of the Unix `sh` script.

This is because the `source` command is natively invalid in PowerShell. Attempting to use `source` or Unix-style shell scripts on Windows to activate the `venv` will silently fail the activation layer, causing dependencies (like `pydantic-settings`) to be installed into your system-wide Python environment rather than the target virtual environment where `uvicorn` executes, thus resulting in `ModuleNotFoundError` crashes.

If you are activating manually via terminal: 
- PowerShell: `.\venv\Scripts\Activate.ps1`
- Command Prompt: `venv\Scripts\activate.bat` 
Do not use `source venv/Scripts/activate` on Windows, as it doesn't work. Once activated, strictly run `pip install -r requirements.txt` inside.
