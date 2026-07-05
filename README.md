# Feedback Capture Web App

This app provides a feedback form for users to submit enhancement requests and ideas, and a screen to view all captured feedback.

## Features

- Public form for feedback submission
- Admin-style list screen for reviewing all feedback
- Data stored in a database
- Works well as a web URL opened from your VoltMX app

## Local run

```bash
cd feebackcaptureApp
python3 -m pip install -r requirements.txt
python3 app.py
```

Open:

- http://127.0.0.1:5000/
- http://127.0.0.1:5000/feedbacks

## Database configuration

By default the app uses a local SQLite file named `feedback.db`.

To use your VM database, set an environment variable before starting the app:

```bash
export DATABASE_URL="postgresql://user:password@your-vm-host:5432/feedbackdb"
```

If you want to use MySQL instead, use a MySQL connection string supported by SQLAlchemy.

## VM deployment

1. Copy this folder to your VM.
2. Install Python 3 and pip.
3. Install requirements with `pip install -r requirements.txt`.
4. Start the app with a process manager such as `systemd`, `gunicorn`, or `pm2`.
5. Make sure port 5000 (or your chosen port) is open in the VM firewall.
6. Use the public VM URL in your VoltMX app button.

## VoltMX integration

In your VoltMX app, open the URL of this app from the feedback button:

```text
http://<vm-public-ip-or-domain>:5000/
```

That screen can collect the feedback and save it to your database.
