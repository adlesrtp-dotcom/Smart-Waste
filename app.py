import os
import uuid
import base64
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from ultralytics import YOLO
app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
SAMPLE_FOLDER = os.path.join(BASE_DIR, 'static', 'samples')
MODEL_PATH = os.path.join(BASE_DIR, 'best.pt')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SAMPLE_FOLDER, exist_ok=True)
TERJEMAHAN = {'cardboard': 'Kardus', 'glass': 'Kaca', 'metal': 'Logam', 'paper': 'Kertas', 'plastic': 'Plastik'}
SARAN = {'Kardus': 'Pisahkan kardus dari sampah basah dan lipat rapi sebelum dimasukkan ke tempat daur ulang.', 'Kertas': 'Kumpulkan kertas secara terpisah dan pastikan tetap kering untuk memudahkan daur ulang.', 'Plastik': 'Kosongkan sisa isi dan bilas kemasan, lalu kumpulkan di tempat sampah anorganik/plastik.', 'Logam': 'Pisahkan benda logam atau kaleng, pipihkan bila memungkinkan untuk efisiensi ruang daur ulang.', 'Kaca': 'Pisahkan kaca dengan hati-hati dalam wadah khusus, hindari kontak langsung dengan pecahan tajam.'}
SAMPLE_DATA = [{'id': 'kardus', 'file': 'kardus.jpg', 'label': 'Kardus', 'desc': 'Contoh kemasan karton/kardus'}, {'id': 'kaca', 'file': 'kaca.jpg', 'label': 'Kaca', 'desc': 'Contoh botol/wadah kaca'}, {'id': 'logam', 'file': 'logam.jpg', 'label': 'Logam', 'desc': 'Contoh kaleng minuman logam'}, {'id': 'kertas', 'file': 'kertas.jpg', 'label': 'Kertas', 'desc': 'Contoh lembaran kertas bekas'}, {'id': 'plastik', 'file': 'plastik.jpg', 'file_name': 'plastik.jpg', 'label': 'Plastik', 'desc': 'Contoh botol kemasan plastik'}]
for s in SAMPLE_DATA:
    if 'file_name' not in s:
        s['file_name'] = s['file']
CONFIDENCE_THRESHOLD = 50.0
model = None
if os.path.exists(MODEL_PATH):
    try:
        model = YOLO(MODEL_PATH)
        print('Model AI best.pt berhasil dimuat.')
    except Exception as e:
        print(f'Gagal memuat model: {e}')
else:
    print(f'Warning: File {MODEL_PATH} tidak ditemukan.')
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
@app.route('/')
def index():
    return render_template('index.html', samples=SAMPLE_DATA)
@app.route('/deteksi', methods=['GET', 'POST'])
def deteksi():
    pesan = None
    hasil = None
    prediksi = None
    confidence = None
    saran = None
    sample_arg = request.args.get('sample') or (request.form.get('sample') if request.method == 'POST' else None)
    if sample_arg:
        clean_name = secure_filename(sample_arg)
        if not clean_name.endswith(('.jpg', '.jpeg', '.png', '.webp')):
                clean_name += '.jpg'
        filepath = os.path.join(SAMPLE_FOLDER, clean_name)
        if os.path.exists(filepath):
            if model is None:
                pesan = 'Model AI belum tersedia.'
            else:
                try:
                    results = model.predict(source=filepath, imgsz=224, verbose=False)
                    result = results[0]
                    class_id = int(result.probs.top1)
                    conf_val = float(result.probs.top1conf) * 100
                    nama_kelas = result.names[class_id]
                    confidence = round(conf_val, 2)
                    if confidence < CONFIDENCE_THRESHOLD:
                        prediksi = 'Sampah Tidak Terdeteksi / Ragu-ragu'
                        pesan = f'Model AI kurang yakin (Keyakinan: {confidence}%).'
                    else:
                        prediksi = TERJEMAHAN.get(nama_kelas.lower(), nama_kelas.title())
                        pesan = f'Hasil klasifikasi: {prediksi} (Keyakinan: {confidence}%).'
                    saran = SARAN.get(prediksi, 'Periksa kategori sampah.')
                    hasil = f'/static/samples/{clean_name}'
                except Exception as e:
                    pesan = f'Gagal menganalisis: {e}'
        else:
            pesan = f'File sampel {clean_name} tidak ditemukan.'
    elif request.method == 'POST':
        file = request.files.get('gambar') or request.files.get('file')
        if not file or file.filename == '':
            pesan = 'Silakan pilih gambar.'
        elif not allowed_file(file.filename):
            pesan = 'Format gambar salah.'
        elif model is None:
            pesan = 'Model AI belum tersedia.'
        else:
            ekstensi = file.filename.rsplit('.', 1)[1].lower()
            filename = f'{uuid.uuid4().hex}.{ekstensi}'
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            try:
                file.save(filepath)
                results = model.predict(source=filepath, imgsz=224, verbose=False)
                result = results[0]
                class_id = int(result.probs.top1)
                conf_val = float(result.probs.top1conf) * 100
                nama_kelas = result.names[class_id]
                confidence = round(conf_val, 2)
                if confidence < CONFIDENCE_THRESHOLD:
                    prediksi = 'Sampah Tidak Terdeteksi / Ragu-ragu'
                    pesan = f'Model AI kurang yakin (Keyakinan: {confidence}%).'
                else:
                    prediksi = TERJEMAHAN.get(nama_kelas.lower(), nama_kelas.title())
                    pesan = f'Hasil klasifikasi: {prediksi}. Keyakinan: {confidence}%.'
                saran = SARAN.get(prediksi, 'Periksa kategori sampah.')
                hasil = f'/uploads/{filename}'
            except Exception as e:
                pesan = 'Gagal memproses gambar.'
                if os.path.exists(filepath): os.remove(filepath)
    return render_template('deteksi.html', pesan=pesan, hasil=hasil, prediksi=prediksi, confidence=confidence, saran=saran, samples=SAMPLE_DATA)
