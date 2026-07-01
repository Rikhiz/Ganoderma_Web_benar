"""
GANODERMA_WEB — Local web app for Ganoderma detection using a trained YOLO model.

Run locally with:
    pip install -r requirements.txt
    python app.py

Then open http://127.0.0.1:5000 in your browser.
"""

import os
import shutil
import uuid
from datetime import datetime

from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, "input")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
MODEL_PATH = os.path.join(BASE_DIR, "model", "best.pt")

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "bmp", "webp"}

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024  # 25 MB per upload

os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Model is loaded once at startup so every prediction is fast.
_model = None


def get_model():
    """Lazily load the YOLO model so the server still starts even if
    best.pt isn't in place yet (the upload page will just show an error
    on predict instead of crashing on launch)."""
    global _model
    if _model is None:
        from ultralytics import YOLO

        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Model tidak ditemukan di '{MODEL_PATH}'. "
                f"Pastikan file best.pt sudah diletakkan di folder model/."
            )
        _model = YOLO(MODEL_PATH)
    return _model


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    if "image" not in request.files:
        return jsonify({"error": "Tidak ada file gambar yang dikirim."}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "Nama file kosong."}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Format file tidak didukung. Gunakan JPG, PNG, atau WEBP."}), 400

    # Save the incoming image into input/ with a unique, collision-free name
    ext = file.filename.rsplit(".", 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    saved_path = os.path.join(INPUT_DIR, unique_name)
    file.save(saved_path)

    # A fresh run folder per request, mirroring the runs/detect/predict pattern
    run_name = f"predict_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"

    try:
        model = get_model()
        results = model.predict(
            source=saved_path,
            save=True,
            project=OUTPUT_DIR,
            name=run_name,
            exist_ok=True,
        )
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:  # noqa: BLE001 - surface any inference error to the UI
        return jsonify({"error": f"Gagal menjalankan model: {e}"}), 500

    # Locate the annotated image YOLO just wrote to output/<run_name>/
    run_dir = os.path.join(OUTPUT_DIR, run_name)
    annotated_file = None
    if os.path.isdir(run_dir):
        for f in os.listdir(run_dir):
            if f.lower().endswith((".jpg", ".jpeg", ".png")):
                annotated_file = f
                break

    if annotated_file is None:
        return jsonify({"error": "Model berhasil dijalankan tetapi hasil gambar tidak ditemukan."}), 500

    # Summarize detections for the UI
    detections = []
    if results:
        r = results[0]
        names = r.names
        if r.boxes is not None:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                detections.append({
                    "label": names.get(cls_id, str(cls_id)) if isinstance(names, dict) else names[cls_id],
                    "confidence": round(conf * 100, 1),
                })

    return jsonify({
        "success": True,
        "result_image": f"/output/{run_name}/{annotated_file}",
        "detections": detections,
        "run_name": run_name,
    })


@app.route("/output/<path:filename>")
def serve_output(filename):
    return send_from_directory(OUTPUT_DIR, filename)


@app.route("/model-status")
def model_status():
    exists = os.path.exists(MODEL_PATH)
    return jsonify({"model_found": exists, "path": MODEL_PATH})


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
