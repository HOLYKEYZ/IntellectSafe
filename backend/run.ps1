# PowerShell script to run the API from correct directory

Set-Location $PSScriptRoot
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
