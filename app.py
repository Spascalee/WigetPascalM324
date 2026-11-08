from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    jsonify,
)
from datetime import datetime
from dataclasses import dataclass, field
from pathlib import Path
import os
from dotenv import load_dotenv

app = Flask(__name__)
app.secret_key = os.urandom(24)
load_dotenv()
PASSWORD = os.getenv("PASSWORD")
entries = []

# Die Datei VERSION wird erst beim Release aus dem Git-Tag erzeugt
VERSION_FILE = Path(__file__).with_name("VERSION")


def read_version(version_file=VERSION_FILE):
    """Liefert die ausgelieferte Version, lokal ohne VERSION-Datei "dev"."""
    try:
        version = Path(version_file).read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return "dev"
    return version or "dev"


APP_VERSION = read_version()


@dataclass
class Entry:
    content: str
    # default_factory: Zeit bei jedem neuen Eintrag ermitteln, nicht einmal beim Start
    timestamp: datetime = field(default_factory=datetime.now)
    happiness: str = ""


@app.route("/")
def index():
    return render_template("index.html", entries=entries)


@app.route("/health")
def health():
    # Wird nach jedem Deployment vom Smoke-Test abgefragt
    return jsonify(status="ok", version=APP_VERSION)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_password = request.form.get("password")
        if user_password == PASSWORD:
            session["logged_in"] = True
            flash("Login successful!", "success")
            return redirect(url_for("index"))
        else:
            flash("Incorrect password. Please try again.", "error")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    flash("Logged out successfully.", "success")
    return redirect(url_for("index"))


@app.route("/add_entry", methods=["POST"])
def add_entry():
    content = request.form.get("content")
    happiness = request.form.get("happiness", "")
    if content:
        entry = Entry(content=content, happiness=happiness)
        entries.append(entry)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0")
