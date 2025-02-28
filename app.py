import os
import numpy as np
import cv2
from flask import Flask, render_template, request, send_file, jsonify
from flask_cors import CORS
from PIL import Image
import piexif

# Initialize Flask App
app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)  # 🔹 Enable CORS to prevent fetch() errors

# Define Upload and Processed folders
UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Increase upload size (10MB max)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024


def remove_metadata(input_path, output_path):
    """ Removes metadata from image """
    img = Image.open(input_path)
    img.save(output_path, "jpeg")  # Saves without metadata


def add_invisible_watermark(image_path):
    """ Adds subtle invisible watermark to prevent AI recognition """
    img = cv2.imread(image_path)
    watermark = np.full(img.shape, (10, 10, 10), dtype=np.uint8)  # Light watermark
    watermarked_img = cv2.addWeighted(img, 1, watermark, 0.02, 0)

    output_path = os.path.join(PROCESSED_FOLDER, "watermarked_" + os.path.basename(image_path))
    cv2.imwrite(output_path, watermarked_img)
    return output_path


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    try:
        processed_path = os.path.join(PROCESSED_FOLDER, "cleaned_" + file.filename)
        remove_metadata(file_path, processed_path)

        watermarked_path = add_invisible_watermark(processed_path)

        return send_file(watermarked_path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, threaded=True)  # Multi-threading for faster processing
