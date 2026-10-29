import os
import uuid
import base64
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from ultralytics import YOLO

app = Flask(__name__)

<<<<<<< HEAD
# Konfigurasi Folder & Limit Upload
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

=======
# Konfigurasi Path Absolut Berdasarkan Lokasi File
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
SAMPLE_FOLDER = os.path.join(BASE_DIR, "static", "samples")
MODEL_PATH = os.path.join(BASE_DIR, "best.pt")

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
>>>>>>> 5e47824 (Update model AI best.pt dan perbaikan backend)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # Maksimal 5 MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SAMPLE_FOLDER, exist_ok=True)

# Kamus Penerjemahan Kelas Dataset ke Bahasa Indonesia
TERJEMAHAN = {
    "cardboard": "Kardus",
    "glass": "Kaca",
    "metal": "Logam",
    "paper": "Kertas",
    "plastic": "Plastik",
}

<<<<<<< HEAD
# Threshold Kepercayaan Minimal (Di bawah 50% dianggap ragu-ragu)
CONFIDENCE_THRESHOLD = 50.0

# Load Model AI (best.pt)
MODEL_PATH = "best.pt"
model = None

=======
# Saran Pemilahan dan Daur Ulang Edukatif
SARAN = {
    "Kardus": "Pisahkan kardus dari sampah basah dan lipat rapi sebelum dimasukkan ke tempat daur ulang.",
    "Kertas": "Kumpulkan kertas secara terpisah dan pastikan tetap kering untuk memudahkan daur ulang.",
    "Plastik": "Kosongkan sisa isi dan bilas kemasan, lalu kumpulkan di tempat sampah anorganik/plastik.",
    "Logam": "Pisahkan benda logam atau kaleng, pipihkan bila memungkinkan untuk efisiensi ruang daur ulang.",
    "Kaca": "Pisahkan kaca dengan hati-hati dalam wadah khusus, hindari kontak langsung dengan pecahan tajam.",
}

# Daftar Data Sampel yang Disediakan dari Dataset
SAMPLE_DATA = [
    {"id": "kardus", "file": "kardus.jpg", "label": "Kardus", "desc": "Contoh kemasan karton/kardus"},
    {"id": "kaca", "file": "kaca.jpg", "label": "Kaca", "desc": "Contoh botol/wadah kaca"},
    {"id": "logam", "file": "logam.jpg", "label": "Logam", "desc": "Contoh kaleng minuman logam"},
    {"id": "kertas", "file": "kertas.jpg", "label": "Kertas", "desc": "Contoh lembaran kertas bekas"},
    {"id": "plastik", "file": "Plastik", "file_name": "plastik.jpg", "label": "Plastik", "desc": "Contoh botol kemasan plastik"}
]

# Normalisasi file key untuk template
for s in SAMPLE_DATA:
    if "file_name" not in s:
        s["file_name"] = s["file"]

# Threshold Kepercayaan Minimal
CONFIDENCE_THRESHOLD = 50.0

# Load Model AI
model = None
>>>>>>> 5e47824 (Update model AI best.pt dan perbaikan backend)
if os.path.exists(MODEL_PATH):
    try:
        model = YOLO(MODEL_PATH)
        print("Model AI 'best.pt' berhasil dimuat.")
    except Exception as e:
        print(f"Gagal memuat model: {e}")
else:
<<<<<<< HEAD
    print("Warning: File 'best.pt' tidak ditemukan di folder utama proyek.")
=======
    print(f"Warning: File '{MODEL_PATH}' tidak ditemukan.")
>>>>>>> 5e47824 (Update model AI best.pt dan perbaikan backend)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("index.html", samples=SAMPLE_DATA)


<<<<<<< HEAD
# Halaman deteksi sampah (Form Upload Tradisional)
=======
# Halaman deteksi sampah (Form Upload & Sampel)
>>>>>>> 5e47824 (Update model AI best.pt dan perbaikan backend)
@app.route("/deteksi", methods=["GET", "POST"])
def deteksi():
    pesan = None
    hasil = None
    prediksi = None
    confidence = None
<<<<<<< HEAD

    if request.method == "POST":
