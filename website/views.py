from flask import Blueprint, render_template, request
from website.redactor import redact_text
views = Blueprint('views', __name__)

@views.route('/', methods=["GET", "POST"])
def home():
    redacted_output = None
    if request.method == "POST":
        uploaded_file = request.files.get("file")
        if uploaded_file and uploaded_file.filename.endswith(".txt"):
            text = uploaded_file.read().decode("utf-8")
            redacted_output = redact_text(text)
    return render_template("home.html", redacted_output=redacted_output)
