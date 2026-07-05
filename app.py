from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
os.makedirs(INSTANCE_DIR, exist_ok=True)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL",
    f"sqlite:///{os.path.join(INSTANCE_DIR, 'feedback.db')}",
)
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


with app.app_context():
    db.create_all()


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
    feedbacks = Feedback.query.order_by(Feedback.created_at.desc()).all()
    return render_template("feedbacks.html", feedbacks=feedbacks)


@app.route("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=False)
