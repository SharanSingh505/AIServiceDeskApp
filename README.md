# AI Service Desk Assistant — Local MVP

This local-only MVP uses fictional sample data. It does not connect to ServiceNow, Microsoft 365, Dataverse, or Azure.

## What it demonstrates

- Lists sample incidents
- Matches ticket category to engineer skills
- Accounts for workload and availability
- Estimates resolution time against a priority-based SLA target
- Explains the recommendation and keeps a human approval step

## Prerequisite

Install **Python 3.11 or newer** from [python.org](https://www.python.org/downloads/windows/). In the installer, select **Add python.exe to PATH**.

## Run

Open PowerShell in this folder and run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```

Then open http://127.0.0.1:8000 in a browser.

## Test

With the virtual environment active:

```powershell
python -m unittest discover -s tests -v
```

## Next integration steps

1. Replace `sample_data.py` with Dataverse tables or approved ServiceNow development data.
2. Add a least-privilege ServiceNow API adapter.
3. Expose selected backend actions as MCP tools.
4. Call the backend from Power Automate and Copilot Studio.
5. Replace the local page with a Power Apps manager dashboard.
