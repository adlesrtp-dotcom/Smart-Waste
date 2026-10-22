
import os
import uuid
from flask import (
    Flask, render_template, request,
    send_from_directory
)
from werkzeug.utils import secure_filename
from ultralytics import YOLO

app = Flask(__name__)

# Konfigurasi website
UPLOAD_FOLDER = os.path.join(app.root_path, "uploads")
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Lokasi model AI hasil training
MODEL_PATHS = [
    os.path.join(app.root_path, "best.pt"),
    os.path.join(
        app.root_path,
        "runs", "classify", "runs", "smartwaste",
        "klasifikasi_sampah", "weights", "best.pt"
    ),
]

MODEL_PATH = next(
    (path for path in MODEL_PATHS if os.path.isfile(path)),
    None
)

# Muat model satu kali ketika aplikasi dijalankan
model = None

if MODEL_PATH:
    try:
        model = YOLO(MODEL_PATH)
        print(f"Model SmartWaste berhasil dimuat: {MODEL_PATH}")
        print(f"Kategori model: {model.names}")
    except Exception as e:
        print(f"Gagal memuat model AI: {e}")
else:
    print("PERINGATAN: File best.pt tidak ditemukan.")


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


# Halaman utama
@app.route("/")
def index():
    return render_template("index.html")


# Halaman deteksi sampah
@app.route("/deteksi", methods=["GET", "POST"])
def deteksi():
    pesan = None
    hasil = None
    prediksi = None
    confidence = None

    if request.method == "POST":
        file = request.files.get("gambar")

        if not file or file.filename == "":
            pesan = "Silakan pilih gambar sampah terlebih dahulu."

        elif not allowed_file(file.filename):
            pesan = "Format gambar harus JPG, JPEG, PNG, atau WEBP."

        elif model is None:
            pesan = (
                "Model AI belum tersedia. "
                "Pastikan file best.pt berada di folder proyek."
            )

        else:
            # Buat nama file unik untuk menghindari nama yang sama
            ekstensi = file.filename.rsplit(".", 1)[1].lower()
            filename = f"{uuid.uuid4().hex}.{ekstensi}"
            filepath = os.path.join(UPLOAD_FOLDER, filename)

            try:
                file.save(filepath)

                # Jalankan klasifikasi menggunakan YOLOv8
                results = model.predict(
                source=filepath,
                imgsz=224,
                augment=True,
                verbose=False
)
                result = results[0]
                class_id = int(result.probs.top1)
                confidence = float(result.probs.top1conf) * 100

                # Nama kelas dari model
                nama_kelas = result.names[class_id]

                # Terjemahkan kategori ke Bahasa Indonesia
                terjemahan = {
                    "cardboard": "Kardus",
                    "glass": "Kaca",
                    "metal": "Logam",
                    "paper": "Kertas",
                    "plastic": "Plastik",
                }

                prediksi = terjemahan.get(
                    nama_kelas.lower(), nama_kelas.title()
                )

                confidence = round(confidence, 2)
                hasil = filename

                pesan = (
                    f"Hasil klasifikasi: {prediksi}. "
                    f"Tingkat keyakinan model: {confidence}%."
                )

            except Exception as e:
                print(f"Terjadi kesalahan saat deteksi: {e}")
                pesan = (
                    "Maaf, gambar gagal diproses. "
                    "Silakan coba gambar lain."
                )

                # Hapus file jika proses gagal
                if os.path.exists(filepath):
                    os.remove(filepath)

    return render_template(
        "deteksi.html",
        pesan=pesan,
        hasil=hasil,
        prediksi=prediksi,
        confidence=confidence
    )


# Menampilkan gambar yang sudah diunggah
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


# Menangani file yang melebihi batas ukuran
@app.errorhandler(413)
def file_too_large(error):
    return render_template(
        "deteksi.html",
        pesan="Ukuran gambar maksimal 5 MB.",
        hasil=None,
        prediksi=None,
        confidence=None
    ), 413


if __name__ == "__main__":
    app.run(debug=True)