@app.route('/predict', methods=['POST'])
def predict_api():
    if model is None: return jsonify({'success': False, 'error': 'Model AI belum dimuat.'}), 500
    filepath = None
    is_temp = False
    image_url = None
    try:
        if request.is_json:
            data = request.get_json() or {}
            sample_name = data.get('sample')
            image_data = data.get('image')
            if sample_name:
                clean_name = secure_filename(sample_name)
                if not clean_name.endswith(('.jpg', '.jpeg', '.png', '.webp')):
                        clean_name += '.jpg'
                filepath = os.path.join(SAMPLE_FOLDER, clean_name)
                if not os.path.exists(filepath): return jsonify({'success': False, 'error': 'File tidak ditemukan.'}), 404
                image_url = f'/static/samples/{clean_name}'
            elif image_data:
                header, encoded = image_data.split(',', 1) if ',' in image_data else ('', image_data)
                file_bytes = base64.b64decode(encoded)
                filename = f'{uuid.uuid4().hex}.jpg'
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                with open(filepath, 'wb') as f: f.write(file_bytes)
                is_temp = True
                image_url = f'/uploads/{filename}'
            else: return jsonify({'success': False, 'error': 'Gambar tidak ditemukan.'}), 400
        elif 'gambar' in request.files or 'file' in request.files:
            file = request.files.get('gambar') or request.files.get('file')
            if not file or file.filename == '': return jsonify({'success': False, 'error': 'File tidak dipilih.'}), 400
            ekstensi = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'jpg'
            filename = f'{uuid.uuid4().hex}.{ekstensi}'
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            is_temp = True
            image_url = f'/uploads/{filename}'
        elif request.form.get('sample'):
            clean_name = secure_filename(request.form.get('sample'))
            if not clean_name.endswith(('.jpg', '.jpeg', '.png', '.webp')):
                clean_name += '.jpg'
            filepath = os.path.join(SAMPLE_FOLDER, clean_name)
            if not os.path.exists(filepath): return jsonify({'success': False, 'error': 'File sampel tidak ada.'}), 404
            image_url = f'/static/samples/{clean_name}'
        else: return jsonify({'success': False, 'error': 'Format tidak dikenal.'}), 400
        results = model.predict(source=filepath, imgsz=224, verbose=False)
        result = results[0]
        class_id = int(result.probs.top1)
        conf_val = float(result.probs.top1conf) * 100
        nama_kelas = result.names[class_id]
        confidence = round(conf_val, 1)
        prediksi = 'Sampah Tidak Terdeteksi / Ragu-ragu' if confidence < CONFIDENCE_THRESHOLD else TERJEMAHAN.get(nama_kelas.lower(), nama_kelas.title())
        saran = SARAN.get(prediksi, 'Periksa kategori sampah.')
        return jsonify({'success': True, 'class': prediksi, 'label': prediksi, 'confidence': confidence, 'saran': saran, 'image_url': image_url})
    except Exception as e:
        if is_temp and filepath and os.path.exists(filepath): os.remove(filepath)
        return jsonify({'success': False, 'error': 'Gagal memproses gambar.'}), 500
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
if __name__ == '__main__':
    app.run(debug=True, port=5000)