=======
    saran = None

    sample_arg = request.args.get("sample") or (request.form.get("sample") if request.method == "POST" else None)

    # Deteksi menggunakan data sampel
    if sample_arg:
        clean_name = secure_filename(sample_arg)
        if not clean_name.endswith((".jpg", ".jpeg", ".png", ".webp")):
            clean_name += ".jpg"
        filepath = os.path.join(SAMPLE_FOLDER, clean_name)

        if os.path.exists(filepath):
            if model is None:
                pesan = "Model AI belum tersedia. Pastikan file best.pt berada di folder proyek."
            else:
                try:
                    results = model.predict(source=filepath, imgsz=224, verbose=False)
                    result = results[0]

                    class_id = int(result.probs.top1)
                    conf_val = float(result.probs.top1conf) * 100
                    nama_kelas = result.names[class_id]

                    confidence = round(conf_val, 2)
                    if confidence < CONFIDENCE_THRESHOLD:
                        prediksi = "Sampah Tidak Terdeteksi / Ragu-ragu"
                        pesan = f"Model AI kurang yakin dengan objek sampel ini (Keyakinan: {confidence}%)."
                    else:
                        prediksi = TERJEMAHAN.get(nama_kelas.lower(), nama_kelas.title())
                        pesan = f"Hasil klasifikasi data sampel: {prediksi} (Keyakinan: {confidence}%)."

                    saran = SARAN.get(prediksi, "Periksa kategori sampah dan ikuti petunjuk pemilahan kampus.")
                    hasil = f"/static/samples/{clean_name}"
                except Exception as e:
                    pesan = f"Gagal menganalisis data sampel: {e}"
        else:
            pesan = f"File sampel '{clean_name}' tidak ditemukan."

    elif request.method == "POST":
>>>>>>> 5e47824 (Update model AI best.pt dan perbaikan backend)
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

<<<<<<< HEAD
                # Inferensi Model Klasifikasi
=======
>>>>>>> 5e47824 (Update model AI best.pt dan perbaikan backend)
                results = model.predict(source=filepath, imgsz=224, verbose=False)
                result = results[0]

                class_id = int(result.probs.top1)
                conf_val = float(result.probs.top1conf) * 100
                nama_kelas = result.names[class_id]

                confidence = round(conf_val, 2)
<<<<<<< HEAD
                
                # Cek Threshold Confidence
=======

>>>>>>> 5e47824 (Update model AI best.pt dan perbaikan backend)
                if confidence < CONFIDENCE_THRESHOLD:
                    prediksi = "Sampah Tidak Terdeteksi / Ragu-ragu"
                    pesan = f"Model AI kurang yakin dengan objek ini (Keyakinan: {confidence}%)."
                else:
                    prediksi = TERJEMAHAN.get(nama_kelas.lower(), nama_kelas.title())
                    pesan = f"Hasil klasifikasi: {prediksi}. Tingkat keyakinan model: {confidence}%."

<<<<<<< HEAD
                hasil = filename
=======
                saran = SARAN.get(prediksi, "Periksa kategori sampah dan ikuti petunjuk pemilahan kampus.")
                hasil = f"/uploads/{filename}"
>>>>>>> 5e47824 (Update model AI best.pt dan perbaikan backend)

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
<<<<<<< HEAD
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
=======
        saran=saran,
        samples=SAMPLE_DATA,
    )


# API Endpoint khusus untuk Modal Scanner AI (Mendukung Data Sampel, Base64, & File)
@app.route("/predict", methods=["POST"])
def predict_api():
    if model is None:
        return jsonify({"success": False, "error": "Model AI belum dimuat."}), 500

    filepath = None
    is_temp = False
    image_url = None

    try:
        # Case 1: Request JSON (Data Sampel atau Base64)
        if request.is_json:
            data = request.get_json() or {}
            sample_name = data.get("sample")
            image_data = data.get("image")

            if sample_name:
                clean_name = secure_filename(sample_name)
                if not clean_name.endswith((".jpg", ".jpeg", ".png", ".webp")):
                    clean_name += ".jpg"
                filepath = os.path.join(SAMPLE_FOLDER, clean_name)
                if not os.path.exists(filepath):
                    return jsonify({"success": False, "error": f"File sampel '{clean_name}' tidak ditemukan."}), 404
                image_url = f"/static/samples/{clean_name}"
            elif image_data:
                header, encoded = image_data.split(",", 1) if "," in image_data else ("", image_data)
                file_bytes = base64.b64decode(encoded)
                filename = f"{uuid.uuid4().hex}.jpg"
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                with open(filepath, "wb") as f:
                    f.write(file_bytes)
                is_temp = True
                image_url = f"/uploads/{filename}"
            else:
                return jsonify({"success": False, "error": "Data gambar atau sampel tidak ditemukan."}), 400
