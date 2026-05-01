import os
import time
import uuid
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, send_from_directory, session, url_for
from PIL import Image, UnidentifiedImageError
from werkzeug.utils import secure_filename

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
ALLOWED_FORMATS = {"JPEG", "PNG"}
MAX_FILE_SIZE = 104857600  # 100MB per file (bytes)
CLEANUP_MAX_AGE_SECONDS = 60 * 60  # 1 hour

UPLOAD_DIR.mkdir(exist_ok=True)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 210239488  # 2 x 100MB + 512KB (bytes)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")


def cleanup_old_uploads() -> None:
    now = time.time()
    for file_path in UPLOAD_DIR.glob("*"):
        if file_path.is_file() and (now - file_path.stat().st_mtime) > CLEANUP_MAX_AGE_SECONDS:
            try:
                file_path.unlink()
            except OSError:
                pass


def validate_image_and_get_ext(file_storage, field_name: str) -> str:
    if not file_storage or file_storage.filename == "":
        raise ValueError(f"{field_name} wajib diunggah.")

    raw = file_storage.read()
    if len(raw) > MAX_FILE_SIZE:
        raise ValueError(f"{field_name} melebihi batas 100MB.")

    file_storage.stream.seek(0)

    try:
        img = Image.open(file_storage.stream)
    except UnidentifiedImageError as exc:
        raise ValueError(f"{field_name} bukan gambar valid.") from exc

    if img.format not in ALLOWED_FORMATS:
        raise ValueError(f"{field_name} harus berformat JPG/JPEG/PNG.")

    file_storage.stream.seek(0)
    return ".jpg" if img.format == "JPEG" else ".png"


def save_uploaded_file(file_storage, original_name: str, suffix: str, extension: str) -> str:
    safe_name = secure_filename(original_name) or "image"
    stem = Path(safe_name).stem
    file_name = f"{uuid.uuid4().hex}_{stem}_{suffix}{extension}"
    out_path = UPLOAD_DIR / file_name
    file_storage.save(out_path)
    return file_name


@app.before_request
def perform_cleanup():
    cleanup_old_uploads()


@app.route("/", methods=["GET"])
def index():
    active = session.get("active_uploads", [])
    before_name = active[0] if len(active) > 0 else None
    after_name = active[1] if len(active) > 1 else None

    before_exists = before_name and (UPLOAD_DIR / before_name).exists()
    after_exists = after_name and (UPLOAD_DIR / after_name).exists()

    before_url = url_for("uploaded_file", filename=before_name) if before_exists else None
    after_url = url_for("uploaded_file", filename=after_name) if after_exists else None

    return render_template("index.html", before_url=before_url, after_url=after_url)


@app.route("/compare", methods=["POST"])
def compare():
    try:
        file_a = request.files.get("image_a")
        file_b = request.files.get("image_b")
        ext_a = validate_image_and_get_ext(file_a, "Gambar A")
        ext_b = validate_image_and_get_ext(file_b, "Gambar B")
    except ValueError as err:
        flash(str(err), "error")
        return redirect(url_for("index"))

    before_name = save_uploaded_file(file_a, file_a.filename, "before", ext_a)
    after_name = save_uploaded_file(file_b, file_b.filename, "after", ext_b)
    session["active_uploads"] = [before_name, after_name]

    return render_template(
        "index.html",
        before_url=url_for("uploaded_file", filename=before_name),
        after_url=url_for("uploaded_file", filename=after_name),
    )


@app.route("/reset", methods=["POST"])
def reset():
    active = session.get("active_uploads", [])
    for filename in active:
        file_path = UPLOAD_DIR / filename
        if file_path.is_file():
            try:
                file_path.unlink()
            except OSError:
                pass

    session.pop("active_uploads", None)
    flash("Gambar dan hasil compare berhasil di-reset.", "success")
    return redirect(url_for("index"))


@app.route("/reset-silent", methods=["POST"])
def reset_silent():
    active = session.get("active_uploads", [])
    for filename in active:
        file_path = UPLOAD_DIR / filename
        if file_path.is_file():
            try:
                file_path.unlink()
            except OSError:
                pass

    session.pop("active_uploads", None)
    return ("", 204)


@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_DIR, filename)


@app.errorhandler(413)
def payload_too_large(_error):
    flash("Total upload terlalu besar. Maksimum 100MB per gambar.", "error")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5050)
