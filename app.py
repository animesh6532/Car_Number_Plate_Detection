import os
import uuid
import base64
import cv2
import numpy as np
from flask import Flask, render_template, request, jsonify, url_for, redirect
from werkzeug.utils import secure_filename
from src.detector import detector_instance

app = Flask(__name__)

# =========================
# PATH CONFIG
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'static')
UPLOAD_FOLDER = os.path.join(STATIC_DIR, 'uploads')
OUTPUT_FOLDER = os.path.join(STATIC_DIR, 'outputs')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# =========================
# ROUTES
# =========================

@app.route('/')
def index():
    return render_template('index.html')


# =========================
# IMAGE UPLOAD
# =========================
@app.route("/upload", methods=["POST"])
def upload_file():
    # 🔥 SAFE FILE HANDLING
    file = request.files.get("file")

    if file is None or file.filename == "":
        return "No file uploaded", 400

    if not allowed_file(file.filename):
        return "Invalid file type", 400

    # Secure filename
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    # Read image
    img = cv2.imread(filepath)

    if img is None:
        return "Invalid image", 400

    # 🔥 UPDATED PIPELINE (3 VALUES)
    annotated_img, plate_img, text = detector_instance.process_pipeline(img)

    # Save annotated image
    output_path = os.path.join(app.config["OUTPUT_FOLDER"], filename)
    cv2.imwrite(output_path, annotated_img)

    # Save plate image
    plate_url = None
    if plate_img is not None:
        plate_filename = "plate_" + filename
        plate_path = os.path.join(app.config["OUTPUT_FOLDER"], plate_filename)
        cv2.imwrite(plate_path, plate_img)
        plate_url = f"/static/outputs/{plate_filename}"

    return render_template(
        "index.html",
        result=f"/static/outputs/{filename}",
        plate=plate_url,
        text=text
    )


# =========================
# CAMERA PAGE
# =========================
@app.route('/camera')
def camera():
    return render_template('camera.html')


# =========================
# CAMERA PROCESSING
# =========================
@app.route('/upload_camera', methods=['POST'])
def upload_camera():
    data = request.json

    if not data or 'image' not in data:
        return jsonify({'error': 'No image data provided'})

    try:
        img_data_str = data['image']

        # Remove base64 header
        if ',' in img_data_str:
            img_data_str = img_data_str.split(',', 1)[1]

        # Decode
        img_bytes = base64.b64decode(img_data_str)
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            return jsonify({'error': 'Invalid image'})

        # 🔥 UPDATED PIPELINE (3 VALUES)
        annotated_img, plate_img, text = detector_instance.process_pipeline(img)

        # Save annotated image
        unique_name = f"cam_{uuid.uuid4().hex}.jpg"
        out_path = os.path.join(app.config['OUTPUT_FOLDER'], unique_name)
        cv2.imwrite(out_path, annotated_img)

        return jsonify({
            'success': True,
            'image_url': f"/static/outputs/{unique_name}",
            'text': text
        })

    except Exception as e:
        print(f"Camera Error: {e}")
        return jsonify({'error': str(e)})


# =========================
# MAIN
# =========================
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)