>>>>>>> 5e47824 (Update model AI best.pt dan perbaikan backend)

        # Case 2: Request Multipart Form-Data
        elif "gambar" in request.files or "file" in request.files:
            file = request.files.get("gambar") or request.files.get("file")
            if not file or file.filename == "":
<<<<<<< HEAD
                return jsonify({"error": "Tidak ada file yang dipilih."}), 400
            
=======
                return jsonify({"success": False, "error": "Tidak ada file yang dipilih."}), 400
>>>>>>> 5e47824 (Update model AI best.pt dan perbaikan backend)
            ekstensi = file.filename.rsplit(".", 1)[1].lower() if "." in file.filename else "jpg"
            filename = f"{uuid.uuid4().hex}.{ekstensi}"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
<<<<<<< HEAD
        else:
            return jsonify({"error": "Format request tidak dikenali."}), 400

        # Run Prediction
=======
            is_temp = True
            image_url = f"/uploads/{filename}"

        # Case 3: Form Data Sample
        elif request.form.get("sample"):
            clean_name = secure_filename(request.form.get("sample"))
            if not clean_name.endswith((".jpg", ".jpeg", ".png", ".webp")):
                clean_name += ".jpg"
            filepath = os.path.join(SAMPLE_FOLDER, clean_name)
            if not os.path.exists(filepath):
                return jsonify({"success": False, "error": f"File sampel '{clean_name}' tidak ditemukan."}), 404
            image_url = f"/static/samples/{clean_name}"

        else:
            return jsonify({"success": False, "error": "Format request tidak dikenali."}), 400

        # Inferensi Model
>>>>>>> 5e47824 (Update model AI best.pt dan perbaikan backend)
        results = model.predict(source=filepath, imgsz=224, verbose=False)
        result = results[0]

        class_id = int(result.probs.top1)
        conf_val = float(result.probs.top1conf) * 100
        nama_kelas = result.names[class_id]
<<<<<<< HEAD

        confidence = round(conf_val, 1)

        # Cek apakah akurasi memenuhi batas minimal 50%
        if confidence < CONFIDENCE_THRESHOLD:
            prediksi = "Tidak Terdeteksi"
        else:
            prediksi = TERJEMAHAN.get(nama_kelas.lower(), nama_kelas.title())

=======
        confidence = round(conf_val, 1)

        if confidence < CONFIDENCE_THRESHOLD:
            prediksi = "Sampah Tidak Terdeteksi / Ragu-ragu"
        else:
            prediksi = TERJEMAHAN.get(nama_kelas.lower(), nama_kelas.title())

        saran = SARAN.get(prediksi, "Periksa kategori sampah dan ikuti petunjuk fasilitas kampus.")

>>>>>>> 5e47824 (Update model AI best.pt dan perbaikan backend)
        return jsonify({
            "success": True,
            "class": prediksi,
            "label": prediksi,
            "confidence": confidence,
<<<<<<< HEAD
            "image_url": f"/uploads/{filename}"
=======
            "saran": saran,
            "image_url": image_url
>>>>>>> 5e47824 (Update model AI best.pt dan perbaikan backend)
        })

    except Exception as e:
        print(f"Error pada API /predict: {e}")
<<<<<<< HEAD
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({"error": "Gagal memproses gambar."}), 500
=======
        if is_temp and filepath and os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({"success": False, "error": "Gagal memproses gambar."}), 500
>>>>>>> 5e47824 (Update model AI best.pt dan perbaikan backend)


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
<<<<<<< HEAD
=======
            samples=SAMPLE_DATA,
>>>>>>> 5e47824 (Update model AI best.pt dan perbaikan backend)
        ),
        413,
    )


if __name__ == "__main__":
<<<<<<< HEAD
    app.run(debug=True, port=5000)
=======
    app.run(debug=True, port=5000)
>>>>>>> 5e47824 (Update model AI best.pt dan perbaikan backend)
