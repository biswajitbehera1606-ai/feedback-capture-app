from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text
from types import SimpleNamespace
from dotenv import load_dotenv
import os
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
os.makedirs(INSTANCE_DIR, exist_ok=True)
load_dotenv(os.path.join(BASE_DIR, ".env"))


def get_database_uri():
    uri = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(INSTANCE_DIR, 'feedback.db')}",
    )
    if uri.startswith("postgresql://"):
        return uri.replace("postgresql://", "postgresql+psycopg://", 1)
    if uri.startswith("postgres://"):
        return uri.replace("postgres://", "postgresql+psycopg://", 1)
    return uri


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")
app.config["SQLALCHEMY_DATABASE_URI"] = get_database_uri()
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    app_name = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    feedback_type = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default="new")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Feedback {self.app_name} - {self.title}>"


APP_FILTERS = [
    ("all", "All"),
    ("NPSCSAT", "NPSCSAT"),
    ("CAMT", "CAMT"),
    ("queue_shift_management", "Queue Shift Management"),
]


def ensure_schema():
    with app.app_context():
        db.create_all()
        inspector = inspect(db.engine)
        if "feedback" not in inspector.get_table_names():
            return

        columns = {column["name"] for column in inspector.get_columns("feedback")}
        if "app_name" not in columns:
            db.session.execute(
                text("ALTER TABLE feedback ADD COLUMN app_name VARCHAR(80) DEFAULT 'NPSCSAT'")
            )
            db.session.execute(
                text("UPDATE feedback SET app_name = 'NPSCSAT' WHERE app_name IS NULL")
            )
            db.session.commit()


def normalize_app_filter(value):
    value = (value or "all").strip()
    return value if value in {item[0] for item in APP_FILTERS} else "all"


ensure_schema()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/submit", methods=["POST"])
def submit_feedback():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    app_name = request.form.get("app_name", "NPSCSAT").strip()
    feedback_type = request.form.get("feedback_type", "idea").strip()
    title = request.form.get("title", "").strip()
    message = request.form.get("message", "").strip()

    if not all([app_name, name, email, title, message]):
        flash("Please fill in all required fields.")
        return redirect(url_for("index"))

    feedback = Feedback(
        app_name=app_name,
        name=name,
        email=email,
        feedback_type=feedback_type,
        title=title,
        message=message,
    )
    db.session.add(feedback)
    db.session.commit()

    flash("Thank you! Your feedback was saved successfully.")
    return redirect(url_for("list_feedbacks"))


@app.route("/feedbacks")
def list_feedbacks():
    selected_app = normalize_app_filter(request.args.get("app", "all"))

    try:
        query = Feedback.query
        if selected_app != "all":
            query = query.filter(Feedback.app_name == selected_app)
        feedbacks = query.order_by(Feedback.created_at.desc()).all()
    except Exception:
        try:
            if selected_app != "all":
                rows = db.session.execute(
                    text(
                        "SELECT id, app_name, name, email, feedback_type, title, message, status, created_at FROM feedback WHERE app_name = :app ORDER BY created_at DESC"
                    ),
                    {"app": selected_app},
                ).mappings().all()
            else:
                rows = db.session.execute(
                    text(
                        "SELECT id, app_name, name, email, feedback_type, title, message, status, created_at FROM feedback ORDER BY created_at DESC"
                    )
                ).mappings().all()
            feedbacks = [
                SimpleNamespace(
                    app_name=row.get("app_name", "NPSCSAT"),
                    name=row.get("name", ""),
                    email=row.get("email", ""),
                    feedback_type=row.get("feedback_type", "other"),
                    title=row.get("title", ""),
                    message=row.get("message", ""),
                    created_at=row.get("created_at"),
                )
                for row in rows
            ]
        except Exception:
            feedbacks = []

    return render_template(
        "feedbacks.html",
        feedbacks=feedbacks,
        selected_app=selected_app,
        app_filters=APP_FILTERS,
    )


@app.route("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=False)
