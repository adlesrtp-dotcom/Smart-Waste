import os
import uuid
import base64
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from ultralytics import YOLO

app = Flask(__name__)

# Konfigurasi Folder & Limit Upload
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # Maksimal 5 MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Kamus Penerjemahan Kelas Dataset ke Bahasa Indonesia
TERJEMAHAN = {
    "cardboard": "Kardus",
    "glass": "Kaca",
    "metal": "Logam",
    "paper": "Kertas",
    "plastic": "Plastik",
}

# Threshold Kepercayaan Minimal (Di bawah 50% dianggap ragu-ragu)
CONFIDENCE_THRESHOLD = 50.0

# Load Model AI (best.pt)
MODEL_PATH = "best.pt"
model = None

if os.path.exists(MODEL_PATH):
    try:
        model = YOLO(MODEL_PATH)
        print("Model AI 'best.pt' berhasil dimuat.")
    except Exception as e:
        print(f"Gagal memuat model: {e}")
else:
    print("Warning: File 'best.pt' tidak ditemukan di folder utama proyek.")


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("index.html")


# Halaman deteksi sampah (Form Upload Tradisional)
@app.route("/deteksi", methods=["GET", "POST"])
def deteksi():
    pesan = None
    hasil = None
    prediksi = None
    confidence = None

    if request.method == "POST":
        file = request.files.get("gambar") or request.files.get("file")

        if not file or file.filename == "":
            pesan = "Silakan pilih gambar sampah terlebih dahulu."
        elif not allowed_file(file.filename):
            pesan = "Format gambar harus JPG, JPEG, PNG, atau WEBP."
        elif model is None:
            pesan = "Model AI belum tersedia. Pastikan file best.pt berada di folder proyek."
        else:
            ekstensi = file.filename.rsplit(".", 1)[1].lower()
            filename = f"{uuid.uuid4().hex}.{ekstensi}"
            filepath = os.path.join(UPLOAD_FOLDER, filename)

            try:
                file.save(filepath)

                # Inferensi Model Klasifikasi
                results = model.predict(source=filepath, imgsz=224, verbose=False)
                result = results[0]

                class_id = int(result.probs.top1)
                conf_val = float(result.probs.top1conf) * 100
                nama_kelas = result.names[class_id]

                confidence = round(conf_val, 2)
                
                # Cek Threshold Confidence
                if confidence < CONFIDENCE_THRESHOLD:
                    prediksi = "Sampah Tidak Terdeteksi / Ragu-ragu"
                    pesan = f"Model AI kurang yakin dengan objek ini (Keyakinan: {confidence}%)."
                else:
                    prediksi = TERJEMAHAN.get(nama_kelas.lower(), nama_kelas.title())
                    pesan = f"Hasil klasifikasi: {prediksi}. Tingkat keyakinan model: {confidence}%."

                hasil = filename

            except Exception as e:
                print(f"Terjadi kesalahan saat deteksi: {e}")
                pesan = "Maaf, gambar gagal diproses. Silakan coba gambar lain."
                if os.path.exists(filepath):
                    os.remove(filepath)

    return render_template(
        "deteksi.html",
        pesan=pesan,
        hasil=hasil,
        prediksi=prediksi,
        confidence=confidence,
    )


# API Endpoint khusus untuk Modal Scanner AI (Base64 & Multipart File)
@app.route("/predict", methods=["POST"])
def predict_api():
    if model is None:
        return jsonify({"error": "Model AI belum dimuat."}), 500

    filepath = None
    try:
        # Case 1: Request JSON Base64 (dari kamera/upload modal index.html)
        if request.is_json:
            data = request.get_json()
            image_data = data.get("image")
            
            if not image_data:
                return jsonify({"error": "Data gambar tidak ditemukan."}), 400

            header, encoded = image_data.split(",", 1) if "," in image_data else ("", image_data)
            file_bytes = base64.b64decode(encoded)
            
            filename = f"{uuid.uuid4().hex}.jpg"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            
            with open(filepath, "wb") as f:
                f.write(file_bytes)

        # Case 2: Request Multipart Form-Data
        elif "gambar" in request.files or "file" in request.files:
            file = request.files.get("gambar") or request.files.get("file")
            if not file or file.filename == "":
                return jsonify({"error": "Tidak ada file yang dipilih."}), 400
            
            ekstensi = file.filename.rsplit(".", 1)[1].lower() if "." in file.filename else "jpg"
            filename = f"{uuid.uuid4().hex}.{ekstensi}"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
        else:
            return jsonify({"error": "Format request tidak dikenali."}), 400

        # Run Prediction
        results = model.predict(source=filepath, imgsz=224, verbose=False)
        result = results[0]

        class_id = int(result.probs.top1)
        conf_val = float(result.probs.top1conf) * 100
        nama_kelas = result.names[class_id]

        confidence = round(conf_val, 1)

        # Cek apakah akurasi memenuhi batas minimal 50%
        if confidence < CONFIDENCE_THRESHOLD:
            prediksi = "Tidak Terdeteksi"
        else:
            prediksi = TERJEMAHAN.get(nama_kelas.lower(), nama_kelas.title())

        return jsonify({
            "success": True,
            "class": prediksi,
            "label": prediksi,
            "confidence": confidence,
            "image_url": f"/uploads/{filename}"
        })

    except Exception as e:
        print(f"Error pada API /predict: {e}")
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({"error": "Gagal memproses gambar."}), 500


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.errorhandler(413)
def file_too_large(error):
    return (
        render_template(
            "deteksi.html",
            pesan="Ukuran gambar maksimal 5 MB.",
            hasil=None,
            prediksi=None,
            confidence=None,
        ),
        413,
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)