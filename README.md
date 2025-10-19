# Service Appointment Booking System (Flask)

Minimal Flask-based booking system scaffold implementing:

1. User management (register/login, roles: admin/staff/customer, profiles)
2. Service management (services with price/duration, categories)
3. Booking system (view availability, book by date/time, assign staff)
4. Notifications (email/SMS simulation, scheduler reminders)

This is a starter project to be expanded. To run (PowerShell):

1. Create virtualenv and activate

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
``` 

2. Initialize DB and run

```powershell
python -c "from app import create_app, db; app=create_app(); ctx=app.app_context(); ctx.push(); db.create_all(); print('DB created')"
$env:FLASK_APP='app:create_app' ; flask run
```

Default config uses SQLite and console email backend.

Notes: This is a scaffold. Implement additional validations and security for production use.