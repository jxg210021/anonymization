from flask import Flask, Blueprint, render_template, request, flash, redirect, url_for, send_file, session
import io

from website.redactor import clean_text, generate_uuid, get_uuid
from website.uuids import init_uuids, get_uuids, update_uuids
from . import db
from .models import TextFile


views = Blueprint('views', __name__)

@views.route('/', methods=["GET", "POST"])
def home():
    redacted_output = None

    if request.method == "POST":
        uploaded = request.files.get("file")
        if uploaded and uploaded.filename.endswith(".txt"):
            raw = uploaded.read().decode("utf-8")

            # Build filters dict from checkbox names
            filters = {
                'phone':           'phone' in request.form,
                'dates':           'dates' in request.form,
                'dob':             'dob' in request.form,
                'email':           'email' in request.form,
                'name':            'name' in request.form,
                'address':         'address' in request.form,
                'ssn':             'ssn' in request.form,
                'acct':            'acct' in request.form,
                'allergies':       'allergies' in request.form,
                'allergy_list':    [],  # populate if you want custom allergy words
                'results':         'results' in request.form,
                'beneficiary_num': 'beneficiary_num' in request.form,
                'record_num':      'record_num' in request.form,
                'certificate':     'certificate' in request.form,
                'license':         'license' in request.form,
                'serial':          'serial' in request.form,
                'identifier':      'identifier' in request.form,
                'url':             'url' in request.form,
                'code':            'code' in request.form,
            }

            # Call w/ user’s filter choices
            uuid = generate_uuid()
            redacted_output = clean_text(raw, filters, uuid)
            
            unredacted_file = TextFile(id=str(uuid),content=raw)
            db.session.add(unredacted_file)
            db.session.commit()

            print(f"Added uuid {uuid} to database")
            
        else:
            flash("Please upload a valid .txt file.", "error")

    return render_template("home.html", redacted_output=redacted_output)

@views.route("/unredact", methods=["POST"])
def unredact():

    redacted_text = request.form.get("redacted_text")
    if not redacted_text:
        flash("No text to unredact.", "error")
        return redirect(url_for("views.home"))

    uuid = get_uuid(redacted_text)
    try:
        text = str(TextFile.query.get(uuid).content)
    except:
        print(uuid)
        unredacted_output = "Error: unable to find file"

    return render_template("home.html", redacted_output=None, unredacted_output=text)


@views.route("/download", methods=["POST"])
def download():
    """Send the redacted text back to the user as a .txt attachment."""
    redacted_text = request.form.get("redacted_text")

    if not redacted_text:                       # someone typed /download directly
        flash("Nothing to download.", "error")
        return redirect(url_for("views.home"))

    buffer = io.BytesIO()                       # in-memory file
    buffer.write(redacted_text.encode("utf-8"))
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="redacted.txt",
        mimetype="text/plain",
    )